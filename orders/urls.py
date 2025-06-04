from django.urls import path
from .views import (AddOrder,
                    CancelingOrder,
                    RemoveItemFromOrder,
                    RemoveProductFromOrder,
                    ConformPayment,
                    AddAddressToOrder)

app_name = 'orders'

urlpatterns = [
    path('add/<int:pk>/', AddOrder.as_view(), name='add'),
    path('cancel/<int:pk>/', CancelingOrder.as_view(), name='cancel'),
    path('remove/<int:pk>/', RemoveItemFromOrder.as_view(), name='remove'),
    path('remove/product/<int:pk>/', RemoveProductFromOrder.as_view(), name='remove-product'),

    # address
    path('add/address/<int:store_id>/<int:pk>', AddAddressToOrder.as_view(), name='add-address'),

    # payment
    path('payment/conform/<int:pk>', ConformPayment.as_view(), name='payment-conform'),
    path('payment/result/<int:pk>/', ConformPayment.as_view(), name='payment-result'),
]