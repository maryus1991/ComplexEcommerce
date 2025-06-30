from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    AddProductComment,
    RemoveProductComment,
    AddUserToProductAvailability,
    AddLikeComment,
    DisLikeComment,
)


app_name = "product"

urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="detail"),
    path("add-comment/<int:pk>/", AddProductComment.as_view(), name="add_comment"),
    path(
        "remove-comment/<int:pk>/",
        RemoveProductComment.as_view(),
        name="remove_comment",
    ),
    path(
        "<int:pk>/like/<int:comment_id>", AddLikeComment.as_view(), name="like_comment"
    ),
    path(
        "<int:pk>/dislike/<int:comment_id>",
        DisLikeComment.as_view(),
        name="dislike_comment",
    ),
    path("<int:pk>/notif-me", AddUserToProductAvailability.as_view(), name="notif_me"),
]

from .sitemap import (ProductSitemap,
                      ProductCategorySitemap,
                      ProductBrandSitemap)

sitemaps = {
    "products": ProductSitemap,
    "categories": ProductCategorySitemap,
    "brands": ProductBrandSitemap,
}
