from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.StoreMainPage.as_view(), name="home"),
    # product
    path("product/add/", views.StoreAddProduct.as_view(), name="add-product"),
    path("product/", views.StoreProductListView.as_view(), name="list-product"),
    path(
        "product/edit/<int:pk>/",
        views.StoreEditProductView.as_view(),
        name="edit-product",
    ),
    path(
        "product/edit/active-deactivate/<int:pk>/",
        views.StoreEditActiveOrDeactivateProduct.as_view(),
        name="active-deactivate-product",
    ),
    path(
        "product/edit/<int:pk>/remove/img/<int:img_id>/",
        views.StoreEditProductRemoveImg.as_view(),
        name="remove-img-edit-product",
    ),
    path(
        "product/remove/<int:pk>/",
        views.StoreDeleteProductView.as_view(),
        name="remove-product",
    ),
    # brands url
    path("brands/", views.ListBrandView.as_view(), name="list-brands"),
    path("brands/add", views.StoreAddBrandView.as_view(), name="add-brands"),
    # category
    path("category/", views.StoreListCategoryView.as_view(), name="list-category"),
    path("category/add/", views.StoreAddCategoryView.as_view(), name="add-category"),
    # store infos
    path("update/", views.StoreUpdateInformationView.as_view(), name="update"),
    # tickets
    path("tickets/send/", views.StoreSendTicketView.as_view(), name="send-ticket"),
    path("tickets/messages/delete/<int:pk>", views.StoreDeleteMessage.as_view(), name="send-messages-delete"),
    path(
        "tickets/close/sender-side<int:pk>/",
        views.StoreCloseTicketViewSenderSide.as_view(),
        name="close-ticket-sender-side",
    ),
    path(
        "tickets/close/reciver-side/<int:pk>/",
        views.StoreCloseTicketViewSenderSide.as_view(),
        name="close-ticket-receiver-side",
    ),
    path(
        "tickets/sended/list/",
        views.StoreSendTicketsListView.as_view(),
        name="list-sended-ticket",
    ),
    path(
        "tickets/sended/conversation/<int:pk>/",
        views.StoreConversationsView.as_view(),
        name="conversation-ticket",
    ),
    path(
        "tickets/received/list",
        views.StoreReceiveTicketListView.as_view(),
        name="list-received-ticket",
    ),
    path(
        "tickets/received/conversation/<int:pk>",
        views.StoreResponseToUsersTicketView.as_view(),
        name="response-received-ticket",
    ),
    # orders
    path(
        "orders/list/",
        views.StoreOrdersView.as_view(),
        name="orders-list-wait-for-sending-list",
    ),
    path(
        "orders/details/<int:pk>/",
        views.StoreOrderDetailView.as_view(),
        name="orders-detail",
    ),
    path(
        "orders/detials/invoice/offical/<int:pk>/generate/",
        views.AddOfficialInvoiceView.as_view(),
        name="official_invoice-pdf-generate",
    ),
    path(
        "orders/sending/<int:pk>",
        views.ChangeStatusToDeliveredToUser.as_view(),
        name="orders-sending",
    ),
    path(
        "orders/paid/",
        views.StoreSoleOrders.as_view(),
        name="orders-soled",
    ),
    # users
    path("users/list/", views.StoreUserListView.as_view(), name="user-list"),
    path("users/add/", views.StoreAddUsersView.as_view(), name="user-add"),
    path(
        "users/update/<int:pk>",
        views.StoreUpdateUsersView.as_view(),
        name="user-update",
    ),
    path(
        "users/update/active-deative/<int:pk>",
        views.StoreUserActiveOrDeativate.as_view(),
        name="user-active-or-deactivate",
    ),
    path("users/remove/<int:pk>", views.StoreRemoveUser.as_view(), name="user-remove"),
    path(
        "users/<int:pk>/activities/",
        views.StoreUserShowActivities.as_view(),
        name="user_activities",
    ),
    # store apps
    path("app/list/", views.StoreAppsView.as_view(), name="app-list"),
    path("app/upload-chunk-file/", views.ChunkedFileUploadView.as_view(), name="app-upload-app"),
    path(
        "app/remove-active-deactive/<int:pk>",
        views.RemoveAppsOrActiveOrDeactivateAppsView.as_view(),
        name="remove-active-deactive",
    ),
    # store blog
    path("blog/list/", views.StoreBlogListView.as_view(), name="blog-list"),
    path("blog/add/", views.StoreAddBlog.as_view(), name="blog-add"),
    path(
        "blog/update/<int:pk>", views.StoreBlogUpdateView.as_view(), name="blog-update"
    ),
    path(
        "blog/active-deactivate/<int:pk>",
        views.StoreActiveOrDeactivate.as_view(),
        name="blog-active-deactivate",
    ),
    path(
        "blog/delete/<int:pk>", views.StoreBlogDeleteView.as_view(), name="blog-delete"
    ),
    # store blog categories
    path(
        "blog/add/category",
        views.StoreBlogAddCategories.as_view(),
        name="blog-add-category",
    ),
    path(
        "blog/list/category",
        views.StoreBlogListCategories.as_view(),
        name="blog-list-category",
    ),
]
