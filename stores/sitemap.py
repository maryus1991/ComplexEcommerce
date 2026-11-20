from django.contrib.sitemaps import Sitemap
from stores.models import Store


class StoreSitemap(Sitemap):
    """
    for generate site map for store model
    """

    changefreq = "always"
    priority = 0.5

    def items(self):
        return (
            Store.objects.filter(is_active=True, is_verified=True)
            .only("id", "updated_at")
            .order_by("sort_number", "-updated_at")
        )

    def lastmod(self, obj):
        return obj.updated_at
