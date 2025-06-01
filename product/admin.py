from django.contrib import admin

# Register your models here.
from .models import (ProductTag,
                     Product,
                     ProductComment,
                     ProductCategory,
                     ProductFeature,
                     ProductGallery,
                     ProductBrand,
ProductCommentLikeAndDislike,
UserFavorite
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