from django.db import models

from django.contrib.auth import get_user_model

from dashboard.models import UserAddress

from stores.models import Store
from product.models import Product

from utils.tipax_price_calc import calculate_price as calculate_price_tipax
from utils.post_price_calc import calculate_price as calculate_price_post

from sitesetting.models import SiteSetting
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta

User = get_user_model()


# Create your models here.

def pdf_path_upload_to(instance, filename):
    return f'files/official_invoice/pdf/{get_random_string(100)}.pdf'


class DeliveryPrices(models.Model):
    is_tipax = models.BooleanField(default=True)
    price = models.PositiveBigIntegerField()
    origin_city_id = models.PositiveIntegerField()
    destination_city_id = models.PositiveIntegerField()
    date = models.DateField()

    def __str__(self):
        return f'{self.origin_city_id}-{self.destination_city_id}-{self.price}-{"tipax" if self.is_tipax else "post"} '


class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(UserAddress, null=True, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    vip_post = models.BooleanField(default=False)
    tipax_post_delivery = models.BooleanField(default=False)
    in_city_delivery = models.BooleanField(default=False)
    physical_delivery = models.BooleanField(default=False)

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
    discount = models.OneToOneField('Discount', null=True, blank=True,
                                    on_delete=models.CASCADE, related_name='discount')

    total_price = models.PositiveBigIntegerField(default=0)
    total_weight = models.PositiveBigIntegerField(default=0)
    total_length = models.PositiveBigIntegerField(default=0)
    total_width = models.PositiveBigIntegerField(default=0)
    total_height = models.PositiveBigIntegerField(default=0)

    official_invoice = models.BooleanField(default=False)
    official_invoice_conformed_given_to_user = models.BooleanField(default=False)
    official_invoice_pdf = models.FileField(upload_to=pdf_path_upload_to, null=True, blank=True)

    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    canceled = models.BooleanField(default=False)

    additional_descriptions = models.TextField(null=True, blank=True)

    def calculate_tipax_price(self):
        price = DeliveryPrices.objects.filter(
            is_tipax=True,
            origin_city_id=self.store.orgin_city_id,
            destination_city_id=self.address.city_code,
            date__range=[now() - timedelta(days=3), now()],
        )
        if price.exists() and price.count() == 1:
            return price.first().price
        else:
            price = calculate_price_tipax(self)
            DeliveryPrices.objects.create(
                is_tipax=True,
                origin_city_id=self.store.orgin_city_id,
                destination_city_id=self.address.city_code,
                date=now(),
                price=price,
            )
            return price

    def calculate_post_price(self):
        price = DeliveryPrices.objects.filter(
            is_tipax=False,
            origin_city_id=self.store.orgin_city_id,
            destination_city_id=self.address.city_code,
            date__range=[now() - timedelta(days=3), now()],
        )
        if price.exists() and price.count() == 1:
            return price.first().price
        else:
            price = calculate_price_post()
            DeliveryPrices.objects.create(
                is_tipax=False,
                origin_city_id=self.store.orgin_city_id,
                destination_city_id=self.address.city_code,
                date=now(),
                price=price,
            )
            return price

    def calculate_total_price(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_price = 0

            for item in details:
                total_price += item.get_item_price()

            self.total_price = total_price
            self.save()
            return self.total_price
        else:
            return self.total_price

    def calculate_total_price_with_out_discount(self):

        details = self.details.all()
        total_price = 0

        for item in details:
            total_price += item.get_item_price_without_discount()

        return self.total_price

    def get_total_weight(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_weight = 0

            for item in details:
                total_weight += item.product.weight * item.count

            self.total_weight = total_weight
            self.save()
            return self.total_weight
        else:
            return self.total_weight

    def get_total_length(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_length = 0

            for item in details:
                total_length += item.product.length * item.count

            self.total_length = total_length
            self.save()
            return self.total_length
        else:
            return self.total_length

    def get_total_width(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_width = 0

            for item in details:
                total_width += item.product.width * item.count

            self.total_width = total_width
            self.save()
            return self.total_width
        else:
            return self.total_width

    def get_total_height(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_height = 0

            for item in details:
                total_height += item.product.height * item.count

            self.total_height = total_height
            self.save()
            return self.total_height
        else:
            return self.total_height

    def get_items_discount_amount(self):
        total_amount = 0

        for item in self.details.all():
            total_amount += item.get_item_discount()

        return total_amount

    def get_total_discount_amount(self):
        item_discount_amount = self.get_items_discount_amount()
        result_amount = item_discount_amount

        if self.use_discount_code:
            result_amount += self.discount_code_price

        return result_amount

    def get_payment_price(self):
        site = SiteSetting.objects.first()

        total_amount_of_items = self.calculate_total_price()

        total_payment_price = total_amount_of_items + self.delivery_price - self.get_total_discount_amount()

        # store

        if self.official_invoice and self.store.have_official_invoice and site.active_receive_official_invoice:
            total_payment_price += (total_amount_of_items * (self.store.official_invoice_price / 100))

        if self.store.additional_price:
            total_payment_price += self.store.additional_price

        if self.store.additional_tax:
            total_payment_price += (total_amount_of_items * (self.store.additional_tax / 100))

        # site
        total_payment_price += (total_amount_of_items * (site.tax / 100))

        self.total_price = total_payment_price
        self.save()
        return total_payment_price

    def check_count_of_products(self):
        return all(
            item.count <= item.product.count
            for item in self.details.select_related('product')
        )

    def mines_order_detail_count_from_products_count(self):
        for item in self.details.all():
            item.product.count = item.product.count - item.count
            item.product.save()

    def __str__(self):
        return f'{self.user.PhoneNumber} - {self.store.name} - {self.id}'


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')

    date = models.DateTimeField(auto_now_add=True)
    price = models.PositiveBigIntegerField(default=0)
    count = models.PositiveBigIntegerField(default=1)

    is_active = models.BooleanField(default=True)

    def get_item_price(self):
        product = self.product.calc_discount()
        price = product * self.count

        self.price = price
        self.save()
        return price

    def get_item_price_without_discount(self):
        product = self.product.price
        price = product * self.count

        self.price = price
        self.save()
        return price

    def get_item_discount(self):
        product_discount = self.product.calc_discount() * self.count
        product_real_price = self.product.price * self.count

        return product_real_price - product_discount

    def __str__(self):
        return f'{self.order.id} - {self.id}'


class Discount(models.Model):
    user = models.ManyToManyField(User, related_name='discounts', blank=True)
    product = models.ManyToManyField(Product, related_name='discounts', blank=True)
    store = models.ManyToManyField(Store, blank=True, related_name='discounts')
    order = models.ManyToManyField(Order, related_name='discounts',  blank=True)

    end_date_discount = models.DateTimeField(null=True, blank=True)
    count = models.PositiveBigIntegerField(default=0)
    percentage_discount = models.BooleanField(default=False)
    percent = models.PositiveBigIntegerField(null=True, blank=True)
    price = models.PositiveBigIntegerField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True, unique=True, db_index=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} - {self.id}'


class StoreSoldOrders(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='store_sold_orders')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_sold_orders')
    price = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f'{self.price} <-> {self.store.name}'
