from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.generic import View, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, authenticate, get_user_model, login
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from utils.send_email_task import send_email_task
from utils.send_otp import send_message
from user.mixins.logins import CustomLoginRequiredMixin

from config import settings

from .forms import (
    LoginForm,
LoginFormWithEmail,
    RegistrationForm,
    OTPForm,
    ActiveAccountForm,
    ChangePasswordForm,
    EditUserInformationForm,
    LegalPersonForm,
)
from .forms import ActiveAccountForm as ChangeNumberForm
from sitesetting.models import SiteSetting

User = get_user_model()


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
        context = {"login_form": LoginForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        form = LoginForm(request.POST)

        phone_number = ''
        email = ''
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]

            # check the user
            user = User.objects.filter(PhoneNumber=phone_number)
            if user is not None:
                _user = authenticate(username=phone_number, password=password)
                if user.exists() and user.count() == 1:
                    user = user.first()
                    if user.check_password(password):
                        if user.is_active and user.is_verified and _user:
                            if user == _user:
                                site = self.site

                                if self.site :
                                    if site.is_active:
                                        login(request, user)
                                    elif not site.is_active:
                                        messages.warning(
                                            request, "ورود به سایت غیر فعال می باشد"
                                        )
                                        return redirect("/")
                                else:
                                    login(request, user)

                                messages.success(request, "خوش امدید")

                                if user.email is None or user.first_name is None or user.last_name is None :
                                    messages.warning(
                                        request,'لطفا ایمیل , نام و نام خانوادگی را وارد کنید'
                                    )
                                    return redirect("dashboard:account")

                                elif user.address.count() <= 0:
                                    messages.warning(
                                        request,'لطفا ادرس خود را وارد کنید'
                                    )
                                    return redirect("dashboard:create_address")

                                else:
                                    return redirect("product:list")
                            else:
                                messages.error(
                                    request,
                                    "مشکلی پیش امده است لطفا با پشتیبانی تماس حاصل فرمایید",
                                )
                        else:
                            messages.error(
                                request,
                                "کابر شما فعال نیست لطفا با پشتیبانی تماس بگیرید یا از قسمت فعال کردن حساب کاربری به فعال کردن حساب خود اقدام نمایید",
                            )

                    else:
                        messages.error(request, "کابری با این مشخصات پیدا نشد")
                else:
                    messages.error(request, "کاربر پیدا نشد")
            else:
                messages.error(request, "کابری با این مشخصات پیدا نشد")

        else:
            messages.error(
                request, form.errors.as_text()
            )

        if phone_number != '' :
            query =  f'?tel={str(phone_number).replace(" ", "")}'
        elif email != '':
            query =  f'?email={str(email).replace(" ", "")}'
        else :
            query=''

        return redirect(str(reverse("user:login")) + query  )


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
        context = {'login_form_with_email': LoginFormWithEmail()}
        return render(request, self.template_name, context)

    def post(self, request):

        email_form = LoginFormWithEmail(request.POST)


        phone_number = ''
        email = ''


        if email_form.is_valid():
            email = email_form.cleaned_data["email"]
            password = email_form.cleaned_data["password"]

            # check the user
            user = User.objects.filter(email=email)
            if user is not None :
                if user.exists() and user.count() == 1:
                    user = user.first()

                    if user.check_password(password):
                        if user.is_active and user.is_verified:

                            if user.email_verified:
                                site = self.site

                                if self.site:
                                    if site.is_active:
                                        login(request, user)
                                    elif not site.is_active:
                                        messages.warning(
                                            request, "ورود به سایت غیر فعال می باشد"
                                        )
                                        return redirect("/")
                                else:
                                    login(request, user)

                                messages.success(request, "خوش امدید")

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
                                    "شما ایمیل حسابتان را فعال نکردید اول ان را فعال و سپس وارد سایت نمایید",
                                )
                        else:
                            messages.error(
                                request,
                                "کابر شما فعال نیست لطفا با پشتیبانی تماس بگیرید یا از قسمت فعال کردن حساب کاربری به فعال کردن حساب خود اقدام نمایید",
                            )

                    else:
                        messages.error(request, "کابری با این مشخصات پیدا نشد")
                else:
                    messages.error(request, "کاربر پیدا نشد")
            else:
                messages.error(request, "کابری با این مشخصات پیدا نشد")



        else:
            messages.error(
                request, email_form.errors.as_text()
            )

        if phone_number != '' :
            query =  f'?tel={str(phone_number).replace(" ", "")}'
        elif email != '':
            query =  f'?email={str(email).replace(" ", "")}'
        else :
            query=''

        return redirect(str(reverse("user:login")) + query  )


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, "با موفقیت از سایت خارج شدید")
        return redirect("user:login")


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
        if request.user.is_authenticated:
            logout(request)
        return render(request, self.template_name, {"form": self.form_class})

    def post(self, request):
        form = self.form_class(request.POST or None)
        phone_number = ''
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

                user.email = email
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

                    if not user.email_verified:
                        send_email_task.delay(
                            'تایید ایمیل حساب کاربری'
                            , 'با سلام لطفا با ورود به لینک زیر ورود به سایت یا ایمیل را فعال نمایید'
                            ,user.email
                        )
                        messages.success(
                            request, 'برای شما ایمیل فعال سازی جهت ورود با ایمیل ارسال شد'
                        )

                    return redirect("user:otp")
                else:
                    messages.warning(
                        request,'ثبت نام شما انجام شده است ولی ورود به سایت غیر فعال می باشد'
                    )
                    return redirect("/")

            else:
                messages.error(request, "کاربری با این شماره موجود میباشد")

                if phone_number != '':
                    query = f'?tel={str(phone_number).replace(" ", "")}'
                else:
                    query = ''

                return redirect(reverse("user:login") + query)

        else:
            messages.error(
                request,
                form.errors.as_text(),
                # 'لطفا اطلاعات را به درستی وارد کنید رمز عبور شما باید 8 کاراکتر باشد و دارای حروف انگلیسی اعداد و حد اقل باید درای یک حرف به صورت کپیتال و یک کاراکتر ویژه باشد'
            )

            return render(request, self.template_name, {"form": self.form_class(request.POST or None)})


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
                        user.is_verified = True
                        user.save()

                        messages.success(request, "حساب شما با موفقیت تایید شد")

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
        if request.user.is_authenticated:
            logout(request)
        return render(
            request, "auth/forgot-password.html", {"form": RegistrationForm()}
        )

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        phone_number = ''
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]

            user = User.objects.filter(PhoneNumber=phone_number)
            if user.exists() and user.count() == 1:
                user = user.first()
                if not user.check_password(password):
                    user.is_verified = False
                    user.set_password(password)
                    user.set_otp()
                    user.save()

                    send_message.delay(
                        str(phone_number).replace(" ", ""),
                        "کاربر گرامی بازیابی رمز عبور شما با موفقیت انجام گردید اگر شما این درخواست را ندادید لطفا با ورود به صفحه بازیابی رمز عبور  خود را تغییر دهید",
                    )

                    login(request, user)

                    messages.success(
                        request,
                        "رمز عبور شما با موفقیت تغییر یافت حال برای فعال شدن حساب خود کد ارسال به شماره خود را وارد کنید",
                    )
                    return redirect("user:otp")

                else:
                    messages.error(
                        request,
                        "رمز عبور شما با رمز عبور جدید شما یک سان هست لطفا وارد سایت شوید",
                    )

            else:
                messages.error(request, "کاربر مورد نظر موجود نیست")
                if phone_number != '' :
                    query =  f'?tel={str(phone_number).replace(" ", "")}'
                else :
                    query=''
                return redirect(reverse("user:register")+ query)
        else:
            messages.error(request, form.errors.as_text())

        return render(
            request, "auth/forgot-password.html", {"form": RegistrationForm(request.POST or None)}
        )



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
        context = {"login_form": ActiveAccountForm()}
        return render(request, "auth/active_account.html", context)

    def post(self, request, *args, **kwargs):
        form = ActiveAccountForm(request.POST or None)
        phone_number = ''
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            user = User.objects.filter(PhoneNumber=phone_number)
            if user.exists() and user.count() == 1:
                user = user.first()
                if user.is_active and user.is_verified:
                    messages.error(request, "حساب شما قبلا فعال شده است")
                elif user.is_verified is False:

                    login(request, user)

                    return redirect("user:otp")

                if user.is_active is False:
                    messages.error(
                        request,
                        "حساب شما بسته شده است لطفا با مسئول مربوطه تماس فرمایید",
                    )
                    if phone_number != '':
                        query = f'?tel={str(phone_number).replace(" ", "")}'
                    else:
                        query = ''
                    return redirect(reverse("user:login") + query)

            else:
                messages.error(
                    request,
                    "حساب شما پیدا نشد اگر مطمئن هستید که با این شماره حساب ساختید لطفا در قسمت تماس با ما با پشتیبانی در میان بزارید تا مشکل حل بشود",
                )
        else:
            messages.error(request, "لطفا اطلاعات معتبری وارد کنبد")

        if phone_number != '' :
            query =  f'?tel={str(phone_number).replace(" ", "")}'
        else :
            query = ''
        return redirect(reverse("user:login") + query)


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
                user.email = email
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
                    return redirect("product:list")

            else:
                messages.error(request, "این ایمیل قبلا استفاده شده است")

        else:
            messages.error(request, "لطفا در وارد کردن اطلاعات دقت فرمایید")
        return redirect("dashboard:account")


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
                return redirect("product:list")

        else:
            messages.error(request,form.errors.as_text())

        return redirect("dashboard:account")


class LegalPersonHelpText(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        messages.info(
            self.request,
            "برای ورود افراد حقیقی اول با ورود با شماره یا نامبر و تایید ان با وارد کردن پیامک ارسالی به ان شماره و سپس باید وارد قسمت پروفایل کاربری شده و در بخش اطلاعات حساب باید شماره اقتصادی و بقیه اطلاعلات را وارد کنید و بعد از این فرایند شما می توانید فاکتور رسمی دریافت کنید  ",
        )
        return reverse('user:login')


def e_namad(request):
    base_dir = settings.BASE_DIR
    file_path = f"{base_dir}/14545014.txt"
    try:
        with open(file_path, "rb") as file:
            response = HttpResponse(file.read(), content_type="text/plain")
            response["Content-Disposition"] = 'attachment; filename="14545014.txt"'
            return response
    except FileNotFoundError:
        return HttpResponse("File not found!", status=404)
