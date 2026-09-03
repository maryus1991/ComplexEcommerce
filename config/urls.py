from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import static
from django.utils.crypto import get_random_string
from django.contrib.sitemaps.views import sitemap
from blog.urls import sitemaps as blog_sitemaps
from product.urls import sitemaps as product_sitemaps
from sitesetting.urls import sitemaps as site_sitemaps

from sitesetting.views import robots_txt
from stores.sitemap import StoreSitemap

urlpatterns = [
    path("user/", include("user.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("product/", include("product.urls")),
    path("order/", include("orders.urls")),
    path("blog/", include("blog.urls")),
    path("store/", include("stores.main_template_urls")),
    path("guarantee/", include("guarantee.urls")),
    # path(f"panel-store/{get_random_string(100)}/", include("stores.urls")),
    # path(f"admin-panel/{get_random_string(1000)}/", include("admin_panel.urls")),

    # path(f"admin/{get_random_string(1000)}/", admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("", include("sitesetting.urls")),
]

handler404 = "sitesetting.views.custom_404_page"
if settings.DEBUG:

    urlpatterns = urlpatterns + static.static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += [
        path("store-panel/", include("stores.urls")),
        path("admin-panel/", include("admin_panel.urls")),
        path("admin/", admin.site.urls),
        # path("silk/", include("silk.urls", namespace="silk")),
    ]

    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()



else:
    token = get_random_string(1000)
    urlpatterns += [
        path(f"panel-store/{get_random_string(1000)}/", include("stores.urls")),
        path(f"admin-panel/{token}/", include("admin_panel.urls")),

        path(f"admin/{token}/", admin.site.urls),
    ]


# site map and robots.txt


sitemaps = {'store':StoreSitemap}
sitemaps.update(blog_sitemaps)
sitemaps.update(product_sitemaps)
sitemaps.update(site_sitemaps)


urlpatterns += [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("sitemap1.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap1"),
    path("sitemap2.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap2"),
    path("sitemap3.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap3"),
    path("robots.txt", robots_txt, name="robots-txt"),
]
