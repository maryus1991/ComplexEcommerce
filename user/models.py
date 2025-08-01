from django.db import models
from random import randint
from config import settings
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.utils import timezone

from .managers import UserManager
from stores.models import Store

from utils.send_otp import send_message
from utils.send_email_task import send_email_task

class User(AbstractUser):
    username = None
    PhoneNumber = PhoneNumberField(unique=True, db_index=True)
    email = models.EmailField(unique=True, blank=True, null=True)
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
        max_length=20,
        blank=True,
        null=True,
    )
    email_verified = models.BooleanField(default=False)
    phone_number_verified = models.BooleanField(default=False)

    # legal person infos
    legal_person = models.BooleanField(default=False)
    legal_person_economic_number = models.CharField(
        max_length=100, null=True, blank=True
    )
    legal_person_registration_number = models.CharField(
        max_length=100, null=True, blank=True
    )
    legal_person_phone = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "PhoneNumber"
    EMAIL_FIELD = "PhoneNumber"

    def __str__(self):
        return f"{self.PhoneNumber}-{self.id}"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    def set_otp(self) -> int:
        otp = randint(1000, 9999)
        self.otp_expiry_date = timezone.now() + settings.OTP_EXPIRATION
        self.otp = otp
        self.save()



        try:
            send_message.delay(
                str(self.PhoneNumber).replace(" ", ""),
                f"""            جهت حفظ امنیت حساب کابری شما از دادن این کد در دست دیگران خوداری فرمایید کد تایید شما
                  code: {self.otp}
                    """)
        except Exception as e:
            pass

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
