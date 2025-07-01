from django.urls import path

from .views import (
    Main,
    QuestionsPageView,
    AboutUs,
    ContactUs,
    AddTONewsLetters,
    footer_render_partial,
    header_render_partial,
    UsedAppView,
    DownloadUsedAppView,
    dynamic_favicon
)
from .sitemap import StaticSitemap, UsedAppSiteMap


app_name = "site"

urlpatterns = [
    path("", Main.as_view(), name="main"),
    path('favicon.ico', dynamic_favicon, name='favicon'),
    path("Q&A", QuestionsPageView.as_view(), name="Q&A"),
    path("about-us", AboutUs.as_view(), name="about-us"),
    path("contact-us", ContactUs.as_view(), name="contact-us"),
    path("add-to-news-letters", AddTONewsLetters.as_view(), name="add-to-news-letters"),
    path("apps/", UsedAppView.as_view(), name="apps-list"),
    path("apps/download/<int:pk>", DownloadUsedAppView.as_view(), name="apps-download"),
    path("partial/header/", header_render_partial, name="partial-header"),
    path("partial/footer/", footer_render_partial, name="partial-footer"),
]

sitemaps = {
    "static": StaticSitemap,
    "apps": UsedAppSiteMap,
}
