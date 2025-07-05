from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from stores.models import Store

User = get_user_model()


class BlogCategory(models.Model):
    name = models.CharField(verbose_name="نام", max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته مادر",
    )

    image = models.ImageField(verbose_name="عکس", upload_to="blog_categories/")
    is_active = models.BooleanField(verbose_name="فعال / غیر فعال", default=True)
    sort_number = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:list") + f"?category={self.id}"


class Blog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        related_name="blogs",
        verbose_name="نویسنده",
    )
    title = models.CharField(max_length=100, verbose_name="عنوان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ساخت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان انتشار")
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="blogs",
        verbose_name="فروشگاه منتشر کننده",
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blogs",
        verbose_name="دسته",
    )
    content = RichTextUploadingField(verbose_name="متن یا بدنه")
    image = models.ImageField(upload_to="blogs/", null=True, verbose_name="عکس")

    is_active = models.BooleanField(
        default=False, verbose_name="فعال / غیر فعال برای انتشار توسط فروشگاه"
    )
    admin_verified = models.BooleanField(
        default=True, verbose_name="فعال / غیر فعال توسط ادمین"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"pk": self.pk})


class BlogTag(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BlogView(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="views")
    ip = models.GenericIPAddressField()
    count = models.IntegerField(default=1)

    def __str__(self):
        return self.ip
