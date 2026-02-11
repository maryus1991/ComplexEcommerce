from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor_uploader.fields import RichTextUploadingField
from stores.models import Store
from django.utils.crypto import get_random_string
from easy_thumbnails.fields import ThumbnailerImageField


def photo_path_upload_to(*args, **kwargs):
    return f"images/slider/{get_random_string(100)}"


class SiteSetting(models.Model):
    title = models.CharField(max_length=100, default="0", verbose_name="عنوان سایت")
    tax = models.FloatField(default=1, verbose_name="مالیات زیر ساخت")
    min_payment = models.PositiveBigIntegerField(default=1000, verbose_name="حداقل مبلغ سبد خرید")
    number_or_rounding = models.PositiveBigIntegerField(default=1000 , verbose_name="عدد تقسیم برای معادله روند کردن (۱ برای غیر فعال سازی روند کردن)")
    minute_for_clean_order_detail_product = models.PositiveBigIntegerField(default=15, verbose_name="(دقیقه)برای پاک کردن محصول از سبد خرید")
    minute_for_clean_order_submitted_detail_product = models.PositiveBigIntegerField(default=120, verbose_name="حداکثر زمان برای حذف کلیه محصولات از سبد خرید (دقیقه)")
    copy_right_text = models.CharField(
        max_length=250, default="0", verbose_name="متن کپی رایت سایت"
    )
    address = models.CharField(max_length=500, default="0", verbose_name="ادرس")
    phone = PhoneNumberField(default="0111111111", verbose_name="شماره اول")
    phone2 = PhoneNumberField(default="0111111111", verbose_name="شماره دوم")
    email = models.EmailField(default="test@test.test", verbose_name="ایمیل")
    


    message_from_admin = models.TextField(null=True, blank=True, verbose_name=' (ممکن به دلیل سیاست کش از ۱۰ دقیقه الی یک ساعت دیگر نمایش داده شود   ) پیام ادمین در صفحه اصلی')
    background_color_message_of_admin = models.CharField(max_length=255, default='rgba(1,174,0,0.45)', verbose_name=' (به انگلیسی یا RGB ان رنگ نوشته شود) رنگ پس زمینه پیام ادمین')
    color_message_of_admin = models.CharField(max_length=255, default='white', verbose_name=' (به انگلیسی یا RGB ان رنگ نوشته شود) رنگ متن پیام ادمین')
    link_of_message = models.URLField( null=True, blank=True , verbose_name=' (می تواند خالی باشد) لینک پیام ادمین')
    the_message_for_all_or_just_not_auth_users = models.BooleanField(verbose_name='فعال بودن این گزینه برای همه کاربران پیام نمایش میده و غیر فعال بودن برای کاربران وارد نشده', default=False) # true for all users else just for none auth users



    telegram_link = models.URLField(default="0", verbose_name="لینک تلگرام")
    telegram_ID = models.CharField(
        max_length=100, default="0", verbose_name="ایدی تلگرام"
    )

    instagram_link = models.URLField(default="0", verbose_name="لینک حساب اینستاگرام")
    instagram_ID = models.CharField(
        max_length=100, default="0", verbose_name="ایدی اینستاگرام"
    )

    logo = ThumbnailerImageField(
        upload_to="site/logo/", null=True, verbose_name="لوگو", blank=True
    )
    short_description = models.TextField(default="0", verbose_name="توضیحات کوتاه")

    long_description = RichTextUploadingField(
        default="0", verbose_name="توضیحات طولانی"
    )

    about_image = ThumbnailerImageField(
        upload_to="site/about_image/", null=True, verbose_name="عکس معرفی", blank=True
    )

    # delivery options for all website
    active_post_delivery = models.BooleanField(
        default=True, verbose_name="فعال کردن  ارسال با پست برای فروشگاها"
    )
    active_freight_delivery = models.BooleanField(
        default=True, verbose_name="فعال کردن  ارسال با باربری (پس کرایه)"
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
    active_email_account_verified = models.BooleanField(
        default=False,verbose_name="اجازه به فعال سازی حساب با ایمیل"
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

    # product default order in product list page
    product_sort_by_count = models.BooleanField(
        default=True, verbose_name="بیشترین تعداد"
    )
    product_sort_by_highest_price = models.BooleanField(
        default=True, verbose_name="بیشترین قیمت"
    )
    product_sort_by_lowest_price = models.BooleanField(
        default=True, verbose_name='کمترین قیمت'
    )
    product_sort_by_sort_number = models.BooleanField(
        default=True, verbose_name="ترتیب انتخابی"
    )
    product_sort_by_category_sort_number = models.BooleanField(
        default=True, verbose_name=" اولویت ترتیب دسته بندی ها"
    )
    product_sort_by_brand_sort_number = models.BooleanField(
        default=True, verbose_name='	اولویت ترتیب برند ها	'
    )
    product_sort_by_existing_count = models.BooleanField(
        default=True, verbose_name="اولویت با محصولات موجود"
    )

    zero_the_count_of_all_product = models.BooleanField(
        default=False, verbose_name="صفر کردن موجودی تمام محصولات سایت"
    )


    def __str__(self):
        return self.title


class FastLinks(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=100)
    link = models.URLField(
        verbose_name="لینک",
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال یا غیر فعال")
    sort_number = models.PositiveIntegerField(default=0, verbose_name='ترتیب بندی')

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    phone_number = PhoneNumberField()

    def __str__(self):
        return str(self.phone_number).replace(' ','')


class SendMessageHistory(models.Model):
    phone_numbers = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    news_letter = models.BooleanField(default=True)


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
    image = ThumbnailerImageField(upload_to=photo_path_upload_to, verbose_name="عکس")
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
    image = ThumbnailerImageField(upload_to=photo_path_upload_to, verbose_name="عکس")
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
