from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.generic import View, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, authenticate, get_user_model, login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from utils.send_otp import send_message
from user.mixins.logins import CustomLoginRequiredMixin

from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from .forms import (
    LoginForm,
    LoginFormWithEmail,
    RegistrationForm,
    OTPForm,
    ActiveAccountForm,
    ChangePasswordForm,
    EditUserInformationForm,
    LegalPersonForm,
    ActiveAccountFormWithRecaptcha,
    ForgotPasswordForm,
    ForgotPasswordWithEmailForm,
    RegistrationColleagueForm,
    LoginWithOTPPhoneNumber
)
from .forms import ActiveAccountForm as ChangeNumberForm
from sitesetting.models import SiteSetting

User = get_user_model()

@method_decorator(never_cache, name='dispatch')
class RegisterAsColleagueUser(View):
    """for register a specifics users that colleague to store"""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_verified:
            messages.info(request, "شما قبلا وارد شده اید")
            return redirect("dashboard:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = RegistrationColleagueForm(request.POST )
        
        return render(request, 'auth/colleague-user/colleague-user-register.html', {'form': form})

    def post(self, request):
        form = RegistrationColleagueForm(request.POST  or None, request.FILES or None)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            personal_id = form.cleaned_data.get('personal_id')
            store_address = form.cleaned_data.get('store_address')
            store_image = form.cleaned_data.get('store_image')
            phone_number = form.cleaned_data.get('phone_number')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            store = form.cleaned_data.get("colleague_with_store")


            user = User.objects.filter(Q(email=email) | Q(PhoneNumber=phone_number)| Q(colleague_id=personal_id))

            if user.exists():
                messages.error(
                    request, 'کاربری با این شماره یا ایمیل یا کد ملی قبلا ثیت نام شده است'
                )
                return render(request, 'auth/colleague-user/colleague-user-register.html', {'form': form})

            user = User.objects.create_user(
                phone_number,
                password,
                email if email else None,
                first_name=first_name,
                last_name=last_name,
                colleague_id=personal_id,
                store_address=store_address,
                store_image=store_image,
                colleague_request=True,
                is_active=True,
            )
            user.colleague_with_store.set(store)
            
            user.verify_email(request)
            site = SiteSetting.objects.first()

            if site and site.is_active:
                messages.success(
                    request,
                    'کاربر ساخته شد'
                )
                login(request, user)
                return redirect(reverse("user:otp"))

        else:
            messages.error(
                request,form.errors.as_text()
            )

        return render(request, 'auth/colleague-user/colleague-user-register.html', {'form': form})

@method_decorator(never_cache, name='dispatch')
class RegisterView(View):
    """
    Register user page
    """

    template_name = "auth/signup.html"
    form_class = RegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_verified:
            messages.info(request, "شما قبلا وارد شده اید")
            return redirect("dashboard:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class})

    def post(self, request):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.filter(PhoneNumber=phone_number)

            user_email = User.objects.filter(email=email)
            if user_email.exists():
                messages.error(
                    request, 'این ایمیل قبلا استفاده شده است'
                )
                return render(request, self.template_name, {"form": self.form_class(request.POST or None)})

            if not user.exists():
                User.objects.create_user(
                    is_active=True,
                    PhoneNumber=phone_number,
                    password=password,

                )

                user = User.objects.get(PhoneNumber=phone_number)

                if email:
                    user.email = email
                    user.save()
                    user.verify_email(request)
                    messages.success(request, 'ایمیل فعال سازی ارسال شد')

                user.save()

                messages.success(request, "کاربر با موفقیت ساخته شد")

                site = SiteSetting.objects.first()

                if site and not site.force_user_to_verify_with_message and site.is_active:
                    user.is_verified = True
                    user.message_verified = False
                    user.save()

                    if site.is_active:
                        login(request, user)

                    if user.email is None or user.first_name is None or user.last_name is None:
                        messages.warning(
                            request, 'لطفا ایمیل , نام و نام خانوادگی را وارد کنید'
                        )
                        return redirect("dashboard:account")

                    elif user.address.count() <= 0:
                        messages.warning(
                            request, 'لطفا ادرس خود را وارد کنید'
                        )
                        return redirect("dashboard:create_address")

                    else:
                        return redirect("product:list")

                if site and site.is_active:
                    login(request, user)

                    return redirect("user:otp")
                else:
                    messages.warning(
                        request, 'ثبت نام شما انجام شده است ولی ورود به سایت غیر فعال می باشد'
                    )
                    return redirect("/")

            else:
                messages.error(request, "کاربری با این شماره موجود میباشد")
                return render(request, self.template_name, {"form": self.form_class(request.POST or None)})


        else:
            messages.error(
                request,
                form.errors.as_text(),
            )

            return render(request, self.template_name, {"form": self.form_class(request.POST or None)})

@method_decorator(never_cache, name='dispatch')
class VerifyEmailWIthPrivateCode(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        private_code = kwargs.get('private_code')
        user = get_object_or_404(User, private_code=private_code)
        user.email_verified = True

        if SiteSetting.objects.first().active_email_account_verified:
            user.is_verified = True
        if user.phone_number_verified:
            user.is_verified = True
        user.private_code = None
        user.save()

        if user.is_verified:
            login(self.request, user)

        messages.success(
            self.request,
            'ایمیل شما فعال شد'
        )
        return reverse('product:list')

@method_decorator(never_cache, name='dispatch')
class LoginView(View):
    """
    login user page
    """

    template_name = "auth/login.html"

    def dispatch(self, request, *args, **kwargs):
        self.site = SiteSetting.objects.first()
        site = self.site

        if self.site and not site.is_active:
            messages.warning(request, "ورود به سایت غیر فعال می باشد")
            return redirect("/")

        if request.user.is_authenticated and request.user.is_verified:
            messages.info(request, "شما قبلا وارد شده اید")
            return redirect("dashboard:dashboard")

        if request.user.is_authenticated and request.user.is_active:

            if not request.user.is_verified:
                messages.info(
                    request,
                    "لطفا حساب خود را تایید کنید یک کد به شما ارسال شد لطفا انرا وارد کنید تا حساب شما تایید شود",
                )
                return redirect("user:otp")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"login_form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]

            user = User.objects.filter(PhoneNumber=phone_number)
            if not user.exists() or user.count() != 1:
                messages.error(request, 'کاربر پیدا نشد')
                return render(request, self.template_name, {"login_form": LoginForm(request.POST)})

            user = user.first()
            if not user.is_active:
                messages.error(request, 'حساب کاربری شما مسدود شده است لطفا با پشتیبانی تماس فرمایید')
                return render(request, self.template_name, {"login_form": LoginForm(request.POST)})

            if not user.is_verified or not user.phone_number_verified:
                messages.error(request, 'حساب کاربری شما نیاز به فعال سازی دارد')
                return render(request, self.template_name, {"login_form": LoginForm(request.POST)})

            if not user.check_password(password):
                messages.error(request, 'کاربر پیدا نشد')
                return render(request, self.template_name, {"login_form": LoginForm(request.POST)})

            login(request, user)
            messages.success(
                request, 'خوش امدید'
            )

            if user.email is None or user.first_name is None or user.last_name is None:
                messages.warning(
                    request, 'لطفا اطلاعات خود را تکمیل کنید'
                )
                return redirect("dashboard:account")

            elif user.address.count() <= 0:
                messages.warning(
                    request, 'لطفا ادرس خود را وارد کنید'
                )
                return redirect("dashboard:create_address")

            else:
                return redirect("product:list")

        else:
            messages.error(request, form.errors.as_text())
            return render(request, self.template_name, {"login_form": LoginForm(request.POST)})

@method_decorator(never_cache, name='dispatch')
class LoginWithEmailView(View):
    """
    login user page
    """

    template_name = "auth/login-with-email.html"

    def dispatch(self, request, *args, **kwargs):
        self.site = SiteSetting.objects.first()
        site = self.site

        if self.site and not site.is_active:
            messages.warning(request, "ورود به سایت غیر فعال می باشد")
            return redirect("/")

        if request.user.is_authenticated and request.user.is_verified:
            messages.info(request, "شما قبلا وارد شده اید")
            return redirect("dashboard:dashboard")

        if request.user.is_authenticated and request.user.is_active:

            if not request.user.is_verified:
                messages.info(
                    request,
                    "لطفا حساب خود را تایید کنید یک کد به شما ارسال شد لطفا انرا وارد کنید تا حساب شما تایید شود",
                )
                return redirect("user:otp")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'login_form_with_email': LoginFormWithEmail()})

    def post(self, request):
        email_form = LoginFormWithEmail(request.POST)
        if email_form.is_valid():
            email = email_form.cleaned_data["email"]
            password = email_form.cleaned_data["password"]

            user = User.objects.filter(email=email)
            if not user.exists() or user.count() != 1:
                messages.error(request, 'کاربر پیدا نشد')
                return render(request, self.template_name, {'login_form_with_email': LoginFormWithEmail(request.POST)})

            user = user.first()
            if not user.is_active:
                messages.error(request, 'حساب کاربری شما مسدود شده است لطفا با پشتیبانی تماس فرمایید')
                return render(request, self.template_name, {'login_form_with_email': LoginFormWithEmail(request.POST)})

            if not user.is_verified or not user.email_verified:
                messages.error(request, 'حساب کاربری شما نیاز به فعال سازی دارد')
                return render(request, self.template_name, {'login_form_with_email': LoginFormWithEmail(request.POST)})

            if not user.check_password(password):
                messages.error(request, 'کاربر پیدا نشد')
                return render(request, self.template_name, {'login_form_with_email': LoginFormWithEmail(request.POST)})

            login(request, user)
            messages.success(
                request, 'خوش امدید'
            )

            if user.email is None or user.first_name is None or user.last_name is None:
                messages.warning(
                    request, 'لطفا اطلاعات خود را تکمیل کنید'
                )
                return redirect("dashboard:account")

            elif user.address.count() <= 0:
                messages.warning(
                    request, 'لطفا ادرس خود را وارد کنید'
                )
                return redirect("dashboard:create_address")

            else:
                return redirect("product:list")

        else:
            messages.error(request, email_form.errors.as_text())
            return render(request, self.template_name, {'login_form_with_email': LoginFormWithEmail(request.POST)})

@method_decorator(never_cache, name='dispatch')
class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, "با موفقیت از سایت خارج شدید")
        return redirect("user:login")

