from django import forms
from django.core.validators import (
    FileExtensionValidator,
    ValidationError,
    validate_email,
)
from dashboard.models import Ticket, TicketConversation
from multiupload.fields import MultiUploadMetaInput
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.validators import validate_phonenumber
from product.models import Product, ProductCategory, ProductBrand
from ckeditor_uploader.fields import RichTextUploadingFormField
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from blog.models import Blog, BlogCategory
from .models import Store, StoreApps
from .upload_multi_image import MultiImageField
from user.models import User
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from orders.models import Discount


class RegisterStoreMinimalInformationForm(forms.Form):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-6",
                "placeholder": "نام فروشگاه",
            }
        )

    )
    phone = PhoneNumberField(
        widget=forms.NumberInput(
            attrs={"class": "tailwind-input col-span-3 ",
                   "dir": "ltr",
                   "placeholder": "شماره همراه"}
        ),
        required=True,
        validators=[validate_phonenumber],
    )

    logo = forms.ImageField(
        required=True,
        label='لوگو',
        widget=forms.FileInput(
            attrs={"class": "absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10 ", "placeholder": "لوگو"}
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )
    about_image = forms.ImageField(
        required=True,
        label='عکس معرفی',
        widget=forms.FileInput(
            attrs={"class": "absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10", "placeholder": "تصویر معرفی"}
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )
    province = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-3",
                "placeholder": "استان محل فروشگاه",
            }
        ))
    card = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-3 number-input-tdc",
                "placeholder": "شماره کارت",
            }
        ))
    card_shaba = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-6 number-input-tdc",
                "placeholder": "شماره شبا",
            }
        ))
    card_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-3",
                "placeholder": "نام دارنده کارت",
            }
        ))

    economic_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-6 number-input-tdc",
                "placeholder": "شماره اقتصادی",
            }
        ))
    registration_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-6 number-input-tdc",
                "placeholder": "شماره ثبت",
            }
        ))
    official_invoice_phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input col-span-6 number-input-tdc",
                "placeholder": "نامبر / تلفن ثابت",
            }
        ))


