from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from easy_thumbnails.fields import ThumbnailerImageField

from dashboard.models import UserAddress
from stores.models import Store
from product.models import Product
from utils.tipax_price_calc import calculate_price as calculate_price_tipax
from utils.post_price_calc import calculate_post_price_postex
from sitesetting.models import SiteSetting
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta

User = get_user_model()


# Create your models here.


def pdf_path_upload_to(instance, filename):
    return f"files/official_invoice/pdf/{get_random_string(100)}.pdf"


class DeliveryPrices(models.Model):
    is_tipax = models.BooleanField(default=True)
    price = models.PositiveBigIntegerField()
    origin_city_id = models.PositiveIntegerField()
    destination_city_id = models.PositiveIntegerField()
    date = models.DateField()
    weight = models.PositiveIntegerField(default=0)
    volume = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.origin_city_id}-{self.destination_city_id}-{self.price}-{"tipax" if self.is_tipax else "post"} '


class TypeOfPayment(models.TextChoices):
    ZARIN_PALE = 'ZAR', 'زرین پال' 
    ZIBAL = 'ZIP' , 'زیپال'

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(
        UserAddress, null=True, on_delete=models.CASCADE, related_name="orders"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    type_of_payment = models.CharField(max_length=255, choices=TypeOfPayment, null=True, blank=True, verbose_name='درگاه پرداخت')

    vip_post = models.BooleanField(default=False)
    tipax_post_delivery = models.BooleanField(default=False)
    in_city_delivery = models.BooleanField(default=False)
    physical_delivery = models.BooleanField(default=False)
    freight_delivery = models.BooleanField(default=False)

    vip_post_price = models.PositiveBigIntegerField(default=0)
    tipax_post_price = models.PositiveBigIntegerField(default=0)

    delivery_price = models.PositiveBigIntegerField(default=0)
    sending = models.BooleanField(default=False)
    delivered_to_user = models.BooleanField(default=False)
    sending_id = models.CharField(max_length=500, null=True, blank=True)

    Authority = models.CharField(max_length=120, null=True, blank=True, unique=True)
    cart = models.CharField(max_length=120, null=True, blank=True)
    cart_hash = models.CharField(max_length=120, null=True, blank=True)
    payment_id = models.PositiveBigIntegerField(default=0)
    ZarinPal_fee = models.PositiveBigIntegerField(default=0)

    date = models.DateTimeField(auto_now_add=True)
    second_date = models.DateTimeField(null=True, blank=True, db_index=True)

    # discount code
    use_discount_code = models.BooleanField(default=False)
    discount_code_price = models.PositiveBigIntegerField(default=0)
    discount = models.OneToOneField(
        "Discount",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="discount",
    )

    total_price = models.PositiveBigIntegerField(default=0)
    total_payment_price = models.PositiveBigIntegerField(default=0)
    total_weight = models.PositiveBigIntegerField(default=0)
    total_length = models.PositiveBigIntegerField(default=0)
    total_width = models.PositiveBigIntegerField(default=0)
    total_height = models.PositiveBigIntegerField(default=0)

    official_invoice = models.BooleanField(default=False)
    official_invoice_conformed_given_to_user = models.BooleanField(default=False)
    official_invoice_pdf = models.FileField(
        upload_to=pdf_path_upload_to, null=True, blank=True
    )

    is_paid = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    canceled = models.BooleanField(default=False, db_index=True)
    canceled_by_admin = models.BooleanField(default=False)

    additional_descriptions = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_paid", "is_active", "canceled"]),
            models.Index(fields=["store", "is_paid", "is_active", "canceled"]),
            models.Index(fields=["is_paid", "canceled", "-second_date"]),
        ]

    def _get_details_with_products(self):
        prefetched = getattr(self, "_prefetched_objects_cache", None)
        if prefetched and "details" in prefetched:
            return list(prefetched["details"])
        return list(self.details.select_related("product", "order"))

    def calculate_tipax_price(self):
        weight = self.get_total_weight()

        if self.address.city_code is None:
            return -1

        if self.store.orgin_city_id is None:
            return -1

        cached_price = DeliveryPrices.objects.filter(
            is_tipax=True,
            origin_city_id=self.store.orgin_city_id,
            destination_city_id=self.address.city_code,
            date__range=[now() - timedelta(days=3), now()],
            weight=weight,
        ).order_by("-date").values_list("price", flat=True).first()

        if cached_price is not None:
            return cached_price

        calculated_price = calculate_price_tipax(self)
        if calculated_price is not None:
            DeliveryPrices.objects.create(
                is_tipax=True,
                origin_city_id=self.store.orgin_city_id,
                destination_city_id=self.address.city_code,
                date=now(),
                price=calculated_price,
                weight=weight,
            )
            return calculated_price

        return -1

    def calculate_post_price(self):
        if self.address.city_code is None:
            return -1
        if self.store.orgin_city_id is None:
            return -1

        try:
            total_weight = self.get_total_weight()
            total_volume = self.calculate_total_volume()
            cached_price = DeliveryPrices.objects.filter(
                is_tipax=False,
                origin_city_id=self.store.orgin_city_id,
                destination_city_id=self.address.city_code,
                date__range=[now() - timedelta(days=3), now()],
                weight=total_weight,
                volume=total_volume,
            ).order_by("-date").values_list("price", flat=True).first()
            if cached_price is not None:
                return cached_price

            price = calculate_post_price_postex(self)
            price = int(price)

            if price :
                DeliveryPrices.objects.create(
                    is_tipax=False,
                    origin_city_id=self.store.orgin_city_id,
                    destination_city_id=self.address.city_code,
                    date=now(),
                    price=price,
                    weight=total_weight,
                    volume=total_volume,
                )
            return price

        except Exception as e:
            print('calc post price error:', e)
            return -1


    def calculate_total_price(self):
        """
        calculate price of products with there discounts
        """
        if not self.is_paid and not self.canceled:
            details = self._get_details_with_products()
            total_price = 0
            dirty_details = []

            for item in details:
                unit_price = item.product.get_product_price()
                item_price = unit_price * item.count
                if item.product_price != unit_price or item.price != item_price:
                    item.product_price = unit_price
                    item.price = item_price
                    dirty_details.append(item)
                total_price += item_price

            if dirty_details:
                OrderDetail.objects.bulk_update(dirty_details, ["product_price", "price"])

            if self.total_price != total_price:
                self.total_price = total_price
                self.save(update_fields=["total_price"])
            return total_price
        else:
            return self.total_price

    def calculate_total_price_with_out_discount(self):
        """
        calculate price of products without there discounts
        """
        details = self._get_details_with_products()
        total_price = 0
        dirty_details = []

        if not self.is_paid and not self.canceled:
            for item in details:
                unit_price = item.product.price
                if item.product_price_without_discount != unit_price:
                    item.product_price_without_discount = unit_price
                    dirty_details.append(item)
                total_price += unit_price * item.count
            if dirty_details:
                OrderDetail.objects.bulk_update(dirty_details, ["product_price_without_discount"])
        else:
            for item in details:
                total_price += item.product_price_without_discount * item.count

        return total_price

    def _aggregate_detail_dimension(self, field_name):
        prefetched = getattr(self, "_prefetched_objects_cache", None)
        if prefetched and "details" in prefetched:
            return sum(getattr(item.product, field_name) * item.count for item in prefetched["details"])
        return self.details.aggregate(
            total=Coalesce(Sum(F(f"product__{field_name}") * F("count")), 0)
        )["total"]

    def get_total_weight(self):
        """
        calculate total weight of products
        """
        if not self.is_paid and not self.canceled:
            total_weight = self._aggregate_detail_dimension("weight")
            if self.total_weight != total_weight:
                self.total_weight = total_weight
                self.save(update_fields=["total_weight"])
            return total_weight
        else:
            return self.total_weight

    def get_total_length(self):
        """
        calculate total length of products
        """
        if not self.is_paid and not self.canceled:
            total_length = self._aggregate_detail_dimension("length")
            if self.total_length != total_length:
                self.total_length = total_length
                self.save(update_fields=["total_length"])
            return total_length
        else:
            return self.total_length

    def get_total_width(self):
        """
        calculate total width of products
        """
        if not self.is_paid and not self.canceled:
            total_width = self._aggregate_detail_dimension("width")
            if self.total_width != total_width:
                self.total_width = total_width
                self.save(update_fields=["total_width"])
            return total_width
        else:
            return self.total_width

    def get_total_height(self):
        """
        calculate total height of products
        """
        if not self.is_paid and not self.canceled:
            total_height = self._aggregate_detail_dimension("height")
            if self.total_height != total_height:
                self.total_height = total_height
                self.save(update_fields=["total_height"])
            return total_height
        else:
            return self.total_height

    def calculate_total_volume(self):
        """
        for calculate total volume of products
        """
        prefetched = getattr(self, "_prefetched_objects_cache", None)
        if prefetched and "details" in prefetched:
            return sum(
                item.product.height * item.product.width * item.product.length * item.count
                for item in prefetched["details"]
            )
        return self.details.aggregate(
            total=Coalesce(
                Sum(F("product__height") * F("product__width") * F("product__length") * F("count")),
                0,
            )
        )["total"]

    def get_items_discount_amount(self):
        """
        for calculate discount amount of products
        """
        details = self._get_details_with_products()
        total_amount = 0
        dirty_details = []

        if not self.is_paid and not self.canceled:
            for item in details:
                unit_no_discount = item.product.price
                unit_price = item.product.get_product_price()
                item_price = unit_price * item.count
                if (
                    item.product_price_without_discount != unit_no_discount
                    or item.product_price != unit_price
                    or item.price != item_price
                ):
                    item.product_price_without_discount = unit_no_discount
                    item.product_price = unit_price
                    item.price = item_price
                    dirty_details.append(item)
                total_amount += (unit_no_discount * item.count) - item_price
            if dirty_details:
                OrderDetail.objects.bulk_update(
                    dirty_details,
                    ["product_price_without_discount", "product_price", "price"],
                )
        else:
            for item in details:
                total_amount += (item.product_price_without_discount * item.count) - item.price

        return total_amount

    def get_total_discount_amount(self):
        """
        for calculate total discount amount
        """
        result_amount = self.get_items_discount_amount()
        if self.use_discount_code and self.discount_id:
            result_amount += self.discount_code_price

        return result_amount

    def get_total_products_with_no_discount_price(self):
        return self.calculate_total_price_with_out_discount()

    def check_count_of_products(self):
        prefetched = getattr(self, "_prefetched_objects_cache", None)
        if prefetched and "details" in prefetched:
            return all(item.product.count >= 0 for item in prefetched["details"])
        return not self.details.filter(product__count__lt=0).exists()

    def mines_order_detail_count_from_products_count(self):
        products_to_update = []
        for item in self.details.select_related("product"):
            item.product.count = item.product.count - item.count
            products_to_update.append(item.product)
        if products_to_update:
            Product.objects.bulk_update(products_to_update, ["count"])

    def get_tax_and_other_prices(self):
        return int(self.get_payment_price() - self.delivery_price - self.calculate_total_price())


    def get_payment_price(self):
        """

        for calculate the payment price

        """
        if not self.is_paid and not self.canceled   :
            site = SiteSetting.get_cached()

            details = self._get_details_with_products()
            total_amount_of_items = 0
            items_discount_amount = 0
            dirty_details = []

            for item in details:
                unit_no_discount = item.product.price
                unit_price = item.product.get_product_price()
                item_price = unit_price * item.count
                item_no_discount = unit_no_discount * item.count

                if (
                    item.product_price_without_discount != unit_no_discount
                    or item.product_price != unit_price
                    or item.price != item_price
                ):
                    item.product_price_without_discount = unit_no_discount
                    item.product_price = unit_price
                    item.price = item_price
                    dirty_details.append(item)

                total_amount_of_items += item_no_discount
                items_discount_amount += item_no_discount - item_price

            if dirty_details:
                OrderDetail.objects.bulk_update(
                    dirty_details,
                    ["product_price_without_discount", "product_price", "price"],
                )

            total_discount_amount = items_discount_amount
            if self.use_discount_code and self.discount_id:
                total_discount_amount += self.discount_code_price

            total_payment_price = (
                    total_amount_of_items + self.delivery_price - total_discount_amount
            )

            # store

            if (    self.official_invoice and
                    self.store.have_official_invoice and
                    site.active_receive_official_invoice ):
                
                total_payment_price += total_payment_price * (
                        self.store.official_invoice_price / 100
                )

            if self.store.additional_price:
                total_payment_price += self.store.additional_price

            if self.store.additional_tax:
                total_payment_price += total_payment_price * (
                        self.store.additional_tax / 100
                )

            # site
            total_payment_price += total_payment_price * (site.tax / 100)

            if self.total_payment_price != total_payment_price:
                self.total_payment_price = total_payment_price
                self.save(update_fields=["total_payment_price"])
            return total_payment_price
        else:

            return self.total_payment_price

    def __str__(self):
        return f"{self.user.PhoneNumber} - {self.store.name} - {self.id}"