@method_decorator(never_cache, name='dispatch')
class OTP(LoginRequiredMixin, View):
    template_name = "auth/confirmation-form.html"
    model = User
    form = OTPForm

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated and request.user.is_verified:
            messages.info(request, "حساب شما قبلا فعال شده است")
            return redirect("dashboard:dashboard")
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if (
                request.user.otp_expiry_date is None or
                request.user.otp_expiry_date <= timezone.now()
        ):
            print('12345')
            otp = request.user.set_otp()
            messages.success(request, "برای شما کد ارسال شد")

        time = request.user.otp_expiry_date - timezone.now()

        return render(
            request, self.template_name, {"form": self.form, "time": time.seconds}
        )

    def post(self, request):
        form = OTPForm(request.POST or None)
        if form.is_valid():
            user = request.user
            code = f'{form.cleaned_data.get("first_digit")}{form.cleaned_data.get("second_digit")}{form.cleaned_data.get("third_digit")}{form.cleaned_data.get("forth_digit")}'  # noqa
            if len(code) == 4 and code.isdigit():
                code = int(code)
                if 1000 < code < 9999:
                    if user.verify_otp(code):

                        user.phone_number_verified = True
                        user.is_verified = True

                        messages.success(request, "خوش آمدید")
                        user.save()

                        if user.email is None or user.first_name is None or user.last_name is None:
                            messages.warning(
                                request, 'لطفا ایمیل , نام و نام خانوادگی را وارد کنید'
                            )
                            return redirect("dashboard:account")

                        elif user.address.count() <= 0:
                            messages.warning(
                                request, 'لطفا ادرس خود را وارد کنید'
                            )
                            return redirect("dashboard:create_address")

                        else:
                            return redirect("product:list")

                    else:
                        messages.error(
                            request,
                            "مدت کد تمام شده لطفا درخواست ارسال کد مجدد کد بدهید",
                        )

        messages.error(request, "کد وارد شده اشتباه هست")
        return redirect("user:otp")

