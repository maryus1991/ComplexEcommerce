from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor_uploader.fields import RichTextUploadingField
from django.shortcuts import reverse


class Store(models.Model):
    name = models.CharField(max_length=100)
    phone = PhoneNumberField(null=True, blank=True)
    phone2 = PhoneNumberField(null=True, blank=True)

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

    logo = models.ImageField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    zip_code = models.CharField(null=True, blank=True, max_length=20)
    province = models.CharField(null=True, blank=True, max_length=20)
    orgin_city_id = models.BigIntegerField(null=True, blank=True)
    orgin_city = models.CharField(max_length=20, null=True, blank=True)
    card = models.CharField(null=True, blank=True, max_length=100)
    card_shaba = models.CharField(null=True, blank=True, max_length=100)
    card_name = models.CharField(null=True, blank=True, max_length=100)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)

    description = RichTextUploadingField(null=True, blank=True)
    about_image = models.ImageField(null=True, blank=True)

    # official invoice
    have_official_invoice = models.BooleanField(default=True)
    official_invoice_price = models.PositiveIntegerField(null=True, blank=True)
    economic_number = models.CharField(max_length=100, null=True, blank=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    official_invoice_phone_number = models.CharField(
        max_length=100, null=True, blank=True
    )

    # store delivery
    have_post_delivery = models.BooleanField(default=True)
    have_tipax_delivery = models.BooleanField(default=True)
    have_in_same_city_delivery = models.BooleanField(default=True)
    have_physical_delivery = models.BooleanField(default=True)
    in_same_city_delivery_price = models.PositiveIntegerField(null=True, blank=True)

    additional_price = models.PositiveIntegerField(null=True, blank=True)
    additional_tax = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    admin_verified = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("site:apps-list") + f"?q={self.name}"


class StoreComment(models.Model):
    Store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = PhoneNumberField(unique=True, db_index=True)
    subject = models.CharField(max_length=100)
    comment = models.TextField()


class StoreTag(models.Model):
    Store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class StoreCategory(models.Model):
    Store = models.ForeignKey(Store, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="child"
    )
    name = models.CharField(max_length=100)
