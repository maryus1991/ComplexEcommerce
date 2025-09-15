from django.contrib.sitemaps import Sitemap
from .models import Product, ProductCategory, ProductBrand


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


class ProductCategorySitemap(Sitemap):
    """
    for generate site map for ProductCategory model
    """

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ProductCategory.objects.filter(is_active=True).all()

    def lastmod(self, obj):
        return obj.updated_at


class ProductBrandSitemap(Sitemap):
    """
    for generate site map for ProductBrand model
    """

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ProductBrand.objects.filter(is_active=True).all()

    def lastmod(self, obj):
        return obj.updated_at
