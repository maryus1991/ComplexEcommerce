from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="main"),
    # site law
    path(
        "site-law/",
        views.SiteLawListView.as_view(),
        name="site-law-list",
    ),
    path(
        "site-law/set-sort-number/<int:pk>",
        views.SiteLawChangeSortNumber.as_view(),
        name="site-law-sort-number",
    ),
    path(
        "site-law/create/",
        views.SiteLawCreateView.as_view(),
        name="site-law-create",
    ),
    path(
        "site-law/update/<int:pk>",
        views.SiteLawUpdateView.as_view(),
        name="site-law-update",
    ),
    path(
        "site-law/active-deactivate/<int:pk>",
        views.SiteLawActiveAndDeactivateView.as_view(),
        name="site-law-active-deactivate",
    ),
    path(
        "site-law/delete/<int:pk>",
        views.SiteLawDeleteView.as_view(),
        name="site-law-delete",
    ),
    # site setting
    path(
        "update-site-setting/",
        views.UpdateSiteSettingView.as_view(),
        name="update-site-setting",
    ),
    path('fonts/', views.FontManagerView.as_view(), name='font-manager'),
    path('fonts/upload/', views.UploadFontView.as_view(), name='upload-font'),
    path('fonts/fonts.css', views.dynamic_fonts_css, name='fonts.css'),
    path('fonts/json/list/', views.font_list_json, name='font_list_json'),
    path('fonts/delete/<str:font_name>', views.DeleteFontView.as_view(), name='delete-font'),
    # banners
    path("banners/", views.BannersListView.as_view(), name="banners-list"),
    path("banners/create/", views.BannersCreateView.as_view(), name="banners-create"),
    path(
        "banners/update/<int:pk>",
        views.BannersUpdateView.as_view(),
        name="banners-update",
    ),
    path(
        "banners/active-deactivate/<int:pk>",
        views.BannersActiveAndDeactivateView.as_view(),
        name="banners-active-deactivate",
    ),
    path(
        "banners/delete/<int:pk>",
        views.BannersDeleteView.as_view(),
        name="banners-delete",
    ),
    # sliders
    path("sliders/", views.SliderListView.as_view(), name="sliders-list"),
    path("sliders/create/", views.SliderCreateView.as_view(), name="sliders-create"),
    path(
        "sliders/update/<int:pk>",
        views.SliderUpdateView.as_view(),
        name="sliders-update",
    ),
    path(
        "sliders/active-deactivate/<int:pk>",
        views.SliderActiveAndDeactivateView.as_view(),
        name="sliders-active-deactivate",
    ),
    path(
        "sliders/delete/<int:pk>",
        views.SliderDeleteView.as_view(),
        name="sliders-delete",
    ),
    # fast-links
    path("fast-links/", views.FastLinksListView.as_view(), name="fast-links-list"),
    path(
        "fast-links/create/",
        views.FastLinksCreateView.as_view(),
        name="fast-links-create",
    ),
    path(
        "fast-links/update/<int:pk>",
        views.FastLinksUpdateView.as_view(),
        name="fast-links-update",
    ),
    path(
        "fast-links/active-deactivate/<int:pk>",
        views.FastLinksActiveAndDeactivate.as_view(),
        name="fast-links-active-deactivate",
    ),
    path(
        "fast-links/delete/<int:pk>",
        views.FastLinksDelete.as_view(),
        name="fast-links-delete",
    ),
    # Q&A
    path("Q&A/", views.QuestionAndAnswerListView.as_view(), name="Q&A-list"),
    path("Q&A/create/", views.QuestionAndAnswerCreateView.as_view(), name="Q&A-create"),
    path(
        "Q&A/update/<int:pk>",
        views.QuestionAndAnswerUpdateView.as_view(),
        name="Q&A-update",
    ),
    path(
        "Q&A/active-deactivate/<int:pk>",
        views.QuestionAndAnswerActiveAndDeactivate.as_view(),
        name="Q&A-active-deactivate",
    ),
    path(
        "Q&A/delete/<int:pk>",
        views.QuestionAndAnswerDelete.as_view(),
        name="Q&A-delete",
    ),
    # apps
    path("apps/", views.AppsListView.as_view(), name="apps-list"),
    path("apps/ChunkedFileUploadView/", views.ChunkedFileUploadView.as_view(), name="apps-chunk-upload"),
    path("apps/create/", views.AppsCreateView.as_view(), name="apps-create"),
    path("apps/update/<int:pk>", views.AppsUpdateView.as_view(), name="apps-update"),
    path(
        "apps/active-deactivate/<int:pk>",
        views.AppsActiveAndDeactivateView.as_view(),
        name="apps-active-deactivate",
    ),
    path("apps/delete/<int:pk>", views.AppsDeleteView.as_view(), name="apps-delete"),
    # contact page
    path("contact/", views.ContactUsListView.as_view(), name="contact-list"),
    path(
        "contact/details/<int:pk>",
        views.ContactUsDetails.as_view(),
        name="contact-details",
    ),
    path(
        "contact/delete/<int:pk>",
        views.ContactUsDeleteView.as_view(),
        name="contact-delete",
    ),
    # blog
    path("blog/", views.BlogListView.as_view(), name="blog-list"),
    path("blog/create/", views.BlogCreate.as_view(), name="blog-create"),
    path("blog/update/<int:pk>", views.BlogUpdate.as_view(), name="blog-update"),
    path(
        "blog/active-deactivate/<int:pk>",
        views.BlogActiveAndDeactivate.as_view(),
        name="blog-active-deactivate",
    ),
    path("blog/delete/<int:pk>", views.BlogDelete.as_view(), name="blog-delete"),
    # blog category
    path(
        "blog/categories/",
        views.BlogCategoryListView.as_view(),
        name="blog-category-list",
    ),
    path(
        "blog/categories/set-sort-number/<int:pk>",
        views.BlogCategoryChangeSortNumber.as_view(),
        name="blog-category-sort-number",
    ),
    path(
        "blog/categories/create/",
        views.BlogCategoryCreate.as_view(),
        name="blog-category-create",
    ),
    path(
        "blog/categories/update/<int:pk>",
        views.BlogCategoryUpdate.as_view(),
        name="blog-category-update",
    ),
    path(
        "blog/categories/active-deactivate/<int:pk>",
        views.BlogCategoryActiveAndDeactivate.as_view(),
        name="blog-category-active-deactivate",
    ),
    path(
        "blog/categories/delete/<int:pk>",
        views.BlogCategoryDelete.as_view(),
        name="blog-category-delete",
    ),
    # tickets
    path("tickets/create/", views.SendTicketCreateView.as_view(), name="ticket-create"),
    path(
        "tickets/conversation/<int:pk>",
        views.TicketConversationDetailView.as_view(),
        name="ticket-conversation",
    ),
    path(
        "tickets/receivd/",
        views.TicketReceivedListView.as_view(),
        name="ticket-received-list",
    ),
    path("tickets/send/", views.TicketSendListView.as_view(), name="ticket-send-list"),
    path(
        "tickets/delete/<int:pk>",
        views.DeleteTicketView.as_view(),
        name="ticket-delete",
    ),
    path(
        "tickets/message/delete/<int:pk>",
        views.DeleteMessageView.as_view(),
        name="ticket-delete-message",
    ),
    path(
        "tickets/close/<int:pk>", views.CloseTicketView.as_view(), name="ticket-close"
    ),
    # store
    path("stores/", views.StoreListView.as_view(), name="store-list"),
    path("stores/create/", views.StoreCreateView.as_view(), name="store-create"),
    path(
        "store/set-sort-number/<int:pk>",
        views.StoreChangeSortNumber.as_view(),
        name="store-sort-number",
    ),
    path(
        "stores/update/<int:pk>", views.StoreUpdateView.as_view(), name="store-update"
    ),
    path(
        "stores/detail/<int:pk>", views.StoreDetailView.as_view(), name="store-detail"
    ),
    path(
        "stores/verify/<int:pk>", views.StoreVerifyView.as_view(), name="store-verify"
    ),
    path(
        "stores/active-deactivate/<int:pk>",
        views.StoreActiveAndDeactivateView.as_view(),
        name="store-active-deactivate",
    ),
    path(
        "stores/delete/<int:pk>", views.StoreDeleteView.as_view(), name="store-delete"
    ),
    # users
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/send-messages", views.UserSendManyMessage.as_view(), name="user-send-message"),
    path("users/create/", views.UserCreateView.as_view(), name="user-create"),
    path("users/update/<int:pk>", views.UserUpdateView.as_view(), name="user-update"),
    path("users/detail/<int:pk>", views.UserDetailsView.as_view(), name="user-detail"),
    path("users/admin-login/<int:pk>", views.AdminLoginToOtherUsersAccounts.as_view(), name="user-admin-login"),
    path("users/verify/<int:pk>", views.UserVerifyView.as_view(), name="user-verify"),
    path(
        "users/active-deactivate/<int:pk>",
        views.UserActiveDeactivateView.as_view(),
        name="user-active-deactivate",
    ),
    path(
        "users/activities/<int:pk>",
        views.UserActivitiesView.as_view(),
        name="user-activities",
    ),
    path("users/delete/<int:pk>", views.UserDeleteView.as_view(), name="user-delete"),
    # product
    path("product/", views.ProductListView.as_view(), name="product-list"),
    path("product/create/", views.ProductCreateView.as_view(), name="product-create"),
    path(
        "product/<int:pk>/remove-image-from-gallery/<int:img_id>",
        views.StoreEditProductRemoveImg.as_view(),
        name="product-remove-image",
    ),
    path(
        "product/update/<int:pk>",
        views.ProductUpdateView.as_view(),
        name="product-update",
    ),
    path(
        "product/active-deactivate/<int:pk>",
        views.ProductActiveAndDeactivateView.as_view(),
        name="product-active-deactivate",
    ),
    path(
        "product/verify/<int:pk>",
        views.ProductAdminVerifiedView.as_view(),
        name="product-verify",
    ),
    path(
        "product/delete/<int:pk>",
        views.ProductDeleteView.as_view(),
        name="product-delete",
    ),
    # product category
    path(
        "product/categories/",
        views.ProductCategoryListView.as_view(),
        name="product-category-list",
    ),
    path(
        "product/categories/set-sort-number/<int:pk>",
        views.ProductCategoryChangeSortNumber.as_view(),
        name="product-category-sort-number",
    ),
    path(
        "product/categories/create/",
        views.ProductCategoryCreateView.as_view(),
        name="product-category-create",
    ),
    path(
        "product/categories/update/<int:pk>",
        views.ProductCategoryUpdateView.as_view(),
        name="product-category-update",
    ),
    path(
        "product/categories/active-deactivate/<int:pk>",
        views.ProductCategoryActiveAndDeactivateView.as_view(),
        name="product-category-active-deactivate",
    ),
    path(
        "product/categories/delete/<int:pk>",
        views.ProductCategoryDeleteView.as_view(),
        name="product-category-delete",
    ),
    # product brand
    path(
        "product/brands/",
        views.ProductBrandListView.as_view(),
        name="product-brand-list",
    ),
    path(
        "product/brands/set-sort-number/<int:pk>",
        views.ProductBrandChangeSortNumber.as_view(),
        name="product-brands-sort-number",
    ),
    path(
        "product/brands/create/",
        views.ProductBrandCreateView.as_view(),
        name="product-brand-create",
    ),
    path(
        "product/brands/update/<int:pk>",
        views.ProductBrandUpdateView.as_view(),
        name="product-brand-update",
    ),
    path(
        "product/brands/active-deactivate/<int:pk>",
        views.ProductBrandActiveAndDeactivateView.as_view(),
        name="product-brand-active-deactivate",
    ),
    path(
        "product/brands/delete/<int:pk>",
        views.ProductBrandDeleteView.as_view(),
        name="product-brand-delete",
    ),
    # orders
    path("order/", views.OrderListView.as_view(), name="orders-list"),
    path("order/sold/", views.OrderSoldListView.as_view(), name="orders-sold-list"),
    path("order/<int:pk>", views.OrderDetailView.as_view(), name="orders-detail"),
    path("order/sold/<int:pk>", views.OrderSoledChangeStatus.as_view(), name="orders-change-sold-list-status"),
    # discount
    path("discount/", views.DiscountListView.as_view(), name="discount-list"),
    path(
        "discount/create/", views.DiscountCreateView.as_view(), name="discount-create"
    ),
    path(
        "discount/update/<int:pk>",
        views.DiscountUpdateView.as_view(),
        name="discount-update",
    ),
    path(
        "discount/active-deactivate/<int:pk>",
        views.DiscountActiveAndDeActivate.as_view(),
        name="discount-active-deactivate",
    ),
    path(
        "discount/delete/<int:pk>",
        views.DiscountDeleteView.as_view(),
        name="discount-delete",
    ),
    # backup
    path("backup/download/", views.OneClickBackup.as_view(), name="backup"),
    path("backup/restore/", views.BackupRestoreInOneClickView.as_view(), name="backup-restore"),
]
