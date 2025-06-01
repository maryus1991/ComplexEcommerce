from django.contrib import admin

from .models import (Blog, BlogTag, BlogCategory)
# Register your models here.

admin.site.register(Blog)

admin.site.register(BlogTag)
admin.site.register(BlogCategory)