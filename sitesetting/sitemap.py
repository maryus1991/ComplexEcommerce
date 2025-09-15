from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from stores.models import StoreApps


class StaticSitemap(Sitemap):
    """
    for generate sitemap for static pages
    """

    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["about-us", "Q&A", "contact-us"]

    def location(self, item):
        return reverse(f"site:{item}")


class UsedAppSiteMap(Sitemap):
    """
    for generate sitemap for app model
    """

    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return StoreApps.objects.filter(is_active=True).all()
