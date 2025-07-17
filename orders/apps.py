from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    # def ready(self):
    #     from django_celery_beat.models import PeriodicTask, IntervalSchedule
    #     from django_celery_beat.models import ClockedSchedule
    #     from django.utils.timezone import now
    #     import json
    #
    #     schedule, _ = IntervalSchedule.objects.get_or_create(
    #         every=1,
    #         period=IntervalSchedule.MINUTES,
    #     )
    #
    #     PeriodicTask.objects.get_or_create(
    #         name='Clean expired details every minute',
    #         task='orders.tasks.clean_expired_details',
    #         interval=schedule,
    #         defaults={
    #             'enabled': True,
    #             'queue': 'details',
    #             'start_time': now(),
    #         }
    #     )