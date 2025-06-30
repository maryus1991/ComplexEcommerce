from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
    path("account/", views.UserSettingDashboard.as_view(), name="account"),
    # orders
    path("orders/", views.OrdersHistoryDashboard.as_view(), name="orders"),
    path(
        "orders/<int:pk>/detials/",
        views.OrdersDetailHistoryDashboard.as_view(),
        name="order_detail",
    ),
    path(
        "orders/<int:pk>/detials/generate-pdf",
        views.GenerateOrderInvoice.as_view(),
        name="order-generate-invoice",
    ),
    # tickets urls
    path("tickets/", views.UserTicketDashboard.as_view(), name="tickets"),
    path("tickets/create/", views.CreateUserTicket.as_view(), name="tickets-create"),
    path(
        "tickets/<int:pk>",
        views.UserTicketConversation.as_view(),
        name="tickets-conversation",
    ),
    path("tickets/close/<int:pk>", views.CloseTicket.as_view(), name="tickets-close"),
    path(
        "tickets/delete/<int:pk>",
        views.DeleteMessageTicket.as_view(),
        name="tickets-delete",
    ),
    # favorite urls
    path("favorite/", views.FavoriteProductsDashboard.as_view(), name="favorite"),
    path(
        "add-to-favorite/<int:pk>",
        views.AddFavoriteProduct.as_view(),
        name="add_to_favorite",
    ),
    path(
        "remove-from-favorite/<int:pk>",
        views.RemoveFavoriteProduct.as_view(),
        name="remove_from_favorite",
    ),
    # user address
    path("address/", views.UserAddressDashboard.as_view(), name="address"),
    path("user-address/", views.CreateUserAddress.as_view(), name="create_address"),
    path(
        "user-address/<int:pk>",
        views.UpdateUserAddress.as_view(),
        name="update_address",
    ),
    path(
        "remove-user-address/<int:pk>",
        views.DeleteUserAddress.as_view(),
        name="remove_address",
    ),
]
