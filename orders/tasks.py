from celery import shared_task
from django.utils.timezone import timedelta, now

@shared_task(bind=True, queue='details')
def clean_expired_details(self):
    from .models import OrderDetail
    from sitesetting.models import SiteSetting
    setting = SiteSetting.objects.first()
    minute_for_clean_order_detail_product = setting.minute_for_clean_order_detail_product
    expired_orders = OrderDetail.objects.filter(
        added_date__lte=now() - timedelta(minutes=minute_for_clean_order_detail_product),
        order__is_paid=False, order__is_active=True, order__canceled=False, order__Authority__isnull=True
    )
    count = expired_orders.count()
    expired_orders.all().delete()
    return f"{count} carts deleted."
