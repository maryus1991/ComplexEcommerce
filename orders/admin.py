from django.contrib import admin
from auditlog.registry import auditlog
from .models import DeliveryPrices, Order, OrderDetail, Discount, StoreSoldOrders, ReturnsOrders, SpecificsOrders


class SelectRelatedAdmin(admin.ModelAdmin):
    list_select_related = True


admin.site.register(DeliveryPrices)
admin.site.register(Order, SelectRelatedAdmin)
admin.site.register(OrderDetail, SelectRelatedAdmin)
admin.site.register(Discount)
admin.site.register(StoreSoldOrders, SelectRelatedAdmin)
admin.site.register(ReturnsOrders, SelectRelatedAdmin)
admin.site.register(SpecificsOrders, SelectRelatedAdmin)


auditlog.register(Order)
auditlog.register(OrderDetail)
auditlog.register(Discount)
auditlog.register(DeliveryPrices)
auditlog.register(StoreSoldOrders)
