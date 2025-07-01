from django import forms
from django.core.validators import FileExtensionValidator
from ckeditor_uploader.fields import RichTextUploadingFormField
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.validators import validate_phonenumber

from django.core.validators import EmailValidator, ValidationError
from sitesetting.models import (
    SiteSetting,
    Banners,
    Slider,
    FastLinks,
    QuestionAndAnswer,
    ContactUs,
)
from stores.forms import MultiImageField, MultiUploadMetaInput
from stores.models import StoreApps, Store
from blog.models import Blog, BlogCategory
from django.contrib.auth import get_user_model
from product.models import ProductBrand, ProductCategory, Product
from orders.models import Discount

from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

User = get_user_model()


# class MessagingUserForm(forms.Form):
#     user = forms.ModelMultipleChoiceField(
#         queryset=User.objects.all(),
#         required=False,
#         widget=forms.SelectMultiple(
#             attrs={
#                 'class': 'form-control select2',
#                 'style': 'width: 100%;',
#                 'tabindex': '-1',
#                 'aria-hidden': 'true',
#             }
#         )
#     )


class AddDiscountForm(forms.ModelForm):
    end_date_discount = JalaliDateField(
        required=False,
        label="تا تاریخ",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
                "placeholder": "تا تاریخ (محدودیت زمانی استفاده)",
            }
        ),
    )

    user = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden": "true",
            }
        ),
    )
    product = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden": "true",
                "dir": "rtl",
            }
        ),
    )
    store = forms.ModelMultipleChoiceField(
        queryset=Store.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden": "true",
                "dir": "rtl",
            }
        ),
    )

    class Meta:
        model = Discount
        exclude = ("order",)

        widgets = {
            "count": forms.NumberInput(attrs={"class": "form-control"}),
            "percentage_discount": forms.CheckboxInput(),
            "percent": forms.NumberInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "min_price": forms.NumberInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(),
        }


class AddProductForm(forms.ModelForm):
    description = RichTextUploadingFormField()
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        required=True,
        empty_label="فروشگاه مربوطه را انتخاب کنید",
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "placeholder": "فروشگاه",
                "dir": "rtl",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).all(),
        required=True,
        empty_label="دسته بندی مربوطه را انتخاب کنید",
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "placeholder": "درسته بندی",
            }
        ),
    )
    brand = forms.ModelChoiceField(
        queryset=ProductBrand.objects.filter(is_active=True).all(),
        required=True,
        empty_label="برند مربوطه را انتخاب کنید",
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "placeholder": "برند",
            }
        ),
    )

    picture = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={"class": "form-control", "placeholder": "تصویر اصلی"}
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    gallery = MultiImageField(
        required=True,
        max_num=10,
        min_num=0,
        widget=MultiUploadMetaInput(
            attrs={
                "class": "form-control",
            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    have_discount = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "type": "checkbox",
            }
        ),
    )

    features = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ویژگی های محصول را اضافه کنید ... ",
                "id": "id_features",
            }
        ),
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "تگ های محصول را اضافه کنید ... ",
                "id": "id_tags",
            }
        ),
    )
    specs = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "مشخصات محصول را اضافه کنید ... ",
                "id": "id_specs",
            }
        ),
    )

    class Meta:
        model = Product
        fields = (
            "name",
            "price",
            "description",
            "store",
            "category",
            "have_discount",
            "discount",
            "picture",
            "brand",
            "count",
            "weight",
            "tags",
            "features",
            "gallery",
            "length",
            "width",
            "height",
            "specs",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "عنوان"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "قیمت"}
            ),
            "length": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "ارتفاع"}
            ),
            "width": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "طول"}
            ),
            "height": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "عرض"}
            ),
            "discount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "تخفیف", "value": 0},
            ),
            "count": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "تعداد"}
            ),
            "weight": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "وزن (گرم)"}
            ),
        }


class AddUserModelForm(forms.ModelForm):
    PhoneNumber = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        validators=[validate_phonenumber],
    )
    store = forms.ModelChoiceField(
        required=False,
        queryset=Store.objects.all(),
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "dir": "rtl",
            }
        ),
        empty_label="فروشگاه را انتخاب کنید (می تواند خالی باشد و انتخاب نشود)",
    )

    conform_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "PhoneNumber",
            "store",
            "legal_person",
            "legal_person_economic_number",
            "is_active",
            "legal_person_registration_number",
            "is_superuser",
            "legal_person_phone",
            "is_verified",
            "is_store_admin",
            "is_staff",
            "message_verified",
        ]

        widgets = {
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "legal_person_economic_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "legal_person_registration_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "legal_person_phone": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(),
            "is_superuser": forms.CheckboxInput(),
            "is_verified": forms.CheckboxInput(),
            "is_store_admin": forms.CheckboxInput(),
            "is_staff": forms.CheckboxInput(),
            "legal_person": forms.CheckboxInput(),
            "message_verified": forms.CheckboxInput(),
        }