class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="details")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="orders"
    )
    product_price = models.PositiveBigIntegerField(default=0)
    product_price_without_discount = models.PositiveBigIntegerField(default=0)

    date = models.DateTimeField(auto_now_add=True)
    price = models.PositiveBigIntegerField(default=0)
    count = models.PositiveBigIntegerField(default=1)
    added_date = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def get_user_of_the_order(self):
        return self.order.user

    def get_price(self):

        """
        for get the price of one product with discounts
        """

        if not self.order.is_paid and not self.order.canceled:
            new_price = self.product.get_product_price()
            if self.product_price != new_price:
                self.product_price = new_price
                self.save(update_fields=["product_price"])
            return self.product_price
        else:
            return self.product_price

    def get_price_without_discount(self):
        """
        for get the price of one product without discounts
        """
        if not self.order.is_paid and not self.order.canceled:
            new_price = self.product.price
            if self.product_price_without_discount != new_price:
                self.product_price_without_discount = new_price
                self.save(update_fields=["product_price_without_discount"])
            return self.product_price_without_discount
        else:
            return self.product_price_without_discount

    def decrease_product_stock_by_order(self):

        if not self.order.is_paid and not self.order.canceled:
            if self.product.count >= self.count:
                self.product.count -= self.count
                self.product.save(update_fields=["count"])
                return True
        return False

    def increase_product_stock_by_order(self):
        if not self.order.is_paid and not self.order.canceled:
            self.product.count += self.count
            self.product.save(update_fields=["count"])
            return True

        return False

    def get_item_price(self):
        """
        for clac the price of the product and the order count with the product discounts
        """
        if not self.order.is_paid and not self.order.canceled:
            unit_price = self.product.get_product_price()
            price = unit_price * self.count
            update_fields = []
            if self.product_price != unit_price:
                self.product_price = unit_price
                update_fields.append("product_price")
            if self.price != price:
                self.price = price
                update_fields.append("price")
            if update_fields:
                self.save(update_fields=update_fields)
            return price
        else:
            return self.price

    def get_item_price_without_discount(self):
        """

        for clac the price of the product and the order count without the product discounts

        """

        return self.get_price_without_discount() * self.count

    def get_item_discount(self):

        """for get the amount of discount"""

        return self.get_item_price_without_discount() - self.get_item_price()

    def __str__(self):
        return f"{self.order.id} - {self.id}"