class OrderFilteringForm(forms.Form):
    discount = forms.ModelChoiceField(
        queryset=Discount.objects.filter(is_active=True).all(),
        label="کد تخفیف استفاده",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "dir": "rtl",
            }
        ),
    )
    brands = forms.ModelChoiceField(
        queryset=ProductBrand.objects.filter(is_active=True).all(),
        label="جستجو در برند های محصولات ",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "dir": "rtl",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).all(),
        label="جستجو در دسته بندی محصولات ",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "dir": "rtl",
            }
        ),
    )

    address_search = forms.CharField(
        required=False,
        label="ادرس",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    product_search = forms.CharField(
        required=False,
        label="جستجوی محصول",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "نام محصولات رو با - جدا کنید",
            }
        ),
    )
    product_features_search = forms.CharField(
        required=False,
        label="جستجوی در ویژگی های محصول",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": " با - جدا کنید"}
        ),
    )
    product_tags_search = forms.CharField(
        required=False,
        label="جستجوی در تگ های محصول",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": " با - جدا کنید"}
        ),
    )
    user_phone_number = PhoneNumberField(
        required=False,
        label="شماره",
        widget=forms.NumberInput(attrs={"class": "form-control", "dir": "ltr"}),
    )

    sending_id = forms.CharField(
        required=False,
        label="کد پیگیری ارسال",
        widget=forms.TextInput(attrs={"class": "form-control number-input-tdc"}),
    )

    cart = forms.CharField(
        required=False,
        label="شماره کارت",
        widget=forms.TextInput(attrs={"class": "form-control "}),
    )
    payment_id = forms.CharField(
        required=False,
        label="کد پیگیری پرداخت",
        widget=forms.TextInput(attrs={"class": "form-control number-input-tdc" }),
    )

    start_date = JalaliDateField(
        required=False,
        label="از تاریخ ",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
                "placeholder": " تاریخ  باز شدن سفارش ",
            }
        ),
    )
    end_date = JalaliDateField(
        required=False,
        label="تا تاریخ (باز شدن سفارش)",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
                "placeholder": " تاریخ  باز شدن سفارش ",
            }
        ),
    )
    start_second_date = JalaliDateField(
        required=False,
        label="از تاریخ ",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
                "placeholder": " تاریخ پرداخت یا کنسل شدن سفارش ",
            }
        ),
    )
    end_second_date = JalaliDateField(
        required=False,
        label="تا تاریخ",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
                "placeholder": " تاریخ پرداخت یا کنسل شدن سفارش ",
            }
        ),
    )

    deliver_status = forms.ChoiceField(
        label="نحوه ارسال",
        choices=[
            ("", "همه"),
            ("11", "پست"),
            ("12", "تیپاکس"),
            ("21", "ارسال درون شهری"),
            ("22", "تحویل حضوری"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    payment_status = forms.ChoiceField(
        label="وضعیت پرداخت",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "پرداخت شده"),
            ("12", "درحال ارسال"),
            ("21", "تحویل شده"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    official_status = forms.ChoiceField(
        label="وضعیت کلی",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "کنسل شده"),
            ("12", "پرداخت شده"),
            ("21", "باز"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    invoice_status = forms.ChoiceField(
        label="وضعیت فاکتور",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "رسمی"),
            ("12", "غیر رسمی"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    invoice_status_ready_pdf = forms.ChoiceField(
        label="وضعیت فاکتور رسمی",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "فاکتور رسمی تحویل داده شده"),
            ("12", "فاکتور رسمی تحویل داده نشده"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    use_discount_code = forms.ChoiceField(
        label="وضعیت تخفیف",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "با تخفیف"),
            ("12", "بدون تخفیف"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    min_total_price = forms.IntegerField(
        required=False,
        label="کمترین قیمت کل",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    max_total_price = forms.IntegerField(
        required=False,
        label="بیشترین قیمت کل",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    min_total_weight = forms.IntegerField(
        required=False,
        label="کمترین وزن",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    max_total_weight = forms.IntegerField(
        required=False,
        label="بیشترین وزن",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    min_total_length = forms.IntegerField(
        required=False,
        label="کمترین ارتفاع",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    max_total_length = forms.IntegerField(
        required=False,
        label="بیشترین ارتفاع",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    min_total_width = forms.IntegerField(
        required=False,
        label="کمترین طول",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    max_total_width = forms.IntegerField(
        required=False,
        label="بیشترین طول",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    min_total_height = forms.IntegerField(
        required=False,
        label="کمترین عرض",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    max_total_height = forms.IntegerField(
        required=False,
        label="بیشترین عرض",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    min_discount_code_price = forms.IntegerField(
        required=False,
        label="کمترین قیمت تخفیف",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    max_discount_code_price = forms.IntegerField(
        required=False,
        label="بیشترین قیمت تخفیف",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    min_delivery_price = forms.IntegerField(
        required=False,
        label="کمترین قیمت ارسال",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    max_delivery_price = forms.IntegerField(
        required=False,
        label="بیشترین قیمت ارسال",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    min_count_of_product = forms.IntegerField(
        required=False,
        label="کمترین تعداد کالای درخواستی",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    max_count_of_product = forms.IntegerField(
        required=False,
        label="بیشترین تعداد کالای درخواستی",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        items = self.cleaned_data
        keys_to_remove = [
            key for key, value in items.items() if value is None or value == ""
        ]
        for key in keys_to_remove:
            items.pop(key)
        return items


class TicketFilterForm(forms.Form):
    subject = forms.CharField(
        required=False,
        label="جستوجو",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    store_name = forms.CharField(
        required=False,
        label="نام فروشگاه",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    user_name = forms.CharField(
        required=False,
        label="نام کاربر",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    user_number = PhoneNumberField(
        required=False,
        label="شماره کاربر",
        widget=forms.NumberInput(attrs={"class": "form-control", "dir": "ltr"}),
    )

    start_date = JalaliDateField(
        required=False,
        label="از تاریخ ",
        widget=AdminJalaliDateWidget(attrs={"class": "form-control", "dir": "rtl"}),
    )
    end_date = JalaliDateField(
        required=False,
        label="تا تاریخ",
        widget=AdminJalaliDateWidget(attrs={"class": "form-control", "dir": "rtl"}),
    )

    ticket_status = forms.ChoiceField(
        label="وضعیت",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "بسته"),
            ("12", "باز"),
            ("21", "خوانده نشده "),
            ("22", "خوانده شده"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    ticket_status_read_in_responder = forms.ChoiceField(
        label="وضعیت در دریافت کننده",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "خوانده شده توسط دریافت کننده"),
            ("12", "خوانده نشده توسط دریافت کننده"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    ordering = forms.ChoiceField(
        label="ترتیب بندی ",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "جدیدترین "),
            ("12", "قدیمی ترین"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean(self):
        items = self.cleaned_data
        keys_to_remove = [
            key for key, value in items.items() if value is None or value == ""
        ]
        for key in keys_to_remove:
            items.pop(key)
        return items


class ProductSearchForm(forms.Form):
    name = forms.CharField(
        label="جستجوی محصول",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    have_discount = forms.ChoiceField(
        label="دارای تخفیف",
        choices=[("", "-- انتخاب --"), ("1", "بله"), ("0", "خیر")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    ordering = forms.ChoiceField(
        label="ترتیب بندی بر اساس",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "بیشترین بازدید"),
            ("12", "کمترین بازدید"),
            ("21", "بیشترین قیمت"),
            ("22", "کمترین قیمت"),
            ("31", "بیشترین تعداد کامنت"),
            ("32", "کمترین  تعداد کامنت"),
            ("41", "بیشترین موجودی کالا"),
            ("42", "کمترین موجودی کالا"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_active = forms.ChoiceField(
        label="فعال / غیرفعال",
        choices=[("", "-- انتخاب --"), ("1", "فعال"), ("0", "غیرفعال")],
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
    admin_verify = forms.ChoiceField(
        label="تایید شده ادمین / تایید نشده ادمین ",
        choices=[("", "-- انتخاب --"), ("1", "تایید شده"), ("0", "تایید نشده")],
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
    discount_min = forms.IntegerField(
        label="حداقل تخفیف",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    discount_max = forms.IntegerField(
        label="حداکثر تخفیف",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).all(),
        label="دسته‌بندی",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
    )
    brand = forms.ModelChoiceField(
        queryset=ProductBrand.objects.filter(is_active=True).all(),
        label="برند",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
    )
    count_min = forms.IntegerField(
        label="حداقل تعداد",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    count_max = forms.IntegerField(
        label="حداکثر تعداد",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    weight_min = forms.IntegerField(
        label="حداقل وزن",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    weight_max = forms.IntegerField(
        label="حداکثر وزن",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    price_min = forms.IntegerField(
        label="حداقل قیمت",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    price_max = forms.IntegerField(
        label="حداکثر قیمت",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    height_min = forms.IntegerField(
        label="حداقل ارتفاع",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    height_max = forms.IntegerField(
        label="حداکثر ارتفاع",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    length_min = forms.IntegerField(
        label="حداقل طول",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    length_max = forms.IntegerField(
        label="حداکثر طول",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    width_min = forms.IntegerField(
        label="حداقل عرض",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    width_max = forms.IntegerField(
        label="حداکثر عرض",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    feature = forms.CharField(
        label="جستجو در ویژگی‌ها",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ایتم های مورد نظر را بنویسید و با - از هم جدا کنید",
            }
        ),
    )
    tag = forms.CharField(
        label="جستجو در تگ‌ها",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ایتم های مورد نظر را بنویسید و با - از هم جدا کنید",
            }
        ),
    )

    def clean(self):
        items = self.cleaned_data
        # Create a list of keys to remove first
        keys_to_remove = [
            key for key, value in items.items() if value is None or value == ""
        ]
        # Then remove them
        for key in keys_to_remove:
            items.pop(key)
        return items

    def clean_name(self):
        name = self.cleaned_data.get("name")

        if name is not None and name != "":
            return name
        else:
            return None


class BrandAndCategorySearchForm(forms.Form):
    name = forms.CharField(
        label="جستجوی",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    is_active = forms.ChoiceField(
        label="فعال / غیرفعال",
        choices=[("", "-- انتخاب --"), ("1", "فعال"), ("0", "غیرفعال")],
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
    ordering = forms.ChoiceField(
        label="ترتیب بندی بر اساس",
        choices=[
            ("", "-- انتخاب --"),
            ("41", "بیشترین تعداد کالا"),
            ("42", "کمترین تعداد کالا"),
            ("51", "جدید ترین"),
            ("52", "قدیمی ترین"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    category_parent = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).all(),
        label="دسته‌بندی مادر   ",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
    )

    def clean(self):
        items = self.cleaned_data
        # Create a list of keys to remove first
        keys_to_remove = [
            key for key, value in items.items() if value is None or value == ""
        ]
        # Then remove them
        for key in keys_to_remove:
            items.pop(key)
        return items


class AddProductForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=CKEditorUploadingWidget(attrs={'id': 'id_description'})
    )

    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).all(),
        required=True,
        empty_label="دسته بندی مربوطه را انتخاب کنید",
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden ": "true",
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
        required=False,
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
        required=False,
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
                attrs={"class": "form-control number-input", "placeholder": "قیمت"}
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


class AddBrandForm(forms.ModelForm):
    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={"placeholder": "تصویر لوگو"}),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    class Meta:
        model = ProductBrand
        fields = (
            "name",
            "image",
            "is_active",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"checked": "checked"}),
        }


class AddCategoryForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).all(),
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
        required=True,
        widget=forms.FileInput(attrs={"placeholder": "تصویر لوگو"}),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    class Meta:
        model = ProductCategory
        fields = ("name", "is_active", "image", "parent")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"checked": "checked"}),
        }


class AddStoreForm(forms.ModelForm):
    logo = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={"class": "form-control", "placeholder": "لوگو"}),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )
    about_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={"class": "form-control", "placeholder": "تصویر معرفی"}
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    phone = PhoneNumberField(
        widget=forms.NumberInput(
            attrs={"class": "form-control", 'dir':'ltr', "placeholder": "شماره همراه"}
        ),
        required=True,
        validators=[validate_phonenumber],
    )

    phone2 = PhoneNumberField(
        widget=forms.NumberInput(
            attrs={"class": "form-control", 'dir':'ltr', "placeholder": "شماره تلفن ثابت"}
        ),
        required=True,
        validators=[validate_phonenumber],
    )

    description = forms.CharField(
        widget=CKEditorUploadingWidget(attrs={'id': 'id_description'})
    )

    class Meta:
        model = Store

        fields = (
            "name",
            "phone",
            "phone2",
            "whats_app_ID",
            "whats_app_link",
            "telegram_app_ID",
            "telegram_app_Link",
            "instagram_app_ID",
            "instagram_app_Link",
            "logo",
            "about_image",
            "is_active",
            "description",
            "orgin_city",
            "address",
            "zip_code",
            "province",
            "have_official_invoice",
            "official_invoice_price",
            "economic_number",
            "registration_number",
            "official_invoice_phone_number",
            "have_post_delivery",
            "have_tipax_delivery",
            "have_in_same_city_delivery",
            "have_physical_delivery",
            "in_same_city_delivery_price",
            "additional_price",
            "additional_tax",
            'card',
            'card_shaba',
            'card_name',
            'time_for_return_order_days',

        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام فروشگاه",
                }
            ),
            "card": forms.TextInput(
                attrs={
                    "class": "form-control number-input-tdc",
                    "placeholder": "شماره کارت",
                }
            ),
            "card_shaba": forms.TextInput(
                attrs={
                    "class": "form-control number-input-tdc",
                    "placeholder": "شبا کارت",
                }
            ),
            "card_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام دارنده کارت",
                }
            ),
            "whats_app_link": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "لینک واتساپ",
                    "type": "text",
                }
            ),
            "whats_app_ID": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "ای دی واتساپ"}
            ),
            "telegram_app_ID": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "ای دی تلگرام"}
            ),
            "telegram_app_Link": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "لینک تلگرام",
                    "type": "text",
                }
            ),
            "instagram_app_ID": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "ای دی اینستاگرام"}
            ),
            "instagram_app_Link": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "لینک اینستاگرام",
                    "type": "text",
                }
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "ادرس فرشگاه"}
            ),
            "zip_code": forms.TextInput(
                attrs={"class": "form-control number-input-tdc", "placeholder": "کد پستی فرشگاه"}
            ),
            "province": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "استان فرشگاه"}
            ),
            "orgin_city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": " شهر مبدا"}
            ),
            "is_active": forms.CheckboxInput(attrs={}),
            "have_post_delivery": forms.CheckboxInput(attrs={}),
            "have_tipax_delivery": forms.CheckboxInput(attrs={}),
            "have_in_same_city_delivery": forms.CheckboxInput(attrs={}),
            "have_physical_delivery": forms.CheckboxInput(attrs={}),
            "have_official_invoice": forms.CheckboxInput(attrs={}),
            "in_same_city_delivery_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "هزینه ارسال درون شهری"}
            ),
            "additional_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "هزینه اضافی"}
            ),
            "additional_tax": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "مالیات اضافی(درصد)"}
            ),
            "time_for_return_order_days": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "مالیات اضافی(درصد)"}
            ),
            "official_invoice_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "درصد برای صدور فاکتور رسمی"}
            ),
            "economic_number": forms.TextInput(
                attrs={"class": "form-control number-input-tdc", "placeholder": "شماره اقتصادی"}
            ),
            "registration_number": forms.TextInput(
                attrs={"class": "form-control number-input-tdc", "placeholder": "شماره ثبت"}
            ),
            "official_invoice_phone_number": forms.TextInput(
                attrs={
                    "class": "form-control number-input-tdc",
                    "placeholder": "شماره تلفن یا نامبر جهت صدور فاکتور رسمی",
                }
            ),
        }


class StoreSendTicketForm(forms.ModelForm):
    store = forms.ModelChoiceField(
        required=False,
        queryset=Store.objects.filter(is_active=True, is_verified=True).all(),
        widget=forms.Select(
            attrs={
                "class": "form-control select2 select2-hidden-accessible",
                "style": "width: 100%",
                "aria - hidden": "true",
                "tabindex": "-1",
                "dir": "rtl",
            }
        ),
        empty_label="لطفا فروشگاهی که می خوایید تیکت به ان ارسال شود را انتخاب کنید",
    )
    message_message = RichTextUploadingFormField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "متن تیکت ..."}
        ),
        config_name="default",
    )

    class Meta:
        model = Ticket
        fields = (
            "subject",
            "store",
            "message_message",
        )
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "عنوان را وارد کنید ... ",
                }
            )
        }


class AddStoreUserStaffForm(forms.ModelForm):
    """
    for create user staff for stores
    """

    class Meta:
        model = User
        fields = (
            "email",
            "PhoneNumber",
            "first_name",
            "last_name",
            "password",
            "is_store_admin",
        )

    is_store_admin = forms.BooleanField(required=False)

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "ایمیل ...",
                "autocomplete": "email",
            }
        ),
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "نام ..."}
        ),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "نام خانوادگی ..."}
        ),
    )
    PhoneNumber = PhoneNumberField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "شماره همراه",
                "autocomplete": "tel",
                "dir": "ltr",
            }
        ),
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "رمز عبور",
                "autocomplete": "password",
            }
        ),
    )

    conform_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "تایید رمز عبور",
            }
        ),
    )

    def clean_conform_password(self):
        conform_password = self.cleaned_data["conform_password"]
        password = self.cleaned_data.get("password")

        if password and conform_password:

            if password != conform_password:
                raise ValidationError("رمز عبور شما به صورت یکسان وارد نشده است")
            else:
                return conform_password

        else:
            return conform_password

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise ValidationError("رمز شما باید حداقل 8 کاراکتر باشد")

        if password.isdigit():
            raise ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.isupper():
            raise ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.islower():
            raise ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        return password

    def clean_email(self):
        email = self.cleaned_data["email"]
        validate_email(email)
        return email

    def clean_phone_number(self):
        PhoneNumber = self.cleaned_data["PhoneNumber"]
        validate_phonenumber(PhoneNumber)

        return PhoneNumber


