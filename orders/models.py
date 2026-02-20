from django.db import models

from django.contrib.auth import get_user_model

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
    second_date = models.DateTimeField(null=True, blank=True)

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

    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    canceled = models.BooleanField(default=False)
    canceled_by_admin = models.BooleanField(default=False)

    additional_descriptions = models.TextField(null=True, blank=True)

    def calculate_tipax_price(self):
        weight = self.get_total_weight()

        if self.address.city_code is None:
            return -1

        if self.store.orgin_city_id is None:
            return -1

        price_qs = DeliveryPrices.objects.filter(
            is_tipax=True,
            origin_city_id=self.store.orgin_city_id,
            destination_city_id=self.address.city_code,
            date__range=[now() - timedelta(days=3), now()],
            weight=weight,
        ).order_by("-date")

        if price_qs.exists():
            return price_qs.first().price

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
            price_qs = DeliveryPrices.objects.filter(
                is_tipax=False,
                origin_city_id=self.store.orgin_city_id,
                destination_city_id=self.address.city_code,
                date__range=[now() - timedelta(days=3), now()],
                weight=self.get_total_weight(),
                volume=self.calculate_total_volume(),
            ).order_by("-date")
            if price_qs.exists():
                return price_qs.first().price

            price = calculate_post_price_postex(self)
            price = int(price)

            if price :
                DeliveryPrices.objects.create(
                    is_tipax=False,
                    origin_city_id=self.store.orgin_city_id,
                    destination_city_id=self.address.city_code,
                    date=now(),
                    price=price,
                    weight=self.get_total_weight(),
                    volume=self.calculate_total_volume(),
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
            details = self.details.all()
            total_price = 0

            for item in details:
                total_price += item.get_item_price()

            self.total_price = total_price
            self.save()
            return total_price
        else:
            return self.total_price

    def calculate_total_price_with_out_discount(self):
        """
        calculate price of products without there discounts
        """

        total_price = 0

        for item in self.details.all():
            total_price += item.get_item_price_without_discount()

        return total_price

    def get_total_weight(self):
        """
        calculate total weight of products
        """
        if not self.is_paid and not self.canceled:
            details = self.details.all()
            total_weight = 0

            for item in details:
                total_weight += item.product.weight * item.count

            self.total_weight = total_weight
            self.save()
            return total_weight
        else:
            return self.total_weight

    def get_total_length(self):
        """
        calculate total length of products
        """
        if not self.is_paid and not self.canceled:
            details = self.details.all()
            total_length = 0

            for item in details:
                total_length += item.product.length * item.count

            self.total_length = total_length
            self.save()
            return total_length
        else:
            return self.total_length

    def get_total_width(self):
        """
        calculate total width of products
        """
        if not self.is_paid and not self.canceled:
            details = self.details.all()
            total_width = 0

            for item in details:
                total_width += item.product.width * item.count

            self.total_width = total_width
            self.save()
            return total_width
        else:
            return self.total_width

    def get_total_height(self):
        """
        calculate total height of products
        """
        if not self.is_paid and not self.canceled:
            details = self.details.all()
            total_height = 0

            for item in details:
                total_height += item.product.height * item.count

            self.total_height = total_height
            self.save()
            return total_height
        else:
            return self.total_height

    def calculate_total_volume(self):
        """
        for calculate total volume of products
        """
        total_volume = 0
        for item in self.details.all():
            item_volume = item.product.height * item.product.width * item.product.length
            total_volume += item_volume * item.count
        return total_volume

    def get_items_discount_amount(self):
        """
        for calculate discount amount of products
        """
        total_amount = 0
        for item in self.details.all():
            total_amount += item.get_item_discount()
        return total_amount

    def get_total_discount_amount(self):
        """
        for calculate total discount amount
        """
        result_amount = self.get_items_discount_amount()
        if self.use_discount_code and self.discount:
            result_amount += self.discount_code_price

        return result_amount

    def get_total_products_with_no_discount_price(self):
        return self.calculate_total_price_with_out_discount()

    def check_count_of_products(self):
        return all(
            item.product.count >= 0
            for item in self.details.select_related("product")
        )

    def mines_order_detail_count_from_products_count(self):
        for item in self.details.all():
            item.product.count = item.product.count - item.count
            item.product.save()

    def get_tax_and_other_prices(self):
        return int(self.get_payment_price() - self.delivery_price - self.calculate_total_price())


    def get_payment_price(self):
        """

        for calculate the payment price

        """
        if not self.is_paid and not self.canceled   :
            site = SiteSetting.objects.first()

            total_amount_of_items = self.get_total_products_with_no_discount_price()

            total_payment_price = (
                    total_amount_of_items + self.delivery_price - self.get_total_discount_amount()
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

            self.total_payment_price = total_payment_price
            self.save()
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
    added_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def get_user_of_the_order(self):
        return self.order.user

    def get_price(self):

        """
        for get the price of one product with discounts
        """

        if not self.order.is_paid and not self.order.canceled:
            self.product_price = self.product.get_product_price(user=self.get_user_of_the_order())
            self.save()
            return self.product_price
        else:
            return self.product_price

    def get_price_without_discount(self):
        """
        for get the price of one product without discounts
        """
        if not self.order.is_paid and not self.order.canceled:
            self.product_price_without_discount = self.product.price
            self.save()
            return self.product_price_without_discount
        else:
            return self.product_price_without_discount

    def decrease_product_stock_by_order(self):

        if not self.order.is_paid and not self.order.canceled:
            if self.product.count >= self.count:
                self.product.count -= self.count
                self.product.save()
                return True
        return False

    def increase_product_stock_by_order(self):
        if not self.order.is_paid and not self.order.canceled:
            self.product.count += self.count
            self.product.save()
            return True

        return False

    def get_item_price(self):
        """
        for clac the price of the product and the order count with the product discounts
        """
        if not self.order.is_paid and not self.order.canceled:
            product = self.get_price()
            price = product * self.count
            self.price = price
            self.save()
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

    is_active = models.BooleanField(default=True)

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
    is_returned_by_admin = models.BooleanField(default=False)
    open_date = models.DateTimeField(auto_now_add=True)
    paid_by_admin_date = models.DateTimeField(null=True, blank=True)

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
    accept_by_store = models.BooleanField(default=False)
    accept_by_admin = models.BooleanField(default=False)
    send_request_to_return_this_order_by_admin = models.BooleanField(default=False)


class SpecificsOrders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField(default=0)
    name = models.CharField(max_length=500)
    is_paid = models.BooleanField(default=False)
    Authority = models.CharField(max_length=120, null=True, blank=True, unique=True)
    cart = models.CharField(max_length=120, null=True, blank=True)
    cart_hash = models.CharField(max_length=120, null=True, blank=True)
    payment_id = models.PositiveBigIntegerField(default=0)
    ZarinPal_fee = models.PositiveBigIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    second_date = models.DateTimeField(null=True, blank=True)
    additional_descriptions = models.TextField(null=True, blank=True)
