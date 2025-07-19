from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor_uploader.fields import RichTextUploadingField

from django.utils.crypto import get_random_string


def photo_path_upload_to(*args, **kwargs):
    return f"images/slider/{get_random_string(100)}"


class SiteSetting(models.Model):
    title = models.CharField(max_length=100, default="0", verbose_name="عنوان سایت")
    tax = models.FloatField(default=1, verbose_name="مالیات زیر ساخت")
    min_payment = models.PositiveBigIntegerField(default=1000, verbose_name="حداقل مبلغ سبد خرید")
    minute_for_clean_order_detail_product = models.PositiveBigIntegerField(default=15, verbose_name="(دقیقه)برای پاک کردن محصول از سبد خرید")
    copy_right_text = models.CharField(
        max_length=250, default="0", verbose_name="متن کپی رایت سایت"
    )
    address = models.CharField(max_length=500, default="0", verbose_name="ادرس")
    phone = PhoneNumberField(default="0111111111", verbose_name="شماره اول")
    phone2 = PhoneNumberField(default="0111111111", verbose_name="شماره دوم")
    email = models.EmailField(default="test@test.test", verbose_name="ایمیل")

    telegram_link = models.URLField(default="0", verbose_name="لینک تلگرام")
    telegram_ID = models.CharField(
        max_length=100, default="0", verbose_name="ایدی تلگرام"
    )

    instagram_link = models.URLField(default="0", verbose_name="لینک حساب اینستاگرام")
    instagram_ID = models.CharField(
        max_length=100, default="0", verbose_name="ایدی اینستاگرام"
    )

    logo = models.ImageField(
        upload_to="site/logo/", null=True, verbose_name="لوگو", blank=True
    )
    short_description = models.TextField(default="0", verbose_name="توضیحات کوتاه")

    long_description = RichTextUploadingField(
        default="0", verbose_name="توضیحات طولانی"
    )

    about_image = models.ImageField(
        upload_to="site/about_image/", null=True, verbose_name="عکس معرفی", blank=True
    )
    difference_between_post_and_tipax_price = models.PositiveBigIntegerField(default=10,
               verbose_name='درصد اختلاف تیپاکس و پست')

    # delivery options for all website
    active_post_delivery = models.BooleanField(
        default=True, verbose_name="فعال کردن  ارسال با پست برای فروشگاها"
    )
    active_tipax_delivery = models.BooleanField(
        default=True, verbose_name="فعال کردن ارسال با تپاکس برای فروشگاها"
    )
    active_in_same_city_delivery = models.BooleanField(
        default=True, verbose_name="فعال کردن ارسال درون شهری برای فروشگاها"
    )
    active_physical_delivery = models.BooleanField(
        default=True, verbose_name="فعال کردن تحویل فیزیکی برای فروشگاها"
    )
    active_receive_official_invoice = models.BooleanField(
        default=True, verbose_name="فعال کردن دریافت فاکتور رسمی"
    )

    # main page setting
    active_slider_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن اسلایدر ها در صفحه اصلی"
    )
    active_banner_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن بنر ها در صفحه اصلی"
    )
    active_fast_links_in_footer_page = models.BooleanField(
        default=True, verbose_name="فعال کردن  لینک های سریع در پایین صفحه"
    )
    active_categories_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن محبوب ترین دسته ها در صفحه اصلی"
    )
    active_brands_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن محبوب ترین برندها در صفحه اصلی"
    )
    active_blog_categories_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن محبوب ترین دسته های مطالب خواندی در صفحه اصلی"
    )
    active_newset_peoduct_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن جدیدترین محصولات در صفحه اصلی"
    )
    active_most_soled_product_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن محصولات پر فروش  در صفحه اصلی"
    )
    active_most_discount_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن بیشترین تخفیف ها در صفحه اصلی"
    )
    active_most_read_posts_in_main_page = models.BooleanField(
        default=True, verbose_name="فعال کردن مطالب خواندنی در صفحه اصلی"
    )
    active_google_reCAPTCHA = models.BooleanField(
        default=True, verbose_name="فعال کردن افزونه ضد ربات گوگل google reCAPTCHA v3"
    )

    # user login setting
    force_user_to_verify_with_message = models.BooleanField(
        default=True, verbose_name="اجبار کاربران برای تایید حساب با ارسال پیامک"
    )
    force_users_to_login_for_download_apps = models.BooleanField(
        default=True,verbose_name='اجبار کاربران برای ورود به سایت جهت دانلود برنامه ها'
    )
    store_users_staff_logins = models.BooleanField(
        default=True, verbose_name="ورود کارمندان فروشگاها"
    )
    legal_users_login = models.BooleanField(
        default=True, verbose_name="ورود افراد رسمی"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال کردن ورود به سایت و فعال کردن تنظیمات سایت فعلی",
    )
    active_store_page = models.BooleanField(
        default=True, verbose_name="فعال کردن قسمت فروشگاه"
    )

    # payment setting
    active_zarinpal_payment = models.BooleanField(
        default=True, verbose_name="فعال کردن درگاه پرداخت زرین پال"
    )

    # send message
    send_message_response_to_ticket = models.BooleanField(
        default=False, verbose_name="ارسال پیامک زمان پاسخ به تیکت"
    )
    send_message_successful_payment = models.BooleanField(
        default=False, verbose_name="ارسال پیام هنگام پرداخت موفق"
    )
    send_message_official_invoice_upload = models.BooleanField(
        default=True, verbose_name="ارسال پیام هنگام اپلود فاکتور رسمی"
    )
    send_message_when_set_sending_id = models.BooleanField(
        default=True, verbose_name="ارسال پیام هنگام قرار دادن کد پیگیری ارسال"
    )

    def __str__(self):
        return self.title


