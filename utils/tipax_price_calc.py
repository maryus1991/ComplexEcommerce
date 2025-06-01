import requests, os, sys, json
import django
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config import settings

# tipax apis url

TIPAX_LOGIN = 'https://omtestapi.tipax.ir/api/OM/v3/Account/token'  # post
TIPAX_GET_LIST_CITIES = 'https://omtestapi.tipax.ir/api/OM/v3/Cities'  # get
TIPAX_CALC_PRICE = 'https://omtestapi.tipax.ir/api/OM/v3/Pricing'  # post
TIPAX_CALC_PRICE_MIN = 'https://omtestapi.tipax.ir/api/OM/v3/Pricing/Min'  # post



access_token = None


def login():

    data = {
        'username': settings.TIPAX_USERNAME,
        'password': settings.TIPAX_PASSWORD,
        'apiKey': settings.TIPAX_API_KEY,
    }

    headers = {'Content-Type': 'application/json'}

    try:
        # Convert data to JSON string for the request
        json_data = json.dumps(data)

        response = requests.post(
            TIPAX_LOGIN,
            data=json_data,
            headers=headers,
            timeout=10
        )

        # Check if response is successful
        response.raise_for_status()

        # Try to parse JSON only if there's content
        if response.content:
            global access_token
            access_token = response.json()['accessToken']
            return access_token

        else:
            return None

    except requests.exceptions.RequestException as e:

        return None
    except json.JSONDecodeError as e:

        return None

def send_request_for_city(city):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(access_token)}
    response = requests.get(TIPAX_GET_LIST_CITIES + f'?title={city}', headers=headers, )

    if response.status_code == 200:
        if type(response.json()) == list:
            if len(city.split(' ')) == 1 :
                if len(response.json()) > 1:
                    for item in response.json():
                        if item['title'] == city:
                            return [item]
            return response.json()
    else:
        return None

def validate_city(city: str):
    if access_token is None:
        print('used')
        login()

    response = send_request_for_city(city)
    if response is not None:
        return response
    else:
        return send_request_for_city(city)

