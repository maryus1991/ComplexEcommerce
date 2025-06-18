from django import forms
from django.core.validators import FileExtensionValidator
from ckeditor_uploader.fields import RichTextUploadingFormField
from phonenumber_field.formfields import PhoneNumberField

from sitesetting.models import (
    SiteSetting,
    Banners,
    Slider,
    FastLinks,
    QuestionAndAnswer,
    ContactUs
)


class SiteSettingModelForm(forms.ModelForm):
    logo = forms.ImageField(
        required=False,
        label='لوگو',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ]
    )

    about_image = forms.ImageField(
        required=False,
        label='تصویر معرفی',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ]
    )

    long_description = RichTextUploadingFormField()
    phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',

            }
        )
    )
    phone2 = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',

            }
        )
    )

    class Meta:
        model = SiteSetting
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',

                }
            ),
            'tax': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'copy_right_text': forms.TextInput(
                attrs={
                    'class': 'form-control',

                }
            ),
            'address': forms.TextInput(
                attrs={
                    'class': 'form-control',

                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'telegram_link': forms.URLInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'telegram_ID': forms.TextInput(
                attrs={
                    'class': 'form-control',

                }
            ),
            'instagram_link': forms.URLInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'instagram_ID': forms.TextInput(
                attrs={
                    'class': 'form-control',

                }
            ),
            'short_description': forms.TextInput(
                attrs={
                    'class': 'form-control',

                }
            ),
            'is_active': forms.CheckboxInput(),
            'active_post_delivery': forms.CheckboxInput(),
            'active_tipax_delivery': forms.CheckboxInput(),
            'active_in_same_city_delivery': forms.CheckboxInput(),
            'active_physical_delivery': forms.CheckboxInput(),
            'active_receive_official_invoice': forms.CheckboxInput(),
            'active_slider_in_main_page': forms.CheckboxInput(),
            'active_banner_in_main_page': forms.CheckboxInput(),
            'active_categories_in_main_page': forms.CheckboxInput(),
            'active_newset_peoduct_in_main_page': forms.CheckboxInput(),
            'active_most_soled_product_in_main_page': forms.CheckboxInput(),
            'active_most_discount_in_main_page': forms.CheckboxInput(),
            'active_most_read_posts_in_main_page': forms.CheckboxInput(),
        }


class BannersModelForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        label='عکس',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ]
    )

    class Meta:
        model = Banners

        fields = '__all__'
        widgets = {

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'name2': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'link': forms.URLInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'checked': 'checked'
                }
            ),
        }


class SliderModelForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        label='عکس',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ]
    )

    class Meta:
        model = Slider
        fields = '__all__'
        widgets = {

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'name2': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'text': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'link': forms.URLInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'checked': 'checked'
                }
            ),
        }


class FastLinksModelForm(forms.ModelForm):
    class Meta:
        model = FastLinks
        fields = '__all__'


class QuestionAndAnswerModelForm(forms.ModelForm):
    class Meta:
        model = QuestionAndAnswer
        fields = '__all__'