class AddStoreAppForm(forms.ModelForm):
    """
    for upload apps for stores
    """


    class Meta:
        model = StoreApps
        fields = ("is_active", "name", 'short_description')
        widgets = {
            "is_active": forms.CheckboxInput(),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام را وارد کنید"}
            ),
            "short_description": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "توضیحات کوتاه ..."}
            ),


        }


class AddStoreBlogForm(forms.ModelForm):
    """
    for add blogs for stores
    """

    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={"class": "form-control", "placeholder": "تصویر "}
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )
    category = forms.ModelChoiceField(
        queryset=BlogCategory.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control select2 select2-hidden-accessible",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria - hidden": "true",
                "dir": "rtl",
            }
        ),
        empty_label="لطفا دسته بندی انتخاب کنید",
    )
    content = RichTextUploadingFormField()

    class Meta:
        model = Blog
        fields = ("title", "category", "content", "image")
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "عنوان را وارد کنید"}
            )
        }


class StoreBlogFilteringForm(forms.Form):
    user_number = PhoneNumberField(
        required=False,
        label="شماره کاربر نویسنده پست",
        widget=forms.NumberInput(attrs={"class": "form-control", "dir": "ltr"}),
    )

    start_date = JalaliDateField(
        required=False,
        label="از تاریخ انتشار",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
            }
        ),
    )

    end_date = JalaliDateField(
        required=False,
        label="تا تاریخ انتشار",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
            }
        ),
    )

    category = forms.ModelChoiceField(
        queryset=BlogCategory.objects.filter(is_active=True).all(),
        label="دسته بندی مورد استفاده",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "dir": "rtl",
            }
        ),
    )

    is_active = forms.ChoiceField(
        label="وضعیت",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "فعال"),
            ("12", "غیر فعال"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    admin_verified = forms.ChoiceField(
        label="تاییده ادمین",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "تایید شده"),
            ("12", "تایید نشده"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    ordering = forms.ChoiceField(
        label="ترتیب بندی",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "جدید ترین"),
            ("12", "قدیمی ترین"),
            ("21", "بیشترین بازدید"),
            ("22", "کمترین بازید"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    title = forms.CharField(
        required=False,
        label="جستجوی در متن",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        items = self.cleaned_data
        keys_to_remove = [
            key for key, value in items.items() if value is None or value == ""
        ]
        for key in keys_to_remove:
            items.pop(key)
        return items


class AddStoreBlogCategoryForm(forms.ModelForm):
    """
    for add blogs categories for stores
    """

    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={"class": "form-control", "placeholder": "تصویر "}
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
    )

    parent = forms.ModelChoiceField(
        queryset=BlogCategory.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control select2 select2-hidden-accessible",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria - hidden": "true",
                "dir": "rtl",
            }
        ),
        empty_label="دسته مادر یا دسته بالا دست را انتخاب کنید(این قسمت می تواند خالی باشد یا انتخاب نشود)",
        required=False,
    )

    class Meta:
        model = BlogCategory
        fields = (
            "name",
            "parent",
            "image",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام دسته را وارد کنید"}
            ),
        }


