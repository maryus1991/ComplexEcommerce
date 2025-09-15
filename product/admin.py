from django.contrib import admin
from auditlog.registry import auditlog

# Register your models here.
from .models import (
    ProductBrand,
ProductCategory,
Product,
NotificationUserForProductAvailability,
ProductGallery,
ProductComment,
ProductCommentLikeAndDislike,
ProductFeature,
ProductTag,
ProductSpecifications,
ProductViews,
UserFavorite
)

admin.site.register(ProductBrand)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(NotificationUserForProductAvailability)
admin.site.register(ProductGallery)
admin.site.register(ProductComment)
admin.site.register(ProductCommentLikeAndDislike)
admin.site.register(ProductFeature)
admin.site.register(ProductTag)
admin.site.register(ProductSpecifications)
admin.site.register(ProductViews)
admin.site.register(UserFavorite)

auditlog.register(UserFavorite)
auditlog.register(ProductCommentLikeAndDislike)
auditlog.register(ProductBrand)
auditlog.register(ProductTag)
auditlog.register(Product)
auditlog.register(ProductComment)
auditlog.register(ProductCategory)
auditlog.register(ProductFeature)
auditlog.register(ProductGallery)
