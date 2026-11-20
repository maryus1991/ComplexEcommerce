from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from auditlog.registry import auditlog

from .models import User

auditlog.register(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    for set the user admin options
    """

    model = User
    list_select_related = ("store",)
    list_display = ("PhoneNumber", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "PhoneNumber")
    search_fields = ("PhoneNumber", "first_name", "last_name")
    ordering = ("is_staff", "is_superuser", "is_active", "PhoneNumber")

    add_fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "PhoneNumber",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "email",
                    "store",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "is_verified",
                    "is_store_admin",
                    "legal_person",
                    "legal_person_economic_number",
                    "legal_person_registration_number",
                    "colleague_user",
                    "colleague_request",
                    "colleague_id",
                    "store_address",
                    "store_image",
                    "colleague_with_store",
                )
            },
        ),
        ("Group&Permissions", {"fields": ("groups", "user_permissions")}),
    )

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "PhoneNumber",
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "otp",
                    "store",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "is_verified",
                    "is_store_admin",
                    "legal_person",
                    "legal_person_economic_number",
                    "legal_person_registration_number",
                    "colleague_user",
                    "colleague_request",
                    "colleague_id",
                    "store_address",
                    "store_image",
                    "colleague_with_store",
                )
            },
        ),
        ("Group&Permissions", {"fields": ("groups", "user_permissions")}),
        (
            "Important Date",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "otp_expiry_date",
                )
            },
        ),
    )
