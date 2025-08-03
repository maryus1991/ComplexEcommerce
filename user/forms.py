from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.validators import validate_phonenumber


class RegistrationForm(forms.Form):


    phone_number = PhoneNumberField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "شماره همراه",
                "autocomplete": "tel",
                "dir": "rtl",
            }
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "ایمیل ( اختیاری )",
                "autocomplete": "email",
            }
        ),
        validators=[validate_email],
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3 ",
                "placeholder": "رمز عبور",
                "autocomplete": "password",
            }
        ),
    )

    conform_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "تایید رمز عبور",
            }
        ),
    )

    def clean_conform_password(self):
        conform_password = self.cleaned_data["conform_password"]
        password = self.cleaned_data.get("password")

        if password and password != conform_password:

            raise forms.ValidationError("رمز عبور شما به صورت یکسان وارد نشده است")
        else:
            return conform_password

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("رمز شما باید حداقل 8 کاراکتر باشد")

        if password.isdigit():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.isupper():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.islower():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        return password


    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        validate_phonenumber(phone_number)

        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sitesetting.models import SiteSetting
        from django_recaptcha import fields, widgets
        if SiteSetting.objects.first().active_google_reCAPTCHA:
            self.fields['recaptcha']=fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(action='signup'),
            )


class ForgotPasswordForm(forms.Form):
    phone_number = PhoneNumberField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "شماره همراه",
                "autocomplete": "tel",
                "dir": "rtl",
            }
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "ایمیل ( اختیاری )",
                "autocomplete": "email",
            }
        ),
        validators=[validate_email],
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3 ",
                "placeholder": "رمز عبور جدید",
                "autocomplete": "password",
            }
        ),
    )

    conform_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "تایید رمز عبور جدید",
            }
        ),
    )

    def clean_conform_password(self):
        conform_password = self.cleaned_data["conform_password"]
        password = self.cleaned_data.get("password")

        if password and password != conform_password:

            raise forms.ValidationError("رمز عبور شما به صورت یکسان وارد نشده است")
        else:
            return conform_password

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("رمز شما باید حداقل 8 کاراکتر باشد")

        if password.isdigit():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.isupper():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.islower():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        return password


    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        validate_phonenumber(phone_number)

        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sitesetting.models import SiteSetting
        from django_recaptcha import fields, widgets
        if SiteSetting.objects.first().active_google_reCAPTCHA:
            self.fields['recaptcha']=fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(action='signup'),
            )


class ForgotPasswordWithEmailForm(forms.Form):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "ایمیل",
                "autocomplete": "email",
            }
        ),
        validators=[validate_email],
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3 ",
                "placeholder": "رمز عبور جدید",
                "autocomplete": "password",
            }
        ),
    )

    conform_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "تایید رمز عبور جدید",
            }
        ),
    )

    def clean_conform_password(self):
        conform_password = self.cleaned_data["conform_password"]
        password = self.cleaned_data.get("password")

        if password and password != conform_password:

            raise forms.ValidationError("رمز عبور شما به صورت یکسان وارد نشده است")
        else:
            return conform_password

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("رمز شما باید حداقل 8 کاراکتر باشد")

        if password.isdigit():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.isupper():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.islower():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        return password


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sitesetting.models import SiteSetting
        from django_recaptcha import fields, widgets
        if SiteSetting.objects.first().active_google_reCAPTCHA:
            self.fields['recaptcha']=fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(action='signup'),
            )


class OTPForm(forms.Form):
    first_digit = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none digit-input",
                "maxlength": 1,
                "minlength": 1,
                "inputmode": "numeric",
                "pattern": "[0-9]",
                "placeholder": "1",
            },
        ),
        max_length=1,
        min_length=1,
    )
    second_digit = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none digit-input",
                "maxlength": 1,
                "minlength": 1,
                "inputmode": "numeric",
                "pattern": "[0-9]",
                "placeholder": "2",
            },
        ),
        max_length=1,
        min_length=1,
    )
    third_digit = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none digit-input",
                "maxlength": 1,
                "minlength": 1,
                "inputmode": "numeric",
                "pattern": "[0-9]",
                "placeholder": "3",
            },
        ),
        max_length=1,
        min_length=1,
    )
    forth_digit = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none digit-input",
                "maxlength": 1,
                "minlength": 1,
                "inputmode": "numeric",
                "pattern": "[0-9]",
                "placeholder": "4",
            },
        ),
        max_length=1,
        min_length=1,
    )

    def clean(self):
        first_digit = self.cleaned_data["first_digit"]
        second_digit = self.cleaned_data["second_digit"]
        third_digit = self.cleaned_data["third_digit"]
        forth_digit = self.cleaned_data["forth_digit"]

        if (
            first_digit.isdigit() and
                second_digit.isdigit() and
                third_digit.isdigit() and
                forth_digit.isdigit()
        ):
            first_digit, second_digit, third_digit, forth_digit = (
                int(first_digit),
                int(second_digit),
                int(third_digit),
                int(forth_digit),
            )
            if 9 < first_digit or second_digit or third_digit or forth_digit > 0:
                return self.cleaned_data

            else:
                raise forms.ValidationError("کد را به درستی وارد کنید")

        else:
            raise forms.ValidationError("کد را به درستی وارد کنید")


