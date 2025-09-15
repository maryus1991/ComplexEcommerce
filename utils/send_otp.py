from config import settings
from config.celery import shared_task
from kavenegar import KavenegarAPI

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
        print(response.json())
    except Exception as e:
        print(e)


@shared_task(queue='sms')
def send_message(number, template, message):
    try:
        api = KavenegarAPI(KAVEH_NEGAR_OTP)
        params = {
            'receptor': number,
            'template': template,
            'token': f'{message}',
            'type': 'sms',
        }
        response = api.verify_lookup(params)
        print(response.json())
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
