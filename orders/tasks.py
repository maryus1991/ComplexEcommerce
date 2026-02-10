from celery import shared_task
from django.utils.timezone import timedelta, now
from sitesetting.models import SiteSetting
from .models import OrderDetail


@shared_task(bind=True, queue='details')
def clean_expired_details(self):
    setting = SiteSetting.objects.first()
    minutes = setting.minute_for_clean_order_detail_product

    expired_orders = OrderDetail.objects.select_related("product", "order").filter(
        added_date__lte=now() - timedelta(minutes=minutes),
        order__is_paid=False,
        order__is_active=True,
        order__canceled=False,
        order__Authority__isnull=True,
    )

    count = 0
    for order_detail in expired_orders:
        order = order_detail.order
        should_keep_for_1_day = any([
            order.vip_post,
            order.tipax_post_delivery,
            order.in_city_delivery,
            order.physical_delivery,
            order.freight_delivery,
            order.use_discount_code,
            order.official_invoice,
            bool(order.additional_descriptions),
        ])

        if should_keep_for_1_day and order_detail.added_date > now() - timedelta(minutes=setting.minute_for_clean_order_submitted_detail_product):
            continue  # هنوز نباید پاک بشه

        # برگرداندن موجودی محصول
        product = order_detail.product
        product.count += order_detail.count
        product.save()

        # حذف آیتم از جزئیات سفارش
        order_detail.delete()
        count += 1

    return f"{count} carts deleted and stock restored."
