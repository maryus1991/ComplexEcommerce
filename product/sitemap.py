from django.contrib.sitemaps import Sitemap
from .models import Product


class ProductSitemap(Sitemap):
    """
    for generate site map for Product model
    """

    changefreq = "always"
    priority = 1

    def items(self):
        return Product.objects.filter(is_active=True).all()

    def lastmod(self, obj):
        return obj.updated_at