@method_decorator(never_cache, name='dispatch')
class ForgotPassword(View):
    """
    Forgot password page
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_verified:
            messages.info(
                request,
                "شما قبلا لاگین شده اید لطفا خارج بشید از سایت و دوباره وارد سایت بشید",
            )
            return redirect("dashboard:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(
            request, "auth/forgot-password.html", {"form": ForgotPasswordForm()}
        )

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST or None)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]

            user = User.objects.filter(PhoneNumber=phone_number)
            if not user.exists() or user.count() != 1:
                messages.error(request, "کاربر مورد نظر موجود نیست")
                return render(request, "auth/forgot-password.html", {"form": ForgotPasswordForm(request.POST or None)})

            user = user.first()

            if not user.is_active:
                messages.error(request, "حساب شما مسدود شده است")
                return render(request, "auth/forgot-password.html", {"form": ForgotPasswordForm(request.POST or None)})

            user.is_verified = False
            user.set_password(password)
            user.set_otp()
            user.save()

            send_message.delay(
                str(phone_number).replace(" ", ""),
                'ForgotPasswordNotify', str(phone_number).replace(" ", ""),
            )

            login(request, user)

            messages.success(
                request,
                "رمز عبور شما با موفقیت تغییر یافت حال برای فعال شدن حساب خود کد ارسال به شماره خود را وارد کنید",
            )
            return redirect("user:otp")

        else:
            messages.error(request, form.errors.as_text())

        return render(
            request, "auth/forgot-password.html", {"form": ForgotPasswordForm(request.POST or None)}
        )

@method_decorator(never_cache, name='dispatch')
class ForgotPasswordWithEmail(View):
    """
    Forgot password page
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_verified:
            messages.info(
                request,
                "شما قبلا لاگین شده اید لطفا خارج بشید از سایت و دوباره وارد سایت بشید",
            )
            return redirect("dashboard:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(
            request, "auth/forgot-password-with-email.html", {"form": ForgotPasswordWithEmailForm()}
        )

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordWithEmailForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.filter(email=email)

            if not user.exists() or user.count() != 1:
                messages.error(request, "کاربر مورد نظر موجود نیست")
                return render(request, "auth/forgot-password-with-email.html",
                              {"form": ForgotPasswordWithEmailForm(request.POST or None)})

            user = user.first()

            if not user.is_active:
                messages.error(request, "حساب شما مسدود شده است")
                return render(request, "auth/forgot-password-with-email.html",
                              {"form": ForgotPasswordWithEmailForm(request.POST or None)})

            user.is_verified = False
            user.set_password(password)
            user.save()

            user.verify_email(request)

            messages.success(
                request,
                "رمز عبور شما با موفقیت تغییر یافت حال برای فعال شدن حساب خود وارد لینک ارسال شده به ایمیل خود شوید",
            )
            return redirect("user:otp")

        else:
            messages.error(request, form.errors.as_text())

        return render(request, "auth/forgot-password-with-email.html",
                      {"form": ForgotPasswordWithEmailForm(request.POST or None)})

