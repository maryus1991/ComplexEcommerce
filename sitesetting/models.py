from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor_uploader.fields import RichTextUploadingField

class SiteSetting(models.Model):
    title = models.CharField(max_length=100)
    tax = models.FloatField(default=1)
    copy_right_text = models.CharField(max_length=250)
    address = models.CharField(max_length=500)
    phone = PhoneNumberField()
    phone2 = PhoneNumberField()
    email = models.EmailField()

    telegram_link = models.URLField()
    telegram_ID = models.CharField(max_length=100)

    instagram_link = models.URLField()
    instagram_ID = models.CharField(max_length=100)

    logo = models.ImageField(upload_to="site/")
    short_description = models.TextField()

    long_description = RichTextUploadingField()

    about_image = models.ImageField(upload_to="site/")

    is_active = models.BooleanField(default=True)

    # delivery options for all website
    active_post_delivery = models.BooleanField(default=True)
    active_tipax_delivery = models.BooleanField(default=True)
    active_in_same_city_delivery = models.BooleanField(default=True)
    active_physical_delivery = models.BooleanField(default=True)

    active_receive_official_invoice = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class FastLinks(models.Model):
    title = models.CharField(max_length=100)
    link = models.URLField()

    def __str__(self):
        return self.title

class Newsletter(models.Model):
    phone_number = PhoneNumberField()

    def __str__(self):
        return self.phone_number

class QuestionAndAnswer(models.Model):
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question

class ContactUs(models.Model):
    subject = models.CharField(max_length=100)
    email = models.EmailField()
    phone = PhoneNumberField()
    message = models.TextField()

    def __str__(self):
        return f'{self.subject} - {self.email} - {self.phone}'