class FastLinks(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=100)
    link = models.URLField(
        verbose_name="لینک",
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال یا غیر فعال")
    sort_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    phone_number = PhoneNumberField()

    def __str__(self):
        return str(self.phone_number).replace(' ','')


class QuestionAndAnswer(models.Model):
    question = models.TextField(verbose_name="سوال")
    answer = models.TextField(verbose_name="جواب")

    is_active = models.BooleanField(default=True, verbose_name="فعال یا غیر فعال")

    def __str__(self):
        return self.question


class ContactUs(models.Model):
    subject = models.CharField(max_length=100)
    email = models.EmailField()
    phone = PhoneNumberField()
    message = models.TextField()
    admin_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.email} - {self.phone}"


class Slider(models.Model):
    image = models.ImageField(upload_to=photo_path_upload_to, verbose_name="عکس")
    name = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="عنوان اول"
    )
    name2 = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="عنوان دوم"
    )
    text = models.CharField(max_length=250, null=True, blank=True, verbose_name="متن")
    link = models.URLField(verbose_name="لینک")
    is_active = models.BooleanField(
        default=True, null=True, blank=True, verbose_name="فعال یا فعال نبودن"
    )
    only_show_on_phone = models.BooleanField(default=True, verbose_name="مخصوص نمایش در گوشی")

    def __str__(self):
        return f"{self.id}"


class SiteLaw(models.Model):
    name = models.CharField(verbose_name="نام قانون", max_length=250)
    description = RichTextUploadingField(
         verbose_name="توضیحات "
    )
    is_active = models.BooleanField(
        default=True,
    )
    sort_number = models.IntegerField(default=0)


class Banners(models.Model):
    image = models.ImageField(upload_to=photo_path_upload_to, verbose_name="عکس")
    name = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="عنوان اول"
    )
    name2 = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="عنوان دوم"
    )
    link = models.URLField(verbose_name="لینک")
    is_active = models.BooleanField(default=True, verbose_name="فعال یا فعال نبودن")
    only_show_on_phone = models.BooleanField(default=True, verbose_name="مخصوص نمایش در گوشی")

    def __str__(self):
        return f"{self.id}"
