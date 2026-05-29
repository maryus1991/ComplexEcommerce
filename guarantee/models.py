from django.db import models
from user.models import User
from product.models import Product
from phonenumber_field.modelfields import PhoneNumberField

class GuaranteeCompany(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True, verbose_name='فعال بودن')
    def __str__(self):
        return self.name
    

class ProductGuarantee(models.Model):
    company = models.ForeignKey(GuaranteeCompany, on_delete=models.CASCADE, db_index=True, verbose_name='شرکت', related_name='guarantee')
    serial_number = models.CharField(max_length=255, verbose_name='سریال نامبر', unique=True, db_index=True)
    months_of_expire = models.PositiveSmallIntegerField(verbose_name='تعداد ماه های انقضا')
    name = models.CharField(max_length=255, verbose_name='نام')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True, verbose_name='محصول', related_name='guarantee')
    is_active = models.BooleanField(default=True, verbose_name='فعال بودن')

    def __str__(self):
        return f'{self.serial_number} <-> {self.product.name} <-> {self.name} <-> {self.months_of_expire}'
    


class ActiveProductGuarantee(models.Model):
    guarantee = models.ForeignKey(ProductGuarantee, on_delete=models.SET_NULL, null=True, blank=False, db_index=True, verbose_name='گارانتی', related_name='actives_guarantee')
    user =  models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True, verbose_name='گارانتی', related_name='actives_guarantee')
    phone_number = PhoneNumberField(unique=False, db_index=True, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال بودن')
    serial_number = models.CharField(max_length=255, verbose_name='سریال فعال سازی', unique=True, db_index=True)
    date_of_started = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ شروع')
    date_of_expire = models.DateTimeField(verbose_name='تاریخ انقضا')

    def __str__(self):
        return f'{self.id}<->{self.name}'
    