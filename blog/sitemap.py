from .models import Blog, BlogCategory
from django.contrib.sitemaps import Sitemap


class BlogSitemap(Sitemap):
    """for generate sitemap for blog model"""

    changefreq = "always"
    priority = 1

    def items(self):
        return Blog.objects.filter(is_active=True).all()

    def lastmod(self, obj):
        return obj.updated_at


