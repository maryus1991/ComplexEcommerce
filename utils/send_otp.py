from zeep import Client
from pathlib import Path
from dotenv import load_dotenv
from os import path
import os

try:
    from .melipayamak import Api
except Exception as e:
    from melipayamak import Api
except Exception as e:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

local_env_file = path.join(BASE_DIR, ".envs")

if path.isfile(local_env_file):
    load_dotenv(dotenv_path=local_env_file)

melipayamak_username = os.getenv("melipayamak_panel_username")
melipayamak_password = os.getenv("melipayamak_panel_password")
melipayamak_from_number = os.getenv("melipayamak_panel_from_number")
KAVEH_NEGAR_OTP = os.getenv("KAVEH_NEGAR_OTP")

from config import settings
from config.celery import shared_task


@shared_task(queue='sms')
def send_otp(otp):
    from kavenegar import KavenegarAPI
    try:
        api = KavenegarAPI('')
        params = {
            'receptor': '09373061991',
            'template': 'main',
            'token': f'{otp}',
            'type': 'sms',
        }
        response = api.verify_lookup(params)
        print(response)
    except Exception as e:
        print(e)


@shared_task(queue='sms')
def send_message(
        to,
        text,
        username=melipayamak_username,
        password=melipayamak_password,
        _from=melipayamak_from_number,
):
    print('sending message')

    try:
        api = Api(username, password)
        result = api.sms("soap").send(to, _from, text)
        result = int(result)
        print(result, '1kkk')
        if 0 <= result <= 35:
            print(result.json())
            raise Exception
        return result

    except Exception as e:
        print(e)

