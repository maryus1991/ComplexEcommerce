from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from guarantee.models import ActiveProductGuarantee
from django.utils.timezone import now
from django.db import transaction
from dateutil.relativedelta import relativedelta


@receiver(post_save, sender=Order)
def create_active_guarantee(sender, instance, created, **kwargs):
    if not created and instance.is_paid and instance.is_active and not instance.canceled and not instance.canceled_by_admin:
        details = instance.details.select_related("product").prefetch_related("product__guarantee")
        current_time = now()
        to_create = []
        for order_detail in details:
            guarantees = list(order_detail.product.guarantee.all())
            guarantee = guarantees[0] if guarantees else None
            if guarantee and guarantee.is_active:
                to_create.append(
                    ActiveProductGuarantee(
                        guarantee=guarantee,
                        order=order_detail,
                        date_of_expire=current_time + relativedelta(months=guarantee.months_of_expire),
                    )
                )
        if to_create:
            with transaction.atomic():
                ActiveProductGuarantee.objects.bulk_create(to_create)
