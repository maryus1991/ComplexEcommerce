from django.db import models
from random import randint
from config import settings
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from .managers import UserManager
from stores.models import Store
from utils.send_email_task import send_email_task
from utils.send_otp import send_otp
from utils.send_email_task import send_email_task
from django.shortcuts import reverse
from easy_thumbnails.fields import ThumbnailerImageField


class User(AbstractUser):
    username = None
    PhoneNumber = PhoneNumberField(unique=True, db_index=True)
    email = models.EmailField(unique=True, blank=True, null=True, db_index=True)
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=True,
        related_name="users",
    )

    otp = models.CharField(max_length=4, blank=True)
    otp_expiry_date = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_store_admin = models.BooleanField(default=False)
    message_verified = models.BooleanField(default=True)

    private_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )
    email_verified = models.BooleanField(default=False)
    phone_number_verified = models.BooleanField(default=False)

    # colleague users 

    colleague_user = models.BooleanField(default=False)
    colleague_request = models.BooleanField(default=False)
    colleague_id = models.PositiveBigIntegerField(default=0)
    store_address = models.TextField(blank=True, null=True)
    store_image=ThumbnailerImageField(upload_to='colleague/images/store/', null=True, blank=True)
    colleague_with_store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=True,
        related_name="colleague_users",
    )


    # legal person infos
    legal_person = models.BooleanField(default=False, db_index=True)
    legal_person_economic_number = models.CharField(
        max_length=100, null=True, blank=True, db_index=True
    )
    legal_person_registration_number = models.CharField(
        max_length=100, null=True, blank=True, db_index=True
    )
    legal_person_phone = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    USERNAME_FIELD = "PhoneNumber"
    EMAIL_FIELD = "PhoneNumber"

    def __str__(self):
        return f"{self.PhoneNumber}-{self.id}"

    REQUIRED_FIELDS = ["first_name", "last_name"]


    def verify_email(self, request):
        private_code = get_random_string(100)

        if self.email is None:
            return False

        self.private_code = private_code
        self.save()

        try:
            send_email_task(
                self.email,
                request.build_absolute_uri(reverse('user:verify-email', kwargs={'private_code': private_code}))
            )
        except Exception as e:
            print(e)

        return private_code


    def set_otp(self) -> int:
        otp = randint(1000, 9999)
        self.otp_expiry_date = timezone.now() + settings.OTP_EXPIRATION
        self.otp = otp
        self.save()

        try:
            send_otp.delay(
                str(self.PhoneNumber).replace(" ", ""),
                otp
            )
        except Exception as e:
            print(e)

        return otp

    def verify_otp(self, otp: str) -> bool:

        if (int(self.otp) == int(otp)) and (self.otp_expiry_date >= timezone.now()):
            self.otp = ""
            self.otp_expiry_date = None
            self.save()
            return True
        else:
            return False

    class Meta:
        ordering = ("-date_joined",)

    objects = UserManager()
