from django.contrib import admin
from auditlog.registry import auditlog

# Register your models here.
from .models import (
    ProductTag,
    Product,
    ProductComment,
    ProductCategory,
    ProductFeature,
    ProductGallery,
    ProductBrand,
    ProductCommentLikeAndDislike,
    UserFavorite,
)

admin.site.register(UserFavorite)
admin.site.register(ProductCommentLikeAndDislike)
admin.site.register(ProductBrand)
admin.site.register(ProductTag)
admin.site.register(Product)
admin.site.register(ProductComment)
admin.site.register(ProductCategory)
admin.site.register(ProductFeature)
admin.site.register(ProductGallery)
auditlog.register(UserFavorite)
auditlog.register(ProductCommentLikeAndDislike)
auditlog.register(ProductBrand)
auditlog.register(ProductTag)
auditlog.register(Product)
auditlog.register(ProductComment)
auditlog.register(ProductCategory)
auditlog.register(ProductFeature)
auditlog.register(ProductGallery)
