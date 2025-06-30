from django import forms
from phonenumber_field.validators import validate_phonenumber

from .models import ContactUs


class ContactForm(forms.ModelForm):

    class Meta:
        model = ContactUs
        fields = ["subject", "email", "message", "phone"]

        widgets = {
            "subject": forms.TextInput(
                attrs={"placeholder": "عنوان", "class": "tailwind-input col-span-12"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "ایمیل", "class": "tailwind-input col-span-6"}
            ),
            "message": forms.Textarea(
                attrs={"placeholder": "متن", "class": "tailwind-input col-span-12 h-24"}
            ),
            "phone": forms.NumberInput(
                attrs={
                    "placeholder": "شماره موبایل",
                    "class": "tailwind-input col-span-6",
                    "dir": "rtl",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        validate_phonenumber(phone)
        return phone
