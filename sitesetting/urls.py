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
    dynamic_favicon,
SiteLawListView, UsedAppDetailView
)
from .sitemap import StaticSitemap, UsedAppSiteMap
from admin_panel.views import dynamic_fonts_css

app_name = "site"

urlpatterns = [
    path("", Main.as_view(), name="main"),
    path('favicon.ico', dynamic_favicon, name='favicon'),
    path("Q&A", QuestionsPageView.as_view(), name="Q&A"),
    path("site-law", SiteLawListView.as_view(), name="site-law"),
    path("about-us", AboutUs.as_view(), name="about-us"),
    path("contact-us", ContactUs.as_view(), name="contact-us"),
    path("add-to-news-letters", AddTONewsLetters.as_view(), name="add-to-news-letters"),
    path("apps/", UsedAppView.as_view(), name="apps-list"),
    path("apps/<int:pk>", UsedAppDetailView.as_view(), name="apps-details"),
    path("apps/download/<int:pk>", DownloadUsedAppView.as_view(), name="apps-download"),
    path("partial/header/", header_render_partial, name="partial-header"),
    path("partial/footer/", footer_render_partial, name="partial-footer"),
    path('fonts/fonts.css', dynamic_fonts_css, name='fonts.css'),

]

sitemaps = {
    "static": StaticSitemap,
    "apps": UsedAppSiteMap,
}
