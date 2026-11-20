from operator import truediv

from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model

from phonenumber_field.modelfields import PhoneNumberField

from stores.models import Store

User = get_user_model()


class UserIP(models.Model):
    ip = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.get_full_name()}->{self.ip.__str__()}"


class Ticket(models.Model):

    subject = models.CharField(max_length=400)
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, null=True, blank=True, related_name="tickets"
    )  # receiver
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tickets"
    )  # sender
    date = models.DateTimeField(auto_now_add=True)
    close_ticket = models.BooleanField(default=False, db_index=True)
    closed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()}->{self.subject}"


class TicketConversation(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="message")
    message = RichTextUploadingField(null=True, blank=True)
    admin_message = models.BooleanField(default=False)
    is_read_by_server = models.BooleanField(default=False, db_index=True)
    is_read_by_client = models.BooleanField(default=False, db_index=True)
    date = models.DateTimeField(auto_now_add=True)
    date_read_by_admin = models.DateTimeField(null=True, blank=True)
    date_read_by_client = models.DateTimeField(null=True, blank=True)


class UserAddress(models.Model):
    name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    province = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    city_code = models.PositiveIntegerField(null=True, blank=True)
    city_code_post = models.PositiveIntegerField(null=True, blank=True)
    address = models.TextField()
    phone = PhoneNumberField()
    zipcode = models.CharField(max_length=120, null=True, blank=True)
    additional_decryption = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="address")

    def __str__(self):
        return f"{self.user.get_full_name()}->{self.address}"
