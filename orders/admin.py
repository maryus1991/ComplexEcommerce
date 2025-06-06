from django.contrib import admin

# Register your models here.

from .models import Order, OrderDetail, Discount

admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Discount)