@method_decorator(never_cache, name='dispatch')
class ActiveAccount(View):
    """

    for active account

    """

    def dispatch(self, request, *args, **kwargs):
        if (
                request.user.is_authenticated and
                request.user.is_verified and
                request.user.is_active
        ):
            messages.info(request, "حساب شما قبلا فعال شده است")
            return redirect("dashboard:dashboard")
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {"login_form": ActiveAccountFormWithRecaptcha()}
        return render(request, "auth/active_account.html", context)

    def post(self, request, *args, **kwargs):
        form = ActiveAccountFormWithRecaptcha(request.POST or None)

        if form.is_valid():

            if phone_number := form.cleaned_data["phone_number"]:

                user = User.objects.filter(PhoneNumber=phone_number)
                if not user.exists():
                    messages.error(request, 'کاربر پیدا نشد')
                    return render(request, "auth/active_account.html",
                                  {"login_form": ActiveAccountFormWithRecaptcha(request.POST or None)})
                if user.count() != 1:
                    messages.error(request, 'کاربر پیدا نشد')
                    return render(request, "auth/active_account.html",
                                  {"login_form": ActiveAccountFormWithRecaptcha(request.POST or None)})

                user = user.first()

                if not user.is_active:
                    messages.error(request, 'کاربر شما فعال نمی باشد لطفا با پشتیبانی تماس فرمایید')
                    return redirect("user:login")

                if user.is_verified and user.phone_number_verified:
                    messages.error(request, 'حساب شما فعال می باشد')
                    return redirect("user:login")

                login(request, user)
                return redirect("user:otp")

            elif email := form.cleaned_data["email"]:
                user = User.objects.filter(email=email)
                if not user.exists():
                    messages.error(request, 'کاربر پیدا نشد')
                    return render(request, "auth/active_account.html",
                                  {"login_form": ActiveAccountFormWithRecaptcha(request.POST or None)})

                if user.count() != 1:
                    messages.error(request, 'کاربر پیدا نشد')
                    return render(request, "auth/active_account.html",
                                  {"login_form": ActiveAccountFormWithRecaptcha(request.POST or None)})

                user = user.first()

                if not user.is_active:
                    messages.error(request, 'کاربر شما فعال نمی باشد لطفا با پشتیبانی تماس فرمایید')
                    return redirect("user:login")

                if user.is_verified and user.email_verified:
                    messages.error(request, 'حساب شما فعال می باشد')
                    return redirect("user:login")

                user.verify_email(request)

                messages.success(
                    request,
                    'برای شما ایمیل فعال سازی ارسال شد '
                )
                return redirect("user:login")

        else:
            messages.error(request, form.errors.as_text())
            context = {"login_form": ActiveAccountFormWithRecaptcha(request.POST or None)}
            return render(request, "auth/active_account.html", context)