class SiteSettingModelForm(forms.ModelForm):
    logo = forms.ImageField(
        required=False,
        label="لوگو",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    about_image = forms.ImageField(
        required=False,
        label="تصویر معرفی",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    long_description = RichTextUploadingFormField()
    phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    phone2 = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = SiteSetting
        fields = "__all__"
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "tax": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "copy_right_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "telegram_link": forms.URLInput(attrs={"class": "form-control"}),
            "telegram_ID": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "instagram_link": forms.URLInput(attrs={"class": "form-control"}),
            "instagram_ID": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "short_description": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "is_active": forms.CheckboxInput(),
            "active_post_delivery": forms.CheckboxInput(),
            "active_tipax_delivery": forms.CheckboxInput(),
            "active_in_same_city_delivery": forms.CheckboxInput(),
            "active_physical_delivery": forms.CheckboxInput(),
            "active_receive_official_invoice": forms.CheckboxInput(),
            "active_slider_in_main_page": forms.CheckboxInput(),
            "active_banner_in_main_page": forms.CheckboxInput(),
            "active_categories_in_main_page": forms.CheckboxInput(),
            "active_newset_peoduct_in_main_page": forms.CheckboxInput(),
            "active_most_soled_product_in_main_page": forms.CheckboxInput(),
            "active_most_discount_in_main_page": forms.CheckboxInput(),
            "active_most_read_posts_in_main_page": forms.CheckboxInput(),
            "force_user_to_verify_with_message": forms.CheckboxInput(),
            "store_users_staff_logins": forms.CheckboxInput(),
            "legal_users_login": forms.CheckboxInput(),
            "active_store_page": forms.CheckboxInput(),
            "active_zarinpal_payment": forms.CheckboxInput(),
            "send_message_response_to_ticket": forms.CheckboxInput(),
            "send_message_successful_payment": forms.CheckboxInput(),
            "send_message_official_invoice_upload": forms.CheckboxInput(),
            "send_message_when_set_sending_id": forms.CheckboxInput(),
        }


class BannersModelForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        label="عکس",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    class Meta:
        model = Banners

        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "name2": forms.TextInput(attrs={"class": "form-control"}),
            "link": forms.URLInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"checked": "checked"}),
        }


class SliderModelForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        label="عکس",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    class Meta:
        model = Slider
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "name2": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.TextInput(attrs={"class": "form-control"}),
            "link": forms.URLInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"checked": "checked"}),
        }


class FastLinksModelForm(forms.ModelForm):
    class Meta:
        model = FastLinks
        fields = "__all__"

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "link": forms.URLInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(),
        }


class QuestionAndAnswerModelForm(forms.ModelForm):
    class Meta:
        model = QuestionAndAnswer
        fields = "__all__"
        widgets = {
            "question": forms.TextInput(attrs={"class": "form-control"}),
            "answer": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(),
        }


class UsedAppModelForm(forms.ModelForm):
    store = forms.ModelChoiceField(
        queryset=Store.objects.filter(is_active=True, is_verified=True).all(),
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
        empty_label="فروشگاه را انتخاب کنید",
    )

    class Meta:
        model = StoreApps
        fields = "__all__"

        widgets = {
            "is_active": forms.CheckboxInput(),
            "admin_verified": forms.CheckboxInput(),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام را وارد کنید"}
            ),
            "file": forms.ClearableFileInput(
                attrs={"class": "form-control", "placeholder": "برنامه را وارد کنید"}
            ),
        }


class AddBlogModelForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        label="نویسنده",
        queryset=get_user_model()
        .objects.filter(
            is_active=True, is_verified=True, is_staff=True, store__isnull=False
        )
        .all(),
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "dir": "ltr",
            }
        ),
        empty_label="نویسنده را انتخاب کنید",
    )

    store = forms.ModelChoiceField(
        label="فروشگاه منتشر کننده",
        queryset=Store.objects.filter(is_active=True, is_verified=True).all(),
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
        empty_label="فروشگاه را انتخاب کنید",
    )
    category = forms.ModelChoiceField(
        label="دسته",
        queryset=BlogCategory.objects.filter().all(),
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
        empty_label="دسته را انتخاب کنید",
    )

    content = RichTextUploadingFormField()

    image = forms.ImageField(
        label="عکس",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    class Meta:
        model = Blog
        fields = (
            "user",
            "title",
            "store",
            "category",
            "content",
            "image",
            "is_active",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "عنوان"}
            ),
            "is_active": forms.CheckboxInput(),
        }


class AddBlogCategoryModelForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=BlogCategory.objects.filter().all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
        empty_label="دسته مادر یا دسته بالا دست را انتخاب کنید(این قسمت می تواند خالی باشد یا انتخاب نشود)",
    )

    image = forms.ImageField(
        label="لوگو",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    class Meta:
        model = BlogCategory
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام"}
            ),
            "is_active": forms.CheckboxInput(),
        }
