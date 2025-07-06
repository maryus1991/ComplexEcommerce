from django.contrib.sitemaps import Sitemap
from stores.models import Store


class StoreSitemap(Sitemap):
    """
    for generate site map for store model
    """

    changefreq = "always"
    priority = 0.5

    def items(self):
        return Store.objects.filter(is_active=True).all()

    def lastmod(self, obj):
        return obj.updated_at