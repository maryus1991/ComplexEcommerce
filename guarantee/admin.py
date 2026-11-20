from django.contrib import admin
from .models import ActiveProductGuarantee, ProductGuarantee


class SelectRelatedAdmin(admin.ModelAdmin):
    list_select_related = True


admin.site.register(ProductGuarantee, SelectRelatedAdmin)
admin.site.register(ActiveProductGuarantee, SelectRelatedAdmin)
