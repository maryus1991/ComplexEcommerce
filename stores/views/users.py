from django.views.generic import (
    ListView,
    FormView,
    UpdateView,
    RedirectView,
    View,
)
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    render,
    redirect,
)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from phonenumbers.phonenumber import PhoneNumber
from stores.models import Store
from django.utils.dateparse import parse_date
from stores.forms import (
    AddStoreUserStaffForm,
    StoreUsersStaffFilteringForm,
)
from auditlog.models import LogEntry
from user.mixins.logins import StoreAdminUserStaff
import jdatetime
from django.utils.dateparse import parse_date
from utils.tipax_price_calc import validate_city

User = get_user_model()


# store users list
class StoreUserListView(StoreAdminUserStaff, ListView):
    """
    for listing the users of store
    """

    template_name = "store/users/list-users.html"
    context_object_name = "users"

    def get_queryset(self):
        query = get_object_or_404(
            Store,
            pk=self.request.user.store.id,
        ).users

        form = StoreUsersStaffFilteringForm(self.request.GET or None)
        if form.is_valid():
            if user_PhoneNumber := form.cleaned_data.get('user_PhoneNumber'):
                query = query.filter(PhoneNumber=str(user_PhoneNumber).replace(' ',''))
            if user_email := form.cleaned_data.get('user_email'):
                query = query.filter(email=str(user_email).replace(' ',''))
            if user_name := form.cleaned_data.get('user_name'):
                query = query.filter(Q(first_name=str(user_name)) | Q(last_name=str(user_name)))
            if user_is_store_admin := form.cleaned_data.get('user_is_store_admin'):
                if user_is_store_admin == '11':
                    query = query.filter(is_store_admin=True)
                elif user_is_store_admin == '12':
                    query = query.filter(is_store_admin=False)
            if user_verify_account := form.cleaned_data.get('user_verify_account'):
                if user_verify_account == '11':
                    query = query.filter(is_verified=True)
                elif user_verify_account == '12':
                    query = query.filter(is_verified=False)
            if user_is_active := form.cleaned_data.get('user_is_active'):
                if user_is_active == '11':
                    query = query.filter(is_active=True)
                elif user_is_active == '12':
                    query = query.filter(is_active=False)
            if start_date_joined := form.cleaned_data.get('start_date_joined'):
                parts = str(start_date_joined).split("-")

                if len(parts) != 3:
                    messages.error(
                        self.request,
                        "لطفاً تاریخ  را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                    )

                year, month, day = map(int, parts)

                jalali_date = parse_date(
                    jdatetime.date(year, month, day).strftime("%Y-%m-%d")
                )

                query = query.filter(date_joined__gte=jalali_date)
            if end_date_joined := form.cleaned_data.get('end_date_joined'):
                parts = str(end_date_joined).split("-")

                if len(parts) != 3:
                    messages.error(
                        self.request,
                        "لطفاً تاریخ  را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                    )

                year, month, day = map(int, parts)

                jalali_date = parse_date(
                    jdatetime.date(year, month, day).strftime("%Y-%m-%d")
                )

                query = query.filter(date_joined__lte=jalali_date)
            if start_last_login := form.cleaned_data.get('start_last_login'):
                parts = str(start_last_login).split("-")

                if len(parts) != 3:
                    messages.error(
                        self.request,
                        "لطفاً تاریخ  را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                    )

                year, month, day = map(int, parts)

                jalali_date = parse_date(
                    jdatetime.date(year, month, day).strftime("%Y-%m-%d")
                )

                query = query.filter(last_login__gte=jalali_date)
            if end_last_login := form.cleaned_data.get('end_last_login'):
                parts = str(end_last_login).split("-")

                if len(parts) != 3:
                    messages.error(
                        self.request,
                        "لطفاً تاریخ  را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                    )

                year, month, day = map(int, parts)

                jalali_date = parse_date(
                    jdatetime.date(year, month, day).strftime("%Y-%m-%d")
                )

                query = query.filter(date_joined__lte=jalali_date)

        return query.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = StoreUsersStaffFilteringForm(self.request.GET or None)
        return context


class StoreAddUsersView(StoreAdminUserStaff, FormView):
    """
    for adding users to store staff
    """

    form_class = AddStoreUserStaffForm
    template_name = "store/users/add-users.html"
    success_url = reverse_lazy("store:user-list")

    def form_valid(self, form):
        store = self.request.user.store

        # new user data
        email = form.cleaned_data["email"]
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        phone_number = form.cleaned_data["PhoneNumber"]
        password = form.cleaned_data["password"]
        is_store_admin = form.cleaned_data["is_store_admin"]

        if not password:
            messages.error(self.request, "رمز الزامی می باشد")
            return super().form_valid(form)

        user_exit_check = (
            get_user_model()
            .objects.filter(
                Q(PhoneNumber=phone_number) | Q(email=email),
            )
            .all()
        )

        if not user_exit_check.exists() and user_exit_check.count() == 0:

            get_user_model().objects.create_staff_user(
                PhoneNumber=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                store=store,
                is_store_admin=is_store_admin,
            )

            messages.success(
                self.request,
                "کاربر شما ساخته شد و برای فعال شدن کابر لطفا با ان شماه و رمز وارد سایت شده و پیامک ارسالی را وارد کنید تا حساب تایید بشود",
            )
        else:
            messages.error(self.request, "این شماره یا ایمیل قبلا وارد شده است")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class StoreUpdateUsersView(StoreAdminUserStaff, UpdateView):
    """
    for updating users
    """

    form_class = AddStoreUserStaffForm
    template_name = "store/users/add-users.html"
    success_url = reverse_lazy("store:user-list")
    model = User
    context_object_name = "item"

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model, pk=self.kwargs["pk"], store=self.request.user.store
        )

    def form_valid(self, form):
        # get store obj
        store = self.request.user.store

        # get form instance
        email = form.cleaned_data["email"]
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        phone_number = form.cleaned_data["PhoneNumber"]
        password = form.cleaned_data["password"]
        is_store_admin = form.cleaned_data["is_store_admin"]

        user = get_object_or_404(User, pk=self.kwargs["pk"], store=store)

        if user.PhoneNumber == phone_number and user.email == email:
            if (
                user.first_name != first_name or
                    user.last_name != last_name or
                    user.is_store_admin != is_store_admin
            ):
                user.first_name = first_name
                user.last_name = last_name
                user.is_store_admin = is_store_admin
                user.save()
                messages.success(self.request, "اطلاعات شما بروز رسانی شد")

        elif user.PhoneNumber != phone_number:
            user_exit = get_user_model().objects.filter(
                PhoneNumber=phone_number,
            )
            if not user_exit.exists() and user_exit.count() == 0:
                user.PhoneNumber = phone_number
                user.is_verified = False
                user.save()
                messages.success(
                    self.request,
                    "شماره کاربر مورد نظر تغییر یافت لطفا برای ورود به سایت به قسمت تایید حساب کاربری وارد شوید و حساب خود را تایید کنید",
                )
            else:
                messages.error(self.request, "شماره ارسالی در سایت موجود می باشد")

        elif user.email != email:
            user_exit = get_user_model().objects.filter(
                email=email,
            )
            if not user_exit.exists() and user_exit.count() == 0:
                user.email = email
                user.save()
                messages.success(self.request, "ایمیل مورد کاربر مورد نظر تغییر یافت")
            else:
                messages.error(self.request, "ایمیل ارسال در سایت موجود می باشد")

        if not user.check_password(password) and password:
            user.set_password(password)
            user.save()
            messages.success(self.request, "رمز عبور کابر مورد نظر تغییر یافت")

        return redirect("store:user-list")

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class StoreUserActiveOrDeativate(StoreAdminUserStaff, RedirectView):
    """
    for active or deativate users
    """

    def get_redirect_url(self, *args, **kwargs):
        item = get_object_or_404(
            User, pk=self.kwargs["pk"], store=self.request.user.store
        )
        if item.is_active and not item.is_store_admin:
            item.is_active = False
            messages.success(
                self.request,
                "کاربر مورد نظر غیر فعال شد و دیگر توانای ورود به سایت را ندارد",
            )

        elif not item.is_active and not item.is_store_admin:
            item.is_active = True
            messages.success(self.request, "کاربر مورد نظر  فعال شد")

        if item.is_store_admin:
            item.is_active = True
            messages.error(
                self.request, "شما نمی توانید ادمینای فروشگاه را غیر فعال کنید"
            )

        item.save()
        return self.request.META.get("HTTP_REFERER", "/")


class StoreRemoveUser(StoreAdminUserStaff, View):
    """
    for remove users
    """

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(
            User, pk=self.kwargs["pk"], store=self.request.user.store
        )
        messages.warning(
            request,
            "شما نمی توانید ادمین فروشگاه رو حذف کنید و توجه کنید با حذف کاربر تمام فعالیت ان حذف می شود و بهتر است انرا غیر فعال کنید",
        )
        return render(request, "store/users/delete-user.html", {"item": user})

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(
            User, pk=self.kwargs["pk"], store=self.request.user.store
        )

        phone_number = request.POST["conform"]
        if phone_number.isdigit():
            phone_number = str(phone_number)
            obj = str(user.PhoneNumber).replace(" ", "")
            if obj == phone_number:
                if not user.is_store_admin:
                    user.delete()
                    messages.warning(self.request, "کابر شما حذف شد")
                else:
                    messages.warning(
                        request, "شما نمی توانید ادمین فروشگاه رو حذف کنید"
                    )

            else:
                messages.warning(request, "در وارد کردن اطلاعات دقت فرمایید")
        else:
            messages.error(request, "لطفا فقط شماره رو وارد کنید")

        return redirect("store:user-list")


class StoreUserShowActivities(StoreAdminUserStaff, ListView):
    """
    نمایش فعالیت‌های کاربر با استفاده از ListView
    """

    template_name = "store/users/user_activities.html"
    context_object_name = "activities"
    paginate_by = 100

    def get_queryset(self):
        user = get_object_or_404(self.request.user.store.users, pk=self.kwargs["pk"])

        return LogEntry.objects.filter(actor=user).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن کاربر به context
        context["user"] = get_object_or_404(
            self.request.user.store.users, pk=self.kwargs["pk"]
        )
        return context
