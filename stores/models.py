from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor_uploader.fields import RichTextUploadingField


class Store(models.Model):
    name = models.CharField(max_length=100)
    phone = PhoneNumberField(null=True, blank=True)
    phone2 = PhoneNumberField(null=True, blank=True)

    whats_app_link = models.URLField(null=True, blank=True, )
    whats_app_ID = models.CharField(null=True, blank=True, max_length=20)
    telegram_app_ID = models.CharField(null=True, blank=True, max_length=20)
    telegram_app_Link = models.URLField(null=True, blank=True, )
    instagram_app_ID = models.CharField(null=True, blank=True, max_length=20)
    instagram_app_Link = models.URLField(null=True, blank=True, )

    merchant_id = models.BigIntegerField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    orgin_city_id = models.BigIntegerField(null=True, blank=True)
    orgin_city = models.CharField(max_length=20 ,null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)

    description = RichTextUploadingField(null=True, blank=True)
    about_image = models.ImageField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class StoreApps(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='apps')
    file = models.FileField(upload_to="app/",)
    name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


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
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child')
    name = models.CharField(max_length=100)
