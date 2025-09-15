from django.contrib import admin
from .models import Store, StoreApps, UsedAppView, StoreComment
from auditlog.registry import auditlog


# Register your models here.

admin.site.register(Store)
admin.site.register(StoreApps)
admin.site.register(UsedAppView)
admin.site.register(StoreComment)



auditlog.register(Store)
auditlog.register(StoreApps)
auditlog.register(StoreComment)

