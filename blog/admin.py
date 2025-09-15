from django.contrib import admin
from auditlog.registry import auditlog

from .models import BlogCategory, Blog, BlogTag, BlogView

# Register your models here.

admin.site.register(Blog)
admin.site.register(BlogView)
admin.site.register(BlogTag)
admin.site.register(BlogCategory)

auditlog.register(Blog)
auditlog.register(BlogTag)
auditlog.register(BlogCategory)
