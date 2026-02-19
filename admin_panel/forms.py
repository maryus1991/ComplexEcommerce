from django import forms
from django.core.validators import FileExtensionValidator
from ckeditor_uploader.fields import RichTextUploadingFormField
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.validators import validate_phonenumber

from sitesetting.models import (
    SiteSetting,
    Banners,
    Slider,
    FastLinks,
    QuestionAndAnswer,
    SiteLaw
)
from stores.forms import MultiImageField, MultiUploadMetaInput
from stores.models import StoreApps, Store
from blog.models import Blog, BlogCategory
from django.contrib.auth import get_user_model
from product.models import ProductBrand, ProductCategory, Product
from orders.models import Discount, SpecificsOrders, OrderDetail
from guarantee.models import ProductGuarantee, ActiveProductGuarantee

from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

User = get_user_model()

class GuaranteeModelForm(forms.ModelForm):

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden": "true",
                "dir": "rtl",
            }
        ),
        label='محصول'
    )
    class Meta:
        model = ProductGuarantee
        fields = '__all__'
        widgets = {
            'serial_number':forms.TextInput(attrs={'class':'form-control'}),
            'months_of_expire':forms.NumberInput(attrs={'class':'form-control'}),
            'name_of_garantee_company':forms.TextInput(attrs={'class':'form-control'}),
            'is_active':forms.CheckboxInput(),
        }

class ActiveGuaranteeModelForm(forms.ModelForm):
    guarantee = forms.ModelChoiceField(
        queryset=ProductGuarantee.objects.filter(is_active=True).all(),
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden": "true",
                "dir": "rtl",
            }
        ),
        label='گارانتی'
    )
    order = forms.ModelChoiceField(
        queryset=OrderDetail.objects.all(),
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden": "true",
                "dir": "rtl",
            }
        ),
        label='سفارش '
    )
    date_of_started = JalaliDateField(
        required=False,
        label="تاریخ شروع",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
            }
        ),
    )
    date_of_expire = JalaliDateField(
        required=False,
        label="تاریخ انقضا",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "form-control",
                "dir": "rtl",
            }
        ),
    )
    class Meta:
        model = ActiveProductGuarantee
        fields = '__all__'

        widgets = {
            'is_active':forms.CheckboxInput(),
        }

class StorePermissions(forms.ModelForm):
    class Meta:
        model = Store
        fields = (
            'can_stores_add_product_category',
            'can_stores_add_product_brand',
            'can_stores_add_product',
            'can_store_add_blog_category',
            'can_store_add_blog_post',
            'can_store_add_apps',
            'can_store_add_users',
            'allowed_to_add_and_edit_products_with_out_admin_per',
            'allowed_to_add_and_edit_apps_with_out_admin_per',
            'allowed_to_add_and_edit_posts_with_out_admin_per',
            'allowed_to_activate_product_categories_with_out_admin_per',
            'allowed_to_activate_product_brand_with_out_admin_per',
            'allowed_to_activate_post_categories_with_out_admin_per',
            'can_stores_add_colleague_user',
            'can_store_add_product_guarantee',
        )
        widgets = {
            'can_stores_add_product_category': forms.CheckboxInput(),
            'can_stores_add_product_brand': forms.CheckboxInput(),
            'can_stores_add_product': forms.CheckboxInput(),
            'can_store_add_blog_category': forms.CheckboxInput(),
            'can_store_add_blog_post': forms.CheckboxInput(),
            'can_store_add_apps': forms.CheckboxInput(),
            'can_store_add_users': forms.CheckboxInput(),
            'allowed_to_add_and_edit_products_with_out_admin_per': forms.CheckboxInput(),
            'allowed_to_add_and_edit_apps_with_out_admin_per': forms.CheckboxInput(),
            'allowed_to_add_and_edit_posts_with_out_admin_per': forms.CheckboxInput(),
            'allowed_to_activate_product_categories_with_out_admin_per': forms.CheckboxInput(),
            'allowed_to_activate_product_brand_with_out_admin_per': forms.CheckboxInput(),
            'allowed_to_activate_post_categories_with_out_admin_per': forms.CheckboxInput(),
            'can_stores_add_colleague_user': forms.CheckboxInput(),
            'can_store_add_product_guarantee': forms.CheckboxInput(),
        }