class ActiveAccountForm(forms.Form):
    """
    for activating account
    """

    phone_number = PhoneNumberField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "شماره همراه",
                "autocomplete": "tel",
                'dir':"rtl"
            }
        ),
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        validate_phonenumber(phone_number)
        return phone_number

class ActiveAccountFormWITHRecaptchaWithoutEmail(forms.Form):
    """
    for activating account
    """

    phone_number = PhoneNumberField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "شماره همراه",
                "autocomplete": "tel",
                'dir':"rtl"
            }
        ),
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        validate_phonenumber(phone_number)
        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sitesetting.models import SiteSetting
        from django_recaptcha import fields, widgets
        if SiteSetting.objects.first().active_google_reCAPTCHA:
            self.fields['recaptcha_field'] = fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(action='signup'),
            )



class ActiveAccountFormWithRecaptcha(forms.Form):
    """
    for activating account
    """

    phone_number = PhoneNumberField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "شماره همراه",
                "autocomplete": "tel",
                'dir':"rtl"
            }
        ),validators=[validate_phonenumber]
    )


    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "ایمیل",
                "autocomplete": "email",
            }
        ),
        validators=[validate_email],
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sitesetting.models import SiteSetting
        from django_recaptcha import fields, widgets
        if SiteSetting.objects.first().active_google_reCAPTCHA:
            self.fields['recaptcha'] = fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(action='signup'),
            )

class LoginForm(forms.Form):
    """
    Login form
    """

    phone_number = PhoneNumberField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "شماره همراه",
                "autocomplete": "tel",
                "dir": "rtl",
            }
        ),
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "رمز عبور",
                "autocomplete": "password",
            }
        ),
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        validate_phonenumber(phone_number)
        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sitesetting.models import SiteSetting
        from django_recaptcha import fields, widgets
        if SiteSetting.objects.first().active_google_reCAPTCHA:
            self.fields['recaptcha']=fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(action='login'),
            )


class LoginFormWithEmail(forms.Form):
    """
    Login form
    """

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "ایمیل",
                "autocomplete": "email",
            }
        ),
        validators=[validate_email],
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none bg-transparent w-full py-3",
                "placeholder": "رمز عبور",
                "autocomplete": "password",
            }
        ),
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        validate_phonenumber(phone_number)
        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sitesetting.models import SiteSetting
        from django_recaptcha import fields, widgets
        if SiteSetting.objects.first().active_google_reCAPTCHA:
            self.fields['recaptcha']=fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(action='login'),
            )


class EditUserInformationForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "tailwind-input",
                "placeholder": "  ایمیل ...",
            }
        ),
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input",
                "placeholder": "نام ...",
            }
        ),
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input",
                "placeholder": " نام خانوادگی ...",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        validate_email(email)
        return email


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "tailwind-input",
                "placeholder": "رمز عبور فعلی",
                "autocomplete": "password",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "tailwind-input",
                "placeholder": "رمز عبور جدید",
                "autocomplete": "password",
            }
        ),
    )

    conform_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "tailwind-input",
                "placeholder": "تایید رمز عبور جدید",
            }
        ),
    )

    def clean_conform_password(self):
        conform_password = self.cleaned_data["conform_password"]
        password = self.cleaned_data.get("password")

        if password and password != conform_password:
            raise forms.ValidationError("رمز عبور شما به صورت یکسان وارد نشده است")
        else:
            return conform_password

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("رمز شما باید حداقل 8 کاراکتر باشد")

        if password.isdigit():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.isupper():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.islower():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if not password.isalnum():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if not password.isascii():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        return password


class LegalPersonForm(forms.Form):
    legal_person_economic_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": " tailwind-input w-full py-3",
                "placeholder": "  شماره اقتصادی ...",
            }
        ),
    )
    legal_person_registration_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": " tailwind-input w-full py-3",
                "placeholder": "  کد ملی / شماره ثبت ...",
            }
        ),
    )
    legal_person_phone = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": " tailwind-input w-full py-3",
                "placeholder": "  شماره تماس / نمابر ...",
            }
        ),
    )
