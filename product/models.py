from django.db import models
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
import secrets
import os
from django.shortcuts import reverse
from stores.models import Store
from django.utils.timezone import now


def photo_path_upload_to(instance, filename):
    basename = os.path.basename(filename)
    return f"images/products/{secrets.token_urlsafe(100)}-{basename}"


User = get_user_model()


class ProductBrand(models.Model):
    name = models.CharField(max_length=1000)
    image = models.ImageField(upload_to=photo_path_upload_to, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_number = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product:list") + "?brand=" + str(self.id)


class ProductCategory(models.Model):

    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="child"
    )
    name = models.CharField(max_length=1000)
    image = models.ImageField(upload_to=photo_path_upload_to, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_number = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product:list") + "?category=" + str(self.id)


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=1000)
    price = models.BigIntegerField()
    have_discount = models.BooleanField(default=False)
    discount = models.IntegerField(default=0)
    picture = models.ImageField(upload_to=photo_path_upload_to, null=True, blank=True)
    brand = models.ForeignKey(
        ProductBrand, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    description = RichTextUploadingField(null=True, blank=True)
    count = models.PositiveBigIntegerField(default=0)
    weight = models.PositiveBigIntegerField(default=0)
    length = models.PositiveBigIntegerField(default=0)
    width = models.PositiveBigIntegerField(default=0)
    height = models.PositiveBigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=False)
    admin_verified = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.name}-{self.id}-{self.count}"

    def calc_discount(self):

        if self.have_discount:
            price = self.price - (self.price * (self.discount / 100))
        else:
            price = self.price

        return price

    def get_absolute_url(self):
        return reverse("product:detail", kwargs={"pk": self.id})


class NotificationUserForProductAvailability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return f"{self.product.name} notification for {self.user.get_full_name()}"


class ProductGallery(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="gallery"
    )
    image = models.ImageField(upload_to=photo_path_upload_to)

    def __str__(self):
        return f"{self.product.name}-{self.id}"


class ProductComment(models.Model):
    Product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="comments", db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, related_name="product_comments"
    )
    subject = models.CharField(max_length=100)
    comment = models.TextField()
    suggest_product = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    buyer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.Product.name} : {self.user.get_full_name()} -> {self.subject}"


class ProductCommentLikeAndDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(
        ProductComment, on_delete=models.CASCADE, related_name="like"
    )
    like = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} : {self.comment.subject} -> {self.like}"


class ProductFeature(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="features"
    )
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.name} -> {self.title}"


class ProductTag(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100)


class ProductSpecifications(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specs")
    name = models.CharField(max_length=100)


class ProductViews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="views")
    ip = models.GenericIPAddressField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="views", null=True, blank=True
    )
    count = models.PositiveBigIntegerField(default=0)


class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="favorite"
    )

    def __str__(self):
        return f"{self.user.get_full_name()}<->{self.product.name}"
