
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from guarantee.models import ActiveProductGuarantee
from django.utils.timezone import now
from django.db import transaction
from dateutil.relativedelta import relativedelta

@receiver(post_save, sender=Order)
def create_active_guarantee(sender, instance, created, **kwargs):

    if not created and instance.is_paid and instance.is_active and not instance.canceled and not instance.canceled_by_admin :

        for order in instance.details.all():

            with transaction.atomic():
                
                guarantee = order.product.guarantee.first()
                if guarantee and  guarantee.is_active :
                    ActiveProductGuarantee.objects.create(
                        guarantee=guarantee,
                        order=order,
                        date_of_expire=now() + relativedelta(months=guarantee.months_of_expire)
                    )



