import requests, os, sys, json
import django
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.conf import settings

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
        order_obj,
        store_origin_id=0,
        user_destination_id=0,
        packing_id=0,  # for packing type
        package_content_id=1,  # for content of the box
        pack_type=20,  # type of the content of the box
        payment_type=80,  # the type of the payment
        pick_package_type=20,
        distribution_type=10,
        service_id=3,  # service type of sending
):
    try:
        if access_token is None:
            login()
            print('used')
            print(access_token)

        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(access_token)}

        data = {
            "packageInputs": [
                {
                    "origin": {
                        "cityId": int(order_obj.store.orgin_city_id)
                    },
                    "destination": {
                        "cityId": int(order_obj.address.city_code)
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
        print(json.dumps(data))
        response = requests.post(
            TIPAX_CALC_PRICE,
            data=json.dumps(data),
            headers=headers,
            stream=True,
            timeout=20
        )
        print(response.json())
        if response.status_code == 200:
            return int(response.json()[0]['regularRate']['finalPrice']) / 10
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
    except Exception as e:
        return None

#
# import requests
# import os
# import sys
# import json
# import logging
# from pathlib import Path
# from typing import Optional, List, Dict, Any
# from django.conf import settings
# from requests.exceptions import RequestException
#
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # Set up Django environment
# project_root = Path(__file__).resolve().parent.parent
# sys.path.append(str(project_root))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
#
# # Tipax API endpoints
# TIPAX_API_BASE = 'https://omtestapi.tipax.ir/api/OM/v3'
# TIPAX_LOGIN = f'{TIPAX_API_BASE}/Account/token'
# TIPAX_GET_LIST_CITIES = f'{TIPAX_API_BASE}/Cities'
# TIPAX_CALC_PRICE = f'{TIPAX_API_BASE}/Pricing'
#
# # Constants for shipping parameters
# PACKAGE_CONTENT_ID = 1  # Default content type
# PACK_TYPE = 20  # Default package type
# PAYMENT_TYPE = 80  # Default payment type
# PICK_PACKAGE_TYPE = 20  # Default pickup type
# DISTRIBUTION_TYPE = 10  # Default distribution type
# SERVICE_ID = 3  # Default service type
#
#
# class TipaxAPI:
#     """A thread-safe wrapper for Tipax shipping API."""
#
#     def __init__(self):
#         self._access_token = None
#         self._session = requests.Session()
#         self._session.headers.update({
#             'Content-Type': 'application/json',
#             'Accept': 'application/json'
#         })
#
#     def _make_request(
#             self,
#             method: str,
#             url: str,
#             data: Optional[Dict] = None,
#             retry: bool = True
#     ) -> Optional[Dict]:
#         """Generic request handler with auth and retry logic."""
#         headers = {}
#         if self._access_token:
#             headers['Authorization'] = f'Bearer {self._access_token}'
#
#         try:
#             response = self._session.request(
#                 method=method,
#                 url=url,
#                 json=data,
#                 headers=headers,
#                 timeout=15
#             )
#
#             if response.status_code == 401 and retry:
#                 logger.info("Authentication expired, refreshing token...")
#                 if self.login():
#                     return self._make_request(method, url, data, retry=False)
#
#             response.raise_for_status()
#             return response.json() if response.content else None
#
#         except RequestException as e:
#             logger.error(f"Request failed: {str(e)}")
#             return None
#         except json.JSONDecodeError as e:
#             logger.error(f"Failed to decode JSON response: {str(e)}")
#             return None
#
#     def login(self) -> bool:
#         """Authenticate with Tipax API and store the access token."""
#         auth_data = {
#             'username': settings.TIPAX_USERNAME,
#             'password': settings.TIPAX_PASSWORD,
#             'apiKey': settings.TIPAX_API_KEY,
#         }
#
#         try:
#             response = self._session.post(TIPAX_LOGIN, json=auth_data)
#             response.raise_for_status()
#
#             if response.content:
#                 data = response.json()
#                 self._access_token = data.get('accessToken')
#                 if self._access_token:
#                     logger.info("Successfully authenticated with Tipax API")
#                     return True
#
#             logger.error("Authentication failed: No access token received")
#             return False
#
#         except RequestException as e:
#             logger.error(f"Login failed: {str(e)}")
#             return False
#
#     def validate_city(self, city_name: str) -> Optional[List[Dict]]:
#         """Validate and retrieve city information from Tipax."""
#         if not city_name:
#             return None
#
#         if not self._access_token and not self.login():
#             return None
#
#         params = {'title': city_name.strip()}
#         result = self._make_request('GET', TIPAX_GET_LIST_CITIES, params)
#
#         if isinstance(result, list):
#             if len(city_name.split()) == 1 and len(result) > 1:
#                 # Try to find exact match if multiple results
#                 exact_match = [city for city in result if city['title'] == city_name]
#                 return exact_match if exact_match else result
#             return result
#         return None
#
#     def calculate_shipping_cost(
#             self,
#             order: object,
#             packing_id: int = 0,
#             package_content_id: int = PACKAGE_CONTENT_ID,
#             pack_type: int = PACK_TYPE,
#             payment_type: int = PAYMENT_TYPE,
#             pick_package_type: int = PICK_PACKAGE_TYPE,
#             distribution_type: int = DISTRIBUTION_TYPE,
#             service_id: int = SERVICE_ID,
#     ) -> Optional[float]:
#         """Calculate shipping cost for an order."""
#         if not self._access_token and not self.login():
#             return None
#
#         # Validate required order attributes
#         required_attrs = [
#             'store', 'address', 'get_total_weight',
#             'total_price', 'get_total_length',
#             'get_total_width', 'get_total_height', 'id'
#         ]
#         if not all(hasattr(order, attr) for attr in required_attrs):
#             logger.error("Invalid order object: missing required attributes")
#             return None
#
#         payload = {
#             "packageInputs": [{
#                 "origin": {
#                     "cityId": int(order.store.orgin_city_id)
#                 },
#                 "destination": {
#                     "cityId": int(order.address.city_code)
#                 },
#                 "weight": max(order.get_total_weight() / 1000, 0.1),  # minimum 0.1 kg
#                 "packageValue": order.total_price,
#                 "length": max(order.get_total_length(), 1),
#                 "width": max(order.get_total_width(), 1),
#                 "height": max(order.get_total_height(), 1),
#                 "packingId": packing_id,
#                 "packageContentId": package_content_id,
#                 "parcelBookId": order.id,
#                 "isUnusual": True,
#                 "packType": pack_type,
#                 "paymentType": payment_type,
#                 "pickupType": pick_package_type,
#                 "distributionType": distribution_type,
#                 "serviceId": service_id,
#             }]
#         }
#
#         result = self._make_request('POST', TIPAX_CALC_PRICE, payload)
#         if result and isinstance(result, list) and len(result) > 0:
#             try:
#                 # Convert final price from Rials to Tomans (/10)
#                 return float(result[0]['regularRate']['finalPrice']) / 10
#             except (KeyError, ValueError) as e:
#                 logger.error(f"Failed to parse price from response: {str(e)}")
#         return None
#
#
