import requests

try:
    from config import settings
except ImportError:
    from .config import settings


def detect_the_box_size(volume):
    box_sizes = [
        (1, (2, 11, 22)),     # 484 cm³
        (2, (2, 22, 31)),     # 1364
        (3, (2, 30, 45)),     # 2700
        (4, (15, 10, 10)),    # 1500
        (5, (20, 10, 15)),    # 3000
        (6, (20, 15, 20)),    # 6000
        (7, (30, 20, 20)),    # 12000
        (8, (35, 25, 25)),    # 21875
        (9, (45, 20, 25)),    # 22500
        (10, (40, 25, 30)),   # 30000
        (11, (45, 30, 40)),   # 54000
        (12, (50, 35, 45)),   # 78750
        (13, (999, 999, 999)),
    ]

    for size, (h, w, l) in box_sizes:
        box_volume = h * w * l
        if volume <= box_volume:
            return size

    return 13


def calculate_post_price_postex(order):

    headers = {
        "x-api-key": settings.POSTEX_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "from_city_code": order.store.orgin_city_id_post,
        "pickup_needed": False,
        "courier": {
            "courier_code": "IR_POST",
            "service_type": "EXPRESS"
        },
        "parcels": [
            {
                "to_city_code": order.address.city_code_post,
                "payment_type": "RECEIVER",
                "parcel_properties": {
                    "total_weight": order.get_total_weight(),
                    "is_fragile": True,
                    "is_liquid": False,
                    "total_value": order.get_payment_price() * 10,
                    "box_type_id": detect_the_box_size(order.calculate_total_volume())
                }
            }
        ], "value_added_service": {}

    }
    try:
        resp = requests.post(
            "https://api.postex.ir/api/v1/shipping/quotes",
            json=data,
            headers=headers,
            stream=True,
            timeout=30
        )
        return resp.json()['total_cost'] / 10
    except Exception as e:
        calculate_post_price_postex(order)


