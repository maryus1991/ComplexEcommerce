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
            if len(city.split(' ')) == 1:
                if len(response.json()) > 1:
                    for item in response.json():
                        if item['title'] == city:
                            return [item]
            return response.json()

    elif response.status_code == 401:
        login()
        return send_request_for_city(city)
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


def calculate_price(
        store_origin_id,
        user_destination_id,
        order_obj,
        packing_id=0,  # for packing type
        package_content_id=1,  # for content of the box
        pack_type=20,  # type of the content of the box
        payment_type=80,  # the type of the payment
        pick_package_type=20,
        distribution_type=10,
        service_id=3,  # service type of sending
):
    if access_token is None:
        print('used')
        login()

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(access_token)}

    data = {
        "packageInputs": [
            {
                "origin": {
                    "cityId": store_origin_id
                },
                "destination": {
                    "cityId": user_destination_id
                },
                "weight": order_obj.get_total_weight() / 1000,
                "packageValue": order_obj.total_price,
                "length": order_obj.get_total_length() if order_obj.get_total_length() > 0 else 1,
                "width": order_obj.get_total_width() if order_obj.get_total_width() > 0 else 1,
                "height": order_obj.get_total_height() if order_obj.get_total_height() > 0 else 1,
                "packingId": packing_id,
                "packageContentId": package_content_id,
                "parcelBookId": order_obj.id,
                "isUnusual": True,
                "packType": pack_type,
                "paymentType": payment_type,
                "pickupType": pick_package_type,
                "distributionType": user_destination_id,
                "serviceId": service_id,
            }
        ]

    }

    response = requests.post(TIPAX_CALC_PRICE, data=json.dumps(data), headers=headers, )

    if response.status_code == 200:
        return response.json()[0]['regularRate']['finalPrice']
    elif response.status_code == 401:
        login()
        return calculate_price(
            store_origin_id,
            user_destination_id,
            order_obj,
            packing_id,
            package_content_id,
            pack_type,
            payment_type,
            pick_package_type,
            distribution_type,
            service_id)
    else:
        return None
