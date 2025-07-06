from django.contrib import admin
from .models import Store, StoreApps, StoreComment
from auditlog.registry import auditlog


# Register your models here.

admin.site.register(Store)
admin.site.register(StoreComment)
admin.site.register(StoreApps)


auditlog.register(Store)
auditlog.register(StoreApps)
auditlog.register(StoreComment)

