from django.contrib.auth.models import AbstractUser

from config import settings
from config.celery import shared_task
from kavenegar import KavenegarAPI

from stores.models import Store

KAVEH_NEGAR_OTP = settings.KAVEH_NEGAR_OTP

@shared_task(queue='otp')
def send_otp(number, otp):
    try:
        api = KavenegarAPI(KAVEH_NEGAR_OTP)
        params = {
            'receptor': number,
            'template': 'main',
            'token': f'{otp}',
            'type': 'sms',
        }
        response = api.verify_lookup(params)

    except Exception as e:
        print(e)


@shared_task(queue='sms')
def send_message(number, template, message, second_message=None, third_message=None):
    try:
        api = KavenegarAPI(KAVEH_NEGAR_OTP)
        params = {
            'receptor': number,
            'template': template,
            'token': f'{message}',
            'type': 'sms',
        }
        if second_message:
            params.update(
                {
                    'token2':second_message
                }
            )
        if third_message:
            params.update(
                {
                    'token3':third_message
                }
            )

        print(params)
        response = api.verify_lookup(params)

        print(response.json())


    except Exception as e:
        print(e)

@shared_task(queue='sms')
def send_guarantee_message(params):
 

    try:
        api = KavenegarAPI(KAVEH_NEGAR_OTP) 
        response = api.verify_lookup(params)

    except Exception as e:
        print(e)

@shared_task(queue='sms')
def send_many_message(sender , number, message):
    try:
        api = KavenegarAPI(KAVEH_NEGAR_OTP)
        params = {
            'sender': str(sender),
            'receptor': str(number),
            'message': str(message),
        }
        response = api.verify_lookup(params)
        print(response.json())
    except Exception as e:
        print(e)


def OrderNotifyStoreSMS(
        request,
        store,
        site,

    ):
    user = request.user
    if site.active_sms_notify_store and request.user.is_authenticated:
        if store.sms_notify_permission and store.sms_notify_number:
            send_message.delay(
                str(store.sms_notify_number).replace(" ", ""),
                'OrderNotifyStore',
                store.name,
                str(user.PhoneNumber).replace(" ", ""),
                user.get_full_name(),
            )
