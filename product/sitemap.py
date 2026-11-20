from django.contrib.sitemaps import Sitemap
from .models import Product, ProductCategory, ProductBrand


class ProductSitemap(Sitemap):
    """
    Generate XML sitemap for active Products.
    """
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return (
            Product.objects.filter(
                is_active=True,
                admin_verified=True,
                store__is_active=True,
                store__is_verified=True,
            )
            .only("id", "updated_at")
            .order_by("-updated_at")
        )

    def lastmod(self, obj):
        return obj.updated_at


class ProductCategorySitemap(Sitemap):
    """
    Generate XML sitemap for active Product Categories.
    """
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return (
            ProductCategory.objects.filter(is_active=True)
            .only("id", "updated_at")
            .order_by("-sort_number", "id")
        )

    def lastmod(self, obj):
        return obj.updated_at


class ProductBrandSitemap(Sitemap):
    """
    Generate XML sitemap for active Product Brands.
    """
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return (
            ProductBrand.objects.filter(is_active=True)
            .only("id", "updated_at")
            .order_by("-sort_number", "id")
        )

    def lastmod(self, obj):
        return obj.updated_at
