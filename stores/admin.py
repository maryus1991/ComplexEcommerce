from django.contrib import admin
from .models import Store, StoreTag, StoreCategory, StoreApps, StoreComment
# Register your models here.

admin.site.register(Store)
admin.site.register(StoreComment)
admin.site.register(StoreApps)
admin.site.register(StoreTag)
admin.site.register(StoreCategory)