class AdminUsersFilteringForm(forms.Form):
    user_PhoneNumber = PhoneNumberField(
        required=False,
        label="شماره کاربر ",
        widget=forms.NumberInput(attrs={"class": "form-control", "dir": "ltr"}),
    )
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        label=' کاربران فروشگاه',
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria-hidden ": "true",
                "dir": "rtl",
            }
        ),
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
        label="وضعیت ادمین فروشگاهی بودن",
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
    message_verified = forms.ChoiceField(
        label="وضعیت  تایید شده با پیامک",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "تایید شده با پیامک"),
            ("12", "تایید نشده با پیامک"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    legal_person = forms.ChoiceField(
        label="وضعیت رسمی بودن",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "رسمی میباشد"),
            ("12", "رسمی نمیباشد"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_super_user = forms.ChoiceField(
        label="وضعیت ادمین سایت بودن",
        choices=[
            ("", "-- انتخاب --"),
            ("11", "ادمین میباشد"),
            ("12", "ادمین نمیباشد"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    legal_person_economic_number = forms.CharField(
        required=False,
        label="شماره اقتصادی (رسمی)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    legal_person_registration_number = forms.CharField(
        required=False,
        label="شماره ثبت (رسمی)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    legal_person_phone = forms.CharField(
        required=False,
        label="تلفن یا نامبر شخص (رسمی)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

class AdminOrderFilteringForm(forms.Form):
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
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        label='فروشگاه',
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
        widget=forms.TextInput(attrs={"class": "form-control number-input-tdc"}),
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
            ("23", " باربری (پس کرایه)"),
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

class AdminBlogFilteringForm(forms.Form):
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        label="فروشگاه",
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden": "true",
                "dir": "rtl",
            }
        ),
    )

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
            ("23", " اهمیت"),
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

class SpecificsOrdersModelForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden": "true",
            }
        ),
    )

    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        required=False,
        widget=forms.Select(
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
        model = SpecificsOrders
        fields = ('user', 'store', 'price', 'name')

        widgets = {
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }

class SiteLawModelForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditorUploadingWidget(attrs={'id': 'id_description'})
    )

    class Meta:
        model = SiteLaw
        fields = ('name', 'description', 'is_active')
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(),
        }

class MessagingUserForm(forms.Form):
    user = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'tabindex': '-1',
                'aria-hidden': 'true',

            }
        )
    )

    sender_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            'placeholder': 'شماره فرستنده ... ',
        }),
    )

    is_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    is_store_admin = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    message_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    not_message_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    legal_person = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    is_superuser = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )

    store = forms.ModelMultipleChoiceField(
        queryset=Store.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'tabindex': '-1',
                'aria-hidden': 'true',
                'dir': 'rtl'

            }
        )
    )
    store_is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    store_is_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'متن پیام ( سعی کنید که زیاد نباشد ) ...'
            }
        ),
    )

class ExcludeUserFromMessagingForm(forms.Form):
    exclude_user = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'tabindex': '-1',
                'aria-hidden': 'true',

            }
        )
    )

    exclude_is_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    exclude_is_store_admin = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    exclude_message_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    exclude_not_message_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    exclude_legal_person = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    exclude_is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    exclude_is_superuser = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    exclude_is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )

    exclude_store = forms.ModelMultipleChoiceField(
        queryset=Store.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'tabindex': '-1',
                'aria-hidden': 'true',
                'dir': 'rtl'

            }
        )
    )
    exclude_store_is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    exclude_store_is_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )

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
            "count_of_use_per_user": forms.NumberInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(),
        }

