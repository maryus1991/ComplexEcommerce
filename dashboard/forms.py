from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.validators import validate_phonenumber
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.fields import RichTextUploadingFormField
from django.core.validators import FileExtensionValidator
from .models import UserAddress, Store


class UserColleagueForm(forms.Form):
    colleague_with_store = forms.ModelMultipleChoiceField(
        queryset=Store.objects.filter(
            can_stores_add_colleague_user=True,
            is_active=True,
            is_verified=True
        ),
        help_text="فروشگاهی که با آن همکاری دارید را انتخاب کنید",
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    store_address = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input lg:col-span-6 col-span-12 ",
                "placeholder": "ادرس فروشگاه ",
                "autocomplete": "password",
            }
        ),
    )

    store_image = forms.ImageField(
        required=False,
        label='عکس ( فروشگاه یا کارت ویزیت )',
        widget=forms.FileInput(
            attrs={"class": "hidden", "placeholder": "لوگو"}
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )
    
    colleague_id = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input lg:col-span-6 col-span-12 ",
                "placeholder": " کد ملی",
                "autocomplete": "password",
            }
        ),
    )




class CreateRequestReturnOrder(forms.Form):
    cart_name = forms.CharField(widget=forms.TextInput(
        attrs={"class": "tailwind-input col-span-6 ", "placeholder": "نام صاحب کارت"}
    ))
    card_number = forms.CharField(widget=forms.TextInput(
        attrs={"class": "tailwind-input col-span-6 ", "placeholder": "شماره کارت یا شماره شبا"}
    ))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
        attrs={
            "class": "tailwind-input col-span-12 h-24",
            "placeholder": "توضیحات اضافی",
        })
    )


class CreateUserAddress(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            "name",
            "last_name",
            "province",
            "city",
            "address",
            "phone",
            "zipcode",
            "additional_decryption",
            "city_code",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "tailwind-input col-span-6 ", "placeholder": "نام*"}
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "tailwind-input col-span-6 ",
                    "placeholder": "نام خانوادگی*",
                }
            ),
            "province": forms.TextInput(
                attrs={"class": "tailwind-input col-span-6 ", "placeholder": "استان*"}
            ),
            "city": forms.TextInput(
                attrs={"class": "tailwind-input col-span-6 ", "placeholder": "شهر*"}
            ),
            "address": forms.TextInput(
                attrs={"class": "tailwind-input col-span-12 ", "placeholder": "ادرس*"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "tailwind-input col-span-6",
                    "placeholder": "شماره موبایل*",
                    "dir": "rtl",
                }
            ),
            "zipcode": forms.TextInput(
                attrs={
                    "class": "tailwind-input col-span-6",
                    "placeholder": "کد پستی*",
                    "dir": "rtl",
                }
            ),
            "additional_decryption": forms.Textarea(
                attrs={
                    "class": "tailwind-input col-span-12 h-24",
                    "placeholder": "توضیحات اضافی",
                }
            ),
        }

    def clean_phone(self):
        cleaned_data = self.cleaned_data.get("phone")
        validate_phonenumber(cleaned_data)
        return cleaned_data


class UserTicketsClientForm(forms.Form):
    subject = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-6",
                "placeholder": "موضوع ...",
            }
        )
    )

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "tailwind-input col-span-12 h-full w-full ",
                "placeholder": "پیام ...",
            }
        )
    )

    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        help_text="جهت ارسال تیکیت به ادمین سایت فروشگاه را انتخاب نکنید ",
        required=False,
        widget=forms.Select(
            attrs={
                "class": "tailwind-input  col-span-6 py-2.5 w-full text text-white-500 px-1.5 py-1.5 dark:bg-zinc-700 border-0  appearance-none ",
            }
        ),
        empty_label="فروشگاه ... ",
    )


class UserTicketsClientFormMobile(forms.Form):
    subject = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-6",
                "placeholder": "موضوع ...",
            }
        )
    )

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "tailwind-input col-span-12 h-full w-full  ",
                "placeholder": "پیام ...",
            }
        )
    )
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        help_text="فروشگاه را انتخاب کنید",
        required=False,
        widget=forms.Select(
            attrs={
                "class": "tailwind-input  col-span-6 py-2.5 w-full text text-white-500 px-1.5 py-1.5 dark:bg-zinc-700 border-0  appearance-none ",
            }
        ),
        empty_label="فروشگاه را انتخاب کنید",
    )


class TicketConversationForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "tailwind-input col-span-12 ",
                "placeholder": "پیام ...",
            }
        )
    )


class TicketConversationMobileForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "tailwind-input col-span-12 h-36",
                "placeholder": "پیام ...",
            }
        )
    )
