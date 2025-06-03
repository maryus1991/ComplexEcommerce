from django.db import models

from django.contrib.auth import get_user_model

from dashboard.models import UserAddress

from stores.models import Store
from product.models import Product

User = get_user_model()


# Create your models here.

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(UserAddress, null=True, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    post_price = models.PositiveBigIntegerField(default=0)

    vip_post = models.BooleanField(default=False)
    tipax_post_delivery = models.BooleanField(default=False)
    physical_delivery = models.BooleanField(default=False)
    in_city_delivery = models.BooleanField(default=False)

    sending = models.BooleanField(default=False)
    delivered_to_user = models.BooleanField(default=False)
    sending_id = models.CharField(max_length=500, null=True, blank=True)

    Authority = models.CharField(max_length=120, null=True, blank=True, unique=True)
    cart = models.CharField(max_length=120, null=True, blank=True, unique=True)
    payment_id = models.PositiveBigIntegerField(default=0)

    date = models.DateTimeField(auto_now_add=True)
    second_date = models.DateTimeField(null=True, blank=True)

    total_price = models.PositiveBigIntegerField(default=0)
    total_weight = models.PositiveBigIntegerField(default=0)
    total_length = models.PositiveBigIntegerField(default=0)
    total_width = models.PositiveBigIntegerField(default=0)
    total_height = models.PositiveBigIntegerField(default=0)

    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    canceled = models.BooleanField(default=False)

    additional_descriptions = models.TextField(null=True, blank=True)

    def calculate_total_price(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_price = self.post_price

            for item in details:
                total_price += item.get_item_price()

            self.total_price = total_price
            self.save()
            return self.total_price
        else:
            return self.total_price

    def get_total_weight(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_weight = self.total_weight

            for item in details:
                total_weight += item.product.weight

            self.total_weight = total_weight
            self.save()
            return self.total_weight
        else:
            return self.total_weight

    def get_total_length(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_length = self.total_length

            for item in details:
                total_length += item.product.length

            self.total_length = total_length
            self.save()
            return self.total_length
        else:
            return self.total_length

    def get_total_width(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_width = self.total_width

            for item in details:
                total_width += item.product.width

            self.total_width = total_width
            self.save()
            return self.total_width
        else:
            return self.total_width

    def get_total_height(self):
        if not self.is_paid or not self.canceled:
            details = self.details.all()
            total_height = self.total_height

            for item in details:
                total_height += item.product.height

            self.total_height = total_height
            self.save()
            return self.total_height
        else:
            return self.total_height

    def __str__(self):
        return f'{self.user.PhoneNumber} - {self.store.name} - {self.id}'


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')

    date = models.DateTimeField(auto_now_add=True)
    price = models.PositiveBigIntegerField(default=0)
    count = models.PositiveBigIntegerField(default=1)

    def get_item_price(self):
        product = self.product.calc_discount()
        price = product * self.count

        self.price = price
        self.save()
        return price

    def __str__(self):
        return f'{self.order.id} - {self.id}'
