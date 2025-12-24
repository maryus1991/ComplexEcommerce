from django.urls import path
from .views import (
    AddOrder,
    CancelingOrder,
    RemoveItemFromOrder,
    RemoveProductFromOrder,
    ConformPayment,
    AddAddressToOrder,
    ChangeInvoiceToOfficial,
    OrderSetDiscount,
    ChooseTypeOfDelivery,
    OrderRemoveDiscount,
    VerifyPayment,
    SpecificsOrdersView,SpecificsOrdersVerifyPayment
)

app_name = "orders"

urlpatterns = [
    # specifics orders
    path('specifics-orders/', SpecificsOrdersView.as_view(), name='specifics-orders'),
    path('specifics-orders/payment/verify/<int:pk>/', SpecificsOrdersVerifyPayment.as_view(), name='specifics-payment-verify'),

    # orders
    path("add/<int:pk>/", AddOrder.as_view(), name="add"),
    path("cancel/<int:pk>/", CancelingOrder.as_view(), name="cancel"),
    path("remove/<int:pk>/", RemoveItemFromOrder.as_view(), name="remove"),
    path(
        "remove/product/<int:pk>/",
        RemoveProductFromOrder.as_view(),
        name="remove-product",
    ),
    path(
        "delivery/choose/<int:store_id>/<int:pk>/<int:did>",
        ChooseTypeOfDelivery.as_view(),
        name="choose-type-of-delivery",
    ),

    # address
    path(
        "add/address/<int:store_id>/<int:pk>",
        AddAddressToOrder.as_view(),
        name="add-address",
    ),

    # payment
    path("payment/conform/<int:pk>", ConformPayment.as_view(), name="payment-conform"),
    path("payment/result/<int:pk>", VerifyPayment.as_view(), name="payment-result"),

    # invoice status
    path(
        "invoice/status/<int:store_id>/<int:pk>",
        ChangeInvoiceToOfficial.as_view(),
        name="invoice-status",
    ),

    # set discount for order in conform payment page
    path(
        "discount/add/<int:store_id>/<int:pk>",
        OrderSetDiscount.as_view(),
        name="discount",
    ),
    path(
        "discount/remove/<int:store_id>/<int:pk>",
        OrderRemoveDiscount.as_view(),
        name="discount-remove",
    ),
]
