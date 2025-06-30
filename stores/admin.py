from django.contrib import admin
from .models import Store, StoreTag, StoreCategory, StoreApps, StoreComment
from auditlog.registry import auditlog


# Register your models here.

admin.site.register(Store)
admin.site.register(StoreComment)
admin.site.register(StoreApps)
admin.site.register(StoreTag)
admin.site.register(StoreCategory)

auditlog.register(Store)
auditlog.register(StoreApps)
auditlog.register(StoreComment)
auditlog.register(StoreTag)
auditlog.register(StoreCategory)
