from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils.timezone import now

def create_cart_cleanup_task(sender, **kwargs):
    schedule, _ = IntervalSchedule.objects.get_or_create(every=1, period='minutes')

    PeriodicTask.objects.get_or_create(
        name='Clean expired details every minute',
        task='orders.tasks.clean_expired_details',
        interval=schedule,
        defaults={
            'enabled': True,
            'queue': 'details',
            'start_time': now(),
        }
    )
