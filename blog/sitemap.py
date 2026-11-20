from django.contrib.sitemaps import Sitemap
from .models import Blog, BlogCategory


class BlogSitemap(Sitemap):
    """Generate XML sitemap for active Blog articles."""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return (
            Blog.objects.filter(is_active=True, admin_verified=True)
            .only("id", "updated_at")
            .order_by("-updated_at")
        )

    def lastmod(self, obj):
        return obj.updated_at


class BlogCategorySitemap(Sitemap):
    """Generate XML sitemap for active Blog categories."""
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BlogCategory.objects.filter(is_active=True).only("id").order_by("-sort_number", "id")