class StoreUsersStaffFilteringForm(forms.Form):
    user_PhoneNumber = PhoneNumberField(
        required=False,
        label="شماره کاربر ",
        widget=forms.NumberInput(attrs={"class": "form-control", "dir": "ltr"}),
    )

    user_email = forms.EmailField(
        required=False,
        label="ایمیل کاربر  ",
        widget=forms.EmailInput(attrs={"class": "form-control", "dir": "ltr"}),
    )

    user_name = forms.CharField(
        required=False,
        label="نام",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    user_is_store_admin = forms.ChoiceField(
        label="وضعیت ادمین بودن",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "ادمین میباشد"),
            ("12", "ادمین نمیباشد"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    user_verify_account = forms.ChoiceField(
        label="وضعیت تایید بودن حساب",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "تایید شده"),
            ("12", "تایید نشده"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    user_is_active = forms.ChoiceField(
        label="وضعیت فعال بودن حساب",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "فعال "),
            ("12", "غیر فعال"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    start_date_joined = JalaliDateField(
        required=False,
        label="از  (تاریخ ثبت نام)",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
            }
        ),
    )

    end_date_joined = JalaliDateField(
        required=False,
        label="تا  (تاریخ ثبت نام)",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
            }
        ),
    )

    start_last_login = JalaliDateField(
        required=False,
        label="از  (تاریخ اخرین ورود به سایت)",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
            }
        ),
    )

    end_last_login = JalaliDateField(
        required=False,
        label="تا  (تاریخ اخرین ورود به سایت)",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
            }
        ),
    )
