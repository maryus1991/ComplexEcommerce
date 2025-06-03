from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import static
from django.utils.crypto import get_random_string

from user.views import e_namad

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("user.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("product/", include("product.urls")),
    path("order/", include("orders.urls")),
    path("blog/", include("blog.urls")),
    # path(f"{get_random_string(100)}-store/", include("stores.urls")),
    path("store/", include("stores.urls")),
    # path(f"{get_random_string(500)}-admin/", include("stores.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("", include("sitesetting.urls")),
    path("14545014.txt", e_namad, name='e-namad'),
]

handler404 = 'sitesetting.views.custom_404_page'

if settings.DEBUG:
    urlpatterns = urlpatterns + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
