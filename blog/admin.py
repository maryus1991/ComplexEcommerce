from django.contrib import admin
from auditlog.registry import auditlog
from .models import BlogCategory, Blog, BlogTag, BlogView


class SelectRelatedAdmin(admin.ModelAdmin):
    list_select_related = True


admin.site.register(Blog, SelectRelatedAdmin)
admin.site.register(BlogView, SelectRelatedAdmin)
admin.site.register(BlogTag, SelectRelatedAdmin)
admin.site.register(BlogCategory, SelectRelatedAdmin)


auditlog.register(Blog)
auditlog.register(BlogTag)
auditlog.register(BlogCategory)