class AddProductForm(forms.ModelForm):
    description = RichTextUploadingFormField(
        required=False,
        widget=CKEditorUploadingWidget(attrs={'id': 'id_description'})
    )
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
        max_num=20,
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
            'sort_number',
            'sort_number_newest_products',
            'sort_number_most_sell',
            'sort_number_discount',
            'colleague_users_price',

        )
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "عنوان"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "قیمت"}
            ),
            "colleague_users_price": forms.NumberInput(
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
            "sort_number": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "ترتیب محصول در صفحه محصولات (0 تا 100,000,000)"}
            ),
            "sort_number_newest_products": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "ترتیب محصول در جدیدترین محصولات صفحه اصلی (0 تا 10)"}
            ),
            "sort_number_most_sell": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "ترتیب محصول در پرفروش ترین محصولات صفحه اصلی (0 تا 10)"}
            ),
            "sort_number_discount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "ترتیب محصول در بیشترین محصولات صفحه اصلی (0 تا 100)"}
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
                "class": 'form-control select2 ',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "dir": "rtl",
            }
        ),
        empty_label="فروشگاه کارمندی را انتخاب کنید (می تواند خالی باشد و انتخاب نشود)",
    )
    
    colleague_with_store = forms.ModelMultipleChoiceField(
        queryset=Store.objects.filter(can_stores_add_colleague_user=True, is_active=True, is_verified=True).all(),  
        help_text="فروشگاهی که با آن همکاری دارید را انتخاب کنید",
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": 'form-control select2 ',
                "style": "width: 100%; height:100px",
                "tabindex ": "-1",
                "aria - hidden ": "true",
                "dir": "rtl",
                
            }
        ),
    )



 
    store_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={"class": "form-control"}
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "heic"]
            )
        ],
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
    store_address = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    colleague_id = forms.CharField(
        required=False,
        widget=forms.NumberInput(
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
            'colleague_user',
            'colleague_request',
            'colleague_id',
            'store_address',
            'store_image',
            'colleague_with_store',
        ]

        widgets = {
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "legal_person_economic_number": forms.TextInput(
                attrs={"class": "form-control number-input-tdc"}
            ),
            "legal_person_registration_number": forms.TextInput(
                attrs={"class": "form-control number-input-tdc"}
            ),
            "legal_person_phone": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(),
            "is_superuser": forms.CheckboxInput(),
            "is_verified": forms.CheckboxInput(),
            "is_store_admin": forms.CheckboxInput(),
            "is_staff": forms.CheckboxInput(),
            "legal_person": forms.CheckboxInput(),
            "message_verified": forms.CheckboxInput(),
            "colleague_user": forms.CheckboxInput(),
            "colleague_request": forms.CheckboxInput(),
            
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

    long_description = forms.CharField(
        widget=CKEditorUploadingWidget(attrs={'id': 'id_description'})
    )

    description_for_guarantee_page = forms.CharField(
        widget=CKEditorUploadingWidget(attrs={'id': 'id_descriptionـguarantee'})
    )

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
    link_of_message = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
            }
        ),
        label='لینک پیام ادمین (اختیاری)'
    )

    message_from_admin = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=' (ممکن به دلیل سیاست کش از ۱۰ دقیقه الی یک ساعت دیگر نمایش داده شود   ) پیام ادمین در صفحه اصلی'
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
            ), "minute_for_clean_order_detail_product": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "min_payment": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "number_or_rounding": forms.NumberInput(

                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
            "difference_between_post_and_tipax_price": forms.NumberInput(
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

            "minute_for_clean_order_submitted_detail_product": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "background_color_message_of_admin": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "color_message_of_admin": forms.TextInput(
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
            "active_brands_in_main_page": forms.CheckboxInput(),
            "active_blog_categories_in_main_page": forms.CheckboxInput(),
            "active_fast_links_in_footer_page": forms.CheckboxInput(),
            "active_google_reCAPTCHA": forms.CheckboxInput(),
            "force_users_to_login_for_download_apps": forms.CheckboxInput(),
            "active_email_account_verified": forms.CheckboxInput(),
            'product_sort_by_count': forms.CheckboxInput(),
            'product_sort_by_highest_price': forms.CheckboxInput(),
            'product_sort_by_lowest_price': forms.CheckboxInput(),
            'product_sort_by_sort_number': forms.CheckboxInput(),
            'the_message_for_all_or_just_not_auth_users': forms.CheckboxInput(),
            'product_sort_by_category_sort_number': forms.CheckboxInput(),
            'product_sort_by_brand_sort_number': forms.CheckboxInput(),
            'product_sort_by_existing_count': forms.CheckboxInput(),
            'active_freight_delivery': forms.CheckboxInput(),
            'zero_the_count_of_all_product': forms.CheckboxInput(),
            'active_guarantee': forms.CheckboxInput(),
            'active_zarinpal': forms.CheckboxInput(),
            'active_zipal_payment': forms.CheckboxInput(),
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
            "only_show_on_phone": forms.CheckboxInput(),
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
            "only_show_on_phone": forms.CheckboxInput(),
        }

class FastLinksModelForm(forms.ModelForm):
    class Meta:
        model = FastLinks
        fields = "__all__"

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "sort_number": forms.NumberInput(attrs={"class": "form-control"}),
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
    short_description = RichTextUploadingFormField(
        required=False,
    )

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

    store = forms.ModelChoiceField(
        queryset=Store.objects.filter(is_active=True, is_verified=True).all(),
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex": "-1",
                "aria-hidden ": "true",
                'dir': 'rtl'
            }
        ),
        empty_label="فروشگاه را انتخاب کنید",
        required=False,
    )

    class Meta:
        model = StoreApps
        exclude = ('file',)

        widgets = {
            "is_active": forms.CheckboxInput(),
            "admin_verified": forms.CheckboxInput(),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام را وارد کنید"}
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
        fields = ('parent', 'image', 'name', 'is_active')
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام"}
            ),
            "is_active": forms.CheckboxInput(),
        }
