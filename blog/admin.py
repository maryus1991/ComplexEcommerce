from django.contrib import admin
from auditlog.registry import auditlog

from .models import Blog, BlogTag, BlogCategory

# Register your models here.

admin.site.register(Blog)

admin.site.register(BlogTag)
admin.site.register(BlogCategory)

auditlog.register(Blog)
auditlog.register(BlogTag)
auditlog.register(BlogCategory)
