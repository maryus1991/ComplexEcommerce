from django.contrib import admin
from auditlog.registry import auditlog
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
    UserFavorite,
)


class SelectRelatedAdmin(admin.ModelAdmin):
    list_select_related = True


admin.site.register(ProductBrand)
admin.site.register(ProductCategory, SelectRelatedAdmin)
admin.site.register(Product, SelectRelatedAdmin)
admin.site.register(NotificationUserForProductAvailability, SelectRelatedAdmin)
admin.site.register(ProductGallery, SelectRelatedAdmin)
admin.site.register(ProductComment, SelectRelatedAdmin)
admin.site.register(ProductCommentLikeAndDislike, SelectRelatedAdmin)
admin.site.register(ProductFeature, SelectRelatedAdmin)
admin.site.register(ProductTag, SelectRelatedAdmin)
admin.site.register(ProductSpecifications, SelectRelatedAdmin)
admin.site.register(ProductViews, SelectRelatedAdmin)
admin.site.register(UserFavorite, SelectRelatedAdmin)


auditlog.register(UserFavorite)
auditlog.register(ProductCommentLikeAndDislike)
auditlog.register(ProductBrand)
auditlog.register(ProductTag)
auditlog.register(Product)
auditlog.register(ProductComment)
auditlog.register(ProductCategory)
auditlog.register(ProductFeature)
auditlog.register(ProductGallery)
