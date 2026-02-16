from django.contrib import admin

# Register your models here.
from .models import ActiveProductGuarantee, ProductGuarantee

admin.site.register(ProductGuarantee)
admin.site.register(ActiveProductGuarantee)