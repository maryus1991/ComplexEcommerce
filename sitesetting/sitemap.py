from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from stores.models import StoreApps


class StaticSitemap(Sitemap):
    """
    Generate XML sitemap for public static pages.
    """
    changefreq = "weekly"

    def items(self):
        return [
            "site:main",
            "product:list",
            "blog:list",
            "stores:main-template-list",
            "site:apps-list",
            "guarantee:serial-number-search",
            "site:about-us",
            "site:contact-us",
            "site:Q&A",
            "site:site-law",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item in ("site:main", "product:list"):
            return 1.0
        if item in ("blog:list", "stores:main-template-list", "site:apps-list"):
            return 0.8
        return 0.6


class UsedAppSiteMap(Sitemap):
    """
    Generate XML sitemap for active StoreApps.
    """
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return (
            StoreApps.objects.filter(is_active=True, admin_verified=True)
            .only("id")
            .order_by("-id")
        )
