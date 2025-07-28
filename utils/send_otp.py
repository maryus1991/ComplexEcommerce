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


# todo : add celery shared task
from config import settings
from config.celery import shared_task


@shared_task(bind=True, queue='sms')
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
            print(result, 23242)
            raise Exception
        return result

    except Exception as e:
        print(e)
        client = Client("https://api.payamak-panel.com/post/Smartsms.asmx?wsdl")
        data = {
            "username": melipayamak_username,
            "password": melipayamak_password,
            "to": to,
            "from": melipayamak_from_number,
            "text": text + " لغو 11",
        }
        result = client.service.SendSmartSMS(**data)
        print(result, '2kkk')
        return result

# client = Client("https://api.payamak-panel.com/post/Smartsms.asmx?wsdl")
# data = {
#     "username": melipayamak_username,
#     "password": melipayamak_password,
#     "to": '09166355689',
#     "from": melipayamak_from_number,
#     "text": "  ابلغلهعله لغو 11" ,
# }
#
# result = client.service.SendSmartSMS(**data)
#
# print(result)
#


# api = Api(melipayamak_username,melipayamak_password)
# result = api.sms('soap').get_messages(1,0,10)
# print(result)

# api = Api(melipayamak_username,melipayamak_password)
# sms = api.sms('soap')
# x = sms.send_with_domain('09373061991', melipayamak_from_number, 'sdcsdc', False, 'domainName')
# print(x)