@method_decorator(never_cache, name='dispatch')
class LoginWithOTP(View):
    """

    for login with otp

    """
    def get(self, request):
        context = {"login_form": LoginWithOTPPhoneNumber(request.POST or None)}
        return render(request, "auth/login-with-otp.html", context)

    def post(self, request, *args, **kwargs):
        form = ActiveAccountFormWithRecaptcha(request.POST or None)

        if form.is_valid():

            if phone_number := form.cleaned_data["phone_number"]:

                user = User.objects.filter(PhoneNumber=phone_number)
                if not user.exists() or user.count() != 1:
                    messages.error(request, 'کاربر پیدا نشد لطفا ثبت نام فرمایید')
                    return self.get(request)

                user = user.first()

                if not user.is_active:
                    messages.error(request, 'حساب شما فعال نمی باشد لطفا با پشتیبانی تماس فرمایید')
                    return redirect("user:login")

                user.is_verified = False
                user.save()
                login(request, user)
                return redirect("user:otp")

            else:
                messages.error(request, "شماره پیدا نشد")
                context = {"login_form": LoginWithOTPPhoneNumber(request.POST or None)}
                return render(request, "auth/login-with-otp.html", context)

        else:
            messages.error(request, form.errors.as_text())
            context = {"login_form": LoginWithOTPPhoneNumber(request.POST or None)}
            return render(request, "auth/login-with-otp.html", context)

@method_decorator(never_cache, name='dispatch')
class EditUserInformation(CustomLoginRequiredMixin, View):
    """
    for edit user information
    """

    def post(self, request, *args, **kwargs):
        form = EditUserInformationForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")

            user = request.user

            if not User.objects.filter(email=email).exists():
                if email != user.email:
                    user.email_verified = False
                    user.email = email
                    user.save()
                    user.verify_email(request)
                    messages.success(
                        request,
                        'ایمیل فعال سازی برای شما ارسال شد'
                    )

                user.first_name = first_name
                user.last_name = last_name
                user.save()
                messages.success(request, "اطلاعات شما با موفقبت تغییر یافت")

                if user.email is None or user.first_name is None or user.last_name is None:
                    messages.warning(
                        request, 'لطفا ایمیل نام و نام خانوادگی را وارد کنید'
                    )
                    return redirect("dashboard:account")

                elif user.address.count() <= 0:
                    messages.warning(
                        request, 'لطفا ادرس خود را وارد کنید'
                    )
                    return redirect("dashboard:create_address")

                else:
                    return redirect("dashboard:orders")

            else:
                messages.error(request, "این ایمیل قبلا استفاده شده است")

        else:
            messages.error(request, "لطفا در وارد کردن اطلاعات دقت فرمایید")
        return redirect("dashboard:account")

