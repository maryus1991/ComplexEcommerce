from celery import shared_task
from django.db.models import F
from django.utils.timezone import timedelta, now
from product.models import Product
from sitesetting.models import SiteSetting
from .models import OrderDetail


@shared_task(bind=True, queue='details')
def clean_expired_details(self):
    setting = SiteSetting.get_cached()
    if not setting:
        return "0 carts deleted and stock restored."

    current_time = now()
    minutes = setting.minute_for_clean_order_detail_product
    submitted_cutoff = current_time - timedelta(
        minutes=setting.minute_for_clean_order_submitted_detail_product
    )
    expired_orders = OrderDetail.objects.select_related("product", "order").filter(
        added_date__lte=current_time - timedelta(minutes=minutes),
        order__is_paid=False,
        order__is_active=True,
        order__canceled=False,
        order__Authority__isnull=True,
    )

    detail_ids_to_delete = []
    stock_restore = {}
    for order_detail in expired_orders:
        order = order_detail.order
        if (
            order.freight_delivery
            or order.vip_post
            or order.tipax_post_delivery
            or order.in_city_delivery
            or order.physical_delivery
        ):
            if order_detail.added_date >= submitted_cutoff:
                continue

        detail_ids_to_delete.append(order_detail.id)
        stock_restore[order_detail.product_id] = (
            stock_restore.get(order_detail.product_id, 0) + order_detail.count
        )

    if detail_ids_to_delete:
        products = list(Product.objects.filter(id__in=stock_restore.keys()))
        for product in products:
            product.count = F("count") + stock_restore[product.id]
        if products:
            Product.objects.bulk_update(products, ["count"])
        OrderDetail.objects.filter(id__in=detail_ids_to_delete).delete()

    count = len(detail_ids_to_delete)
    return f"{count} carts deleted and stock restored."