class Discount(models.Model):
    user = models.ManyToManyField(User, related_name="discounts", blank=True)
    product = models.ManyToManyField(Product, related_name="discounts", blank=True)
    store = models.ManyToManyField(Store, blank=True, related_name="discounts")
    order = models.ManyToManyField(Order, related_name="discounts", blank=True)
    min_price = models.PositiveBigIntegerField(default=0)
    end_date_discount = models.DateTimeField(null=True, blank=True)
    count = models.PositiveBigIntegerField(default=0)
    percentage_discount = models.BooleanField(default=False)
    percent = models.PositiveBigIntegerField(default=0)
    price = models.PositiveBigIntegerField(default=0)
    name = models.CharField(
        max_length=100, null=True, blank=True, unique=True, db_index=True
    )
    count_of_use_per_user = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.name} - {self.id}"



class StoreSoldOrders(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="store_sold_orders", null=True, blank=True
    )
    specifics_order = models.OneToOneField(
        'SpecificsOrders', on_delete=models.CASCADE, related_name="store_sold_orders", null=True, blank=True
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_sold_orders"
    )
    price = models.PositiveBigIntegerField(default=0)
    is_returned_by_admin = models.BooleanField(default=False, db_index=True)
    open_date = models.DateTimeField(auto_now_add=True, db_index=True)
    paid_by_admin_date = models.DateTimeField(null=True, blank=True)
    ids_paid_together = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    file = models.FileField(null=True, blank=True, upload_to="store_sold_orders/")

    def __str__(self):
        return f"{self.price} <-> {self.store.name} <-> {self.is_returned_by_admin}"


class ReturnsOrders(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="returns_orders")
    user = models.ForeignKey(User, related_name="returns_orders", on_delete=models.CASCADE)
    card_number = models.CharField(max_length=500)
    decryption = models.TextField(null=True, blank=True)
    cart_name = models.TextField(null=True, blank=True)
    date_open_request = models.DateTimeField(auto_now_add=True)
    date_close_request = models.DateTimeField(null=True, blank=True)
    accept_by_store = models.BooleanField(default=False, db_index=True)
    accept_by_admin = models.BooleanField(default=False, db_index=True)
    send_request_to_return_this_order_by_admin = models.BooleanField(default=False)


class SpecificsOrders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField(default=0)
    name = models.CharField(max_length=500)
    is_paid = models.BooleanField(default=False, db_index=True)
    Authority = models.CharField(max_length=120, null=True, blank=True, unique=True)
    cart = models.CharField(max_length=120, null=True, blank=True)
    cart_hash = models.CharField(max_length=120, null=True, blank=True)
    payment_id = models.PositiveBigIntegerField(default=0)
    ZarinPal_fee = models.PositiveBigIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    second_date = models.DateTimeField(null=True, blank=True)
    additional_descriptions = models.TextField(null=True, blank=True)
