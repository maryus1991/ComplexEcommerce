from datetime import timedelta
from easy_thumbnails.fields import ThumbnailerImageField
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor_uploader.fields import RichTextUploadingField
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

class Store(models.Model):
    name = models.CharField(max_length=100)
    phone = PhoneNumberField(null=True, blank=True)
    phone2 = PhoneNumberField(null=True, blank=True)

    sort_number = models.IntegerField(default=0)
    whats_app_link = models.URLField(
        null=True,
        blank=True,
    )
    whats_app_ID = models.CharField(null=True, blank=True, max_length=20)
    telegram_app_ID = models.CharField(null=True, blank=True, max_length=20)
    telegram_app_Link = models.URLField(
        null=True,
        blank=True,
    )
    instagram_app_ID = models.CharField(null=True, blank=True, max_length=20)
    instagram_app_Link = models.URLField(
        null=True,
        blank=True,
    )

    logo = ThumbnailerImageField(
        null=True,
        blank=True,
        resize_source={"size": (512, 512), "crop": False, "upscale": False, "quality": 85},
    )
    address = models.CharField(max_length=200, null=True)
    zip_code = models.CharField(null=True, blank=True, max_length=20)
    province = models.CharField(null=True, blank=True, max_length=20)
    orgin_city_id = models.BigIntegerField(null=True, blank=True)
    orgin_city_id_post = models.BigIntegerField(null=True, blank=True)
    orgin_city = models.CharField(max_length=20, null=True, blank=True)
    card = models.CharField(null=True, blank=True, max_length=100)
    card_shaba = models.CharField(null=True, blank=True, max_length=100)
    card_name = models.CharField(null=True, blank=True, max_length=100)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)

    description = RichTextUploadingField(null=True, blank=True)
    about_image = ThumbnailerImageField(
        null=True,
        blank=True,
        resize_source={"size": (1200, 1200), "crop": False, "upscale": False, "quality": 80},
    )

    # official invoice
    have_official_invoice = models.BooleanField(default=True)
    official_invoice_price = models.PositiveIntegerField(default=0)
    economic_number = models.CharField(max_length=100, null=True, blank=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    official_invoice_phone_number = models.CharField(
        max_length=100, null=True, blank=True
    )


    time_for_return_order_days = models.PositiveSmallIntegerField(default=1)

    # store delivery
    have_post_delivery = models.BooleanField(default=True)
    have_tipax_delivery = models.BooleanField(default=True)
    have_in_same_city_delivery = models.BooleanField(default=True)
    have_physical_delivery = models.BooleanField(default=True)
    have_freight_delivery = models.BooleanField(default=True)
    in_same_city_delivery_price = models.PositiveIntegerField(default=0)

    additional_price = models.PositiveIntegerField(default=0)
    additional_tax = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # store permissions
    can_stores_add_product = models.BooleanField(default=True)
    can_stores_add_colleague_user = models.BooleanField(default=True)
    can_stores_add_product_brand = models.BooleanField(default=False)
    can_stores_add_product_category = models.BooleanField(default=False)
    can_store_add_blog_post = models.BooleanField(default=False)
    can_store_add_blog_category = models.BooleanField(default=False)
    can_store_add_users = models.BooleanField(default=True)
    can_store_add_apps = models.BooleanField(default=False)
    can_store_add_product_guarantee = models.BooleanField(default=True)
    allowed_to_add_and_edit_products_with_out_admin_per = models.BooleanField(default=False)
    allowed_to_add_and_edit_apps_with_out_admin_per = models.BooleanField(default=False)
    allowed_to_add_and_edit_posts_with_out_admin_per = models.BooleanField(default=False)
    allowed_to_activate_product_categories_with_out_admin_per = models.BooleanField(default=False)
    allowed_to_activate_product_brand_with_out_admin_per = models.BooleanField(default=False)
    zero_the_count_of_all_product_of_store = models.BooleanField(default=False)
    allowed_to_activate_post_categories_with_out_admin_per = models.BooleanField(default=False)

    def calculate_store_sold_orders(self):
        return sum(list(self.store_sold_orders.filter(is_returned_by_admin=False).values_list("price", flat=True)))

    def get_absolute_url(self):
        return reverse('stores:main-template-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Store"


class StoreApps(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="apps", verbose_name="فروشگاه"
    )
    file = models.FileField(upload_to="app/", verbose_name="فایل")
    name = models.CharField(max_length=100, verbose_name="نام")
    is_active = models.BooleanField(default=False, verbose_name="فعال / غیر فعال")
    short_description = RichTextUploadingField(null=True,
        blank=True,verbose_name='توضیحات'
    )
    admin_verified = models.BooleanField(default=True)
    image = ThumbnailerImageField(
        upload_to="site/apps/logo/",
        null=True,
        verbose_name="عکس",
        blank=True,
        resize_source={"size": (600, 600), "crop": False, "upscale": False, "quality": 80},
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("site:apps-details", kwargs={"pk": self.pk})


class UsedAppView(models.Model):
    app = models.ForeignKey(StoreApps, on_delete=models.CASCADE, related_name='views')
    ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    count = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, null=True, blank=True)


class StoreComment(models.Model):
    Store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = PhoneNumberField(unique=True, db_index=True)
    subject = models.CharField(max_length=100)
    comment = models.TextField()
