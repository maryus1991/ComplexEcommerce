from django.contrib import admin
from auditlog.registry import auditlog

# Register your models here.

from .models import Order, OrderDetail, Discount, DeliveryPrices, StoreSoldOrders

admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Discount)
admin.site.register(DeliveryPrices)
admin.site.register(StoreSoldOrders)


auditlog.register(Order)
auditlog.register(OrderDetail)
auditlog.register(Discount)
auditlog.register(DeliveryPrices)
auditlog.register(StoreSoldOrders)
