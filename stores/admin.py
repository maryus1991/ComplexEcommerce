from django.contrib import admin
from .models import Store, StoreApps, UsedAppView, StoreComment
from auditlog.registry import auditlog


class SelectRelatedAdmin(admin.ModelAdmin):
    list_select_related = True


admin.site.register(Store)
admin.site.register(StoreApps, SelectRelatedAdmin)
admin.site.register(UsedAppView, SelectRelatedAdmin)
admin.site.register(StoreComment, SelectRelatedAdmin)


auditlog.register(Store)
auditlog.register(StoreApps)
auditlog.register(StoreComment)
