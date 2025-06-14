from django.contrib import admin
from auditlog.registry import auditlog

# Register your models here.

from .models import Order, OrderDetail, Discount, DeliveryPrices

admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Discount)
admin.site.register(DeliveryPrices)


auditlog.register(Order)
auditlog.register(OrderDetail)
auditlog.register(Discount)
auditlog.register(DeliveryPrices)