@method_decorator(never_cache, name='dispatch')
class ChangePassword(CustomLoginRequiredMixin, View):
    """
    change password
    """

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST or None)
        if form.is_valid():
            current_password = form.cleaned_data.get("current_password")
            password = form.cleaned_data.get("password")
            user = request.user

            if user.check_password(current_password) and not user.check_password(
                    password
            ):
                user.set_password(password)
                user.save()

                messages.success(request, "رمز عبور شما با موقیت تغییر یافت")

                if user.email is None or user.first_name is None or user.last_name is None:
                    messages.warning(
                        request, 'لطفا ایمیل نام و نام خانوادگی را وارد کنید'
                    )
                    return redirect("dashboard:account")

                elif user.address.count() <= 0:
                    messages.warning(
                        request, 'لطفا ادرس خود را وارد کنید'
                    )
                    return redirect("dashboard:create_address")

                else:
                    return redirect("product:list")

            else:
                messages.error(request, "رمز عبور فعلی وارد شده اشتباه می باشد")

        else:
            messages.error(request, form.errors.as_text())
        return redirect("dashboard:account")

@method_decorator(never_cache, name='dispatch')
class ChangeNumber(CustomLoginRequiredMixin, View):
    """
    change number
    """

    def post(self, request, *args, **kwargs):
        form = ChangeNumberForm(request.POST or None)
        if form.is_valid():
            phone_number = form.cleaned_data.get("phone_number")
            user = request.user

            if not User.objects.filter(PhoneNumber=phone_number).exists():
                user.PhoneNumber = phone_number
                user.is_verified = False
                user.save()

                login(request, user)

                messages.success(request, "شماره شما با موفقیت تغییر یافت")

                return redirect("user:otp")

            else:
                messages.error(request, "این شماره قبلا استفاده شده است")

        else:
            messages.error(request, "لطفا در وارد کردن اطلاعات دقت فرمایید")
        return redirect("dashboard:account")

@method_decorator(never_cache, name='dispatch')
class ChangeLegalPersonInformation(CustomLoginRequiredMixin, View):
    """
    for change legal person information
    """

    def post(self, request, *args, **kwargs):
        form = LegalPersonForm(request.POST or None)
        if form.is_valid():
            legal_person_economic_number = form.cleaned_data.get(
                "legal_person_economic_number"
            )
            legal_person_registration_number = form.cleaned_data.get(
                "legal_person_registration_number"
            )
            legal_person_phone = form.cleaned_data.get("legal_person_phone")

            if (
                    not legal_person_economic_number.isdigit() or not legal_person_registration_number.isdigit()
            ):
                messages.error(request, "لطفا در وارد کردن اطلاعات دقت فرمایید")

                return redirect("dashboard:account")

            user = get_object_or_404(User, pk=request.user.id)
            user.legal_person = True
            user.legal_person_economic_number = legal_person_economic_number
            user.legal_person_registration_number = legal_person_registration_number
            user.legal_person_phone = legal_person_phone
            user.save()

            messages.success(request, "اطلاعات شما با موفقیت ثبت شد")

            if user.email is None or user.first_name is None or user.last_name is None:
                messages.warning(
                    request, 'لطفا ایمیل نام و نام خانوادگی را وارد کنید'
                )
                return redirect("dashboard:account")

            elif user.address.count() <= 0:
                messages.warning(
                    request, 'لطفا ادرس خود را وارد کنید'
                )
                return redirect("dashboard:create_address")

        else:
            messages.error(request, form.errors.as_text())

        return redirect("dashboard:account")

@method_decorator(never_cache, name='dispatch')
class LegalPersonHelpText(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        messages.info(
            self.request,
            "برای ورود افراد حقیقی اول با ورود با شماره یا نامبر و تایید ان با وارد کردن پیامک ارسالی به ان شماره و سپس باید وارد قسمت پروفایل کاربری شده و در بخش اطلاعات حساب باید شماره اقتصادی و بقیه اطلاعلات را وارد کنید و بعد از این فرایند شما می توانید فاکتور رسمی دریافت کنید  ",
        )
        return reverse('user:login')