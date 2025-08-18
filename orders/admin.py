from django.contrib import admin
from auditlog.registry import auditlog

# Register your models here.

from .models import DeliveryPrices, Order, OrderDetail, Discount, StoreSoldOrders, ReturnsOrders, SpecificsOrders

admin.site.register(DeliveryPrices)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Discount)
admin.site.register(StoreSoldOrders)
admin.site.register(ReturnsOrders)
admin.site.register(SpecificsOrders)



auditlog.register(Order)
auditlog.register(OrderDetail)
auditlog.register(Discount)
auditlog.register(DeliveryPrices)
auditlog.register(StoreSoldOrders)
