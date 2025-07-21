from django.views.generic import (
    RedirectView,
    CreateView,
    UpdateView,
    ListView,
    View,
    DetailView,
)
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, reverse, render, Http404
from django.urls import reverse_lazy
from user.mixins.logins import AdminUserMixin
from admin_panel.forms import AddUserModelForm, MessagingUserForm, ExcludeUserFromMessagingForm, AdminUsersFilteringForm
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from utils.send_otp import send_message
from django.contrib.auth import login
from sitesetting.models import Newsletter, SendMessageHistory
from django.db.models import Q

User = get_user_model()


class NumberNewsLetterDelete(AdminUserMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Newsletter, pk=self.kwargs['pk'])
        obj.delete()
        messages.success(
            self.request,
            'حذف شد'
        )
        return self.request.META['HTTP_REFERER']


class ListSendMessageHistory(AdminUserMixin, ListView):
    model = SendMessageHistory
    context_object_name = 'items'
    template_name = 'admin_panel/users/messaging_history.html'
    ordering = '-id'
    paginate_by = 100


class UsersNewsLetters(AdminUserMixin, View):
    """for list and send message to news letters phone number"""

    def get(self, request):
        phones = Newsletter.objects.all()

        if num := self.request.GET.get('search'):
            num = str(num).replace(' ', '')
            phones = phones.filter(phone_number__icontains=num).all()

        context = {
            'items': phones,
        }
        return render(request, 'admin_panel/users/news-letters.html', context=context)

    def post(self, request):
        content = request.POST.get('content', '').strip()
        selected_contacts = request.POST.getlist('selected_contacts')  # استفاده از getlist برای دریافت آرایه

        if not content:
            messages.error(request, "متن پیام نمی‌تواند خالی باشد")
            return redirect('admin_panel:user-news-letters')

        if not selected_contacts:
            messages.error(request, "هیچ مخاطبی انتخاب نشده است")
            return redirect('admin_panel:user-news-letters')

        try:
            numbers = []
            for contact_id in selected_contacts:
                if not contact_id.isdigit():
                    continue

                try:
                    contact = Newsletter.objects.get(id=int(contact_id))
                    phone_number = str(contact).replace(' ', '')
                    numbers.append(phone_number)
                    send_message.delay(phone_number, content)
                except Exception as e:
                    pass

            messages.success(request, f"پیام با موفقیت به {len(selected_contacts)} مخاطب ارسال شد")
            SendMessageHistory.objects.create(
                phone_numbers=''.join(str(item) + ' , ' for item in numbers),
                message=str(content),
            )
        except Newsletter.DoesNotExist:
            messages.error(request, "یکی از مخاطبین یافت نشد")
        except Exception as e:
            messages.error(request, f"خطا در ارسال پیام: {str(e)}")

        return redirect('admin_panel:user-news-letters')


class UserSendManyMessage(AdminUserMixin, View):
    """for message the many users"""

    def get(self, request):
        return render(request, 'admin_panel/users/message_users.html',
                      {'form': MessagingUserForm(),
                       'exclude_form': ExcludeUserFromMessagingForm()
                       })

    def post(self, request):
        form = MessagingUserForm(request.POST)
        exclude_form = ExcludeUserFromMessagingForm(request.POST)

        if not form.is_valid():
            messages.error(request, 'فرم اصلی معتبر نیست')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cleaned_data = form.cleaned_data
        user_field = cleaned_data.get('user')
        content = cleaned_data.get('content')

        # 1. ابتدا: پایه کاربران
        if user_field:
            user_object = user_field.all()
        else:
            user_object = User.objects.all()

        # 2. فیلترهای فرم اصلی
        filter_mapping = {
            'is_verified': True,
            'is_store_admin': True,
            'message_verified': True,
            'not_message_verified': False,
            'legal_person': True,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }

        for field, value in filter_mapping.items():
            if cleaned_data.get(field):
                field_name = field.replace('not_', '')
                user_object = user_object.filter(**{field_name: value})

        # فیلتر فروشگاه
        if cleaned_data.get('store'):
            user_object = user_object.filter(store__in=cleaned_data['store'].all())
        if cleaned_data.get('store_is_active'):
            user_object = user_object.filter(store__is_active=True)
        if cleaned_data.get('store_is_verified'):
            user_object = user_object.filter(store__is_verified=True)

        # 3. اعمال فرم استثناها اگر معتبر بود
        if exclude_form.is_valid():
            exclude_data = exclude_form.cleaned_data

            if exclude_data.get('exclude_user'):
                user_object = user_object.exclude(pk__in=exclude_data['exclude_user'].values_list('pk', flat=True))

            exclude_fields = {
                'exclude_is_verified': 'is_verified',
                'exclude_is_store_admin': 'is_store_admin',
                'exclude_message_verified': 'message_verified',
                'exclude_not_message_verified': 'message_verified',
                'exclude_legal_person': 'legal_person',
                'exclude_is_staff': 'is_staff',
                'exclude_is_superuser': 'is_superuser',
                'exclude_is_active': 'is_active',
            }

            for field, model_field in exclude_fields.items():
                if exclude_data.get(field):
                    user_object = user_object.exclude(**{
                        model_field: not field.startswith('exclude_not_')  # if not_, then exclude False
                    })

            if exclude_data.get('exclude_store'):
                user_object = user_object.exclude(store__in=exclude_data['exclude_store'].all())

            if exclude_data.get('exclude_store_is_active'):
                user_object = user_object.exclude(store__is_active=True)
            if exclude_data.get('exclude_store_is_verified'):
                user_object = user_object.exclude(store__is_verified=True)

        # 4. ارسال پیام
        if not user_object.exists():
            messages.warning(request, 'هیچ کاربری برای ارسال پیام پیدا نشد.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        user_list = []
        for user in user_object:
            user_list.append(str(user.PhoneNumber).replace(" ", ""))
            send_message.delay(str(user.PhoneNumber).replace(" ", ""), content)

        messages.success(request, 'پیام شما با موفقیت ارسال شد')
        SendMessageHistory.objects.create(
            phone_numbers=''.join(str(item) + ' , ' for item in user_list),
            message=str(content),
            news_letter=False,
        )
        return redirect(request.META.get('HTTP_REFERER', '/'))


class AdminLoginToOtherUsersAccounts(AdminUserMixin, RedirectView):
    """for login and solve problems in othere user accounts"""

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user = get_object_or_404(User, id=pk)

        if not user.is_active:
            messages.error(
                self.request,
                'حساب مورد نظر فعال نشده می باشد'
            )
            return reverse("admin_panel:user-list")

        if not user.is_verified:
            messages.error(
                self.request,
                'حساب مورد نظر تایید نشده می باشد'
            )
            return reverse("admin_panel:user-list")

        messages.success(
            self.request,
            'وارد حساب مورد نظر شدید برای به برگشت به حساب قبلی باید از این حساب خارج بشید و دوباره با حساب اولیه وارد بشید'
        )
        login(self.request, user)
        return '/'


class UserListView(AdminUserMixin, ListView):
    """for listing Users"""

    model = User
    context_object_name = "items"
    template_name = "admin_panel/users/list.html"
    paginate_by = 100

    def get_queryset(self):
        query = super().get_queryset().prefetch_related('store', 'address')

        form = AdminUsersFilteringForm(self.request.GET or None)

        if form.is_valid():
            if user_PhoneNumber := form.cleaned_data.get('user_PhoneNumber'):
                query = query.filter(PhoneNumber=str(user_PhoneNumber).replace(' ', ''))
            if store := form.cleaned_data.get('store'):
                query = query.filter(store=store)
            if user_email := form.cleaned_data.get('user_email'):
                query = query.filter(email=str(user_email).replace(' ', ''))
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

            if message_verified := form.cleaned_data.get('message_verified'):
                if message_verified == '11':
                    query = query.filter(message_verified=True)
                elif message_verified == '12':
                    query = query.filter(message_verified=False)

            if legal_person := form.cleaned_data.get('legal_person'):
                if legal_person == '11':
                    query = query.filter(legal_person=True)
                elif legal_person == '12':
                    query = query.filter(legal_person=False)

            if is_super_user := form.cleaned_data.get('is_super_user'):
                if is_super_user == '11':
                    query = query.filter(is_superuser=True)
                elif is_super_user == '12':
                    query = query.filter(is_superuser=False)

            if legal_person_economic_number := form.cleaned_data.get('legal_person_economic_number'):
                query = query.filter(legal_person_economic_number=str(legal_person_economic_number))

            if legal_person_registration_number := form.cleaned_data.get('legal_person_registration_number'):
                query = query.filter(legal_person_registration_number=str(legal_person_registration_number))

            if legal_person_phone := form.cleaned_data.get('legal_person_phone'):
                query = query.filter(legal_person_phone=str(legal_person_phone))

            if address := form.cleaned_data.get('address'):
                query = query.filter(Q(address__name=str(address)),
                                     Q(address__last_name=str(address)), Q(address__province=str(address)),
                                     Q(address__city=str(address)), Q(address__address=str(address)),
                                     Q(address__phone=str(address)), Q(address__zipcode=str(address)),
                                     Q(address__additional_decryption=str(address)))

        return query

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):

        context = super().get_context_data(**kwargs)

        context['form'] = AdminUsersFilteringForm()

        return context


class UserCreateView(AdminUserMixin, CreateView):
    """for creating User"""

    form_class = AddUserModelForm
    template_name = "admin_panel/users/create.html"
    success_url = reverse_lazy("admin_panel:user-list")

    def form_valid(self, form):

        password = form.cleaned_data.get("password")
        conform_password = form.cleaned_data.get("conform_password")
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        PhoneNumber = form.cleaned_data.get("PhoneNumber")
        store = form.cleaned_data.get("store")
        legal_person = form.cleaned_data.get("legal_person")
        legal_person_economic_number = form.cleaned_data.get(
            "legal_person_economic_number"
        )
        is_active = form.cleaned_data.get("is_active")
        legal_person_registration_number = form.cleaned_data.get(
            "legal_person_registration_number"
        )
        is_superuser = form.cleaned_data.get("is_superuser")
        legal_person_phone = form.cleaned_data.get("legal_person_phone")
        is_verified = form.cleaned_data.get("is_verified")
        is_store_admin = form.cleaned_data.get("is_store_admin")
        is_staff = form.cleaned_data.get("is_staff")

        if conform_password != password:
            messages.error(self.request, "رمز های وارد با هم متفاوت هستند")
            return redirect(self.request.META.get("HTTP_REFERER"))

        if password is None or password == "" or not password.isalnum():
            messages.error(self.request, "رمز باید وارد شود")
            return redirect(self.request.META.get("HTTP_REFERER"))

        if is_staff or is_store_admin:
            if store is None:
                messages.error(
                    self.request,
                    "برای فعال کردن قابلیت کارمندی یا مدیریت فروشگاه باید فروشگاه انتخاب شود",
                )
                return redirect(self.request.META.get("HTTP_REFERER"))

        if legal_person:
            if (
                    legal_person_economic_number is None or
                    legal_person_registration_number is None or
                    legal_person_phone is None
            ):
                messages.error(
                    self.request,
                    "برای فعال کردن قابلیت افراد حقوقی با اطلاعات زیر کامل شود : شماره اقتصادی , شماره ثبت , شماره افراد حقوقی",
                )
                return redirect(self.request.META.get("HTTP_REFERER"))

        if is_superuser:
            User.objects.create_superuser(
                password=password,
                first_name=first_name,
                last_name=last_name,
                PhoneNumber=PhoneNumber,
                store=store,
                legal_person=legal_person,
                legal_person_economic_number=legal_person_economic_number,
                is_active=is_active,
                legal_person_registration_number=legal_person_registration_number,
                legal_person_phone=legal_person_phone,
                is_verified=is_verified,
                is_store_admin=is_store_admin,
            )
        elif is_staff:
            User.objects.create_staff_user(
                password=password,
                first_name=first_name,
                last_name=last_name,
                PhoneNumber=PhoneNumber,
                store=store,
                legal_person=legal_person,
                legal_person_economic_number=legal_person_economic_number,
                is_active=is_active,
                legal_person_registration_number=legal_person_registration_number,
                legal_person_phone=legal_person_phone,
                is_verified=is_verified,
                is_store_admin=is_store_admin,
            )
        else:
            User.objects.create_user(
                password=password,
                first_name=first_name,
                last_name=last_name,
                PhoneNumber=PhoneNumber,
                store=store,
                legal_person=legal_person,
                legal_person_economic_number=legal_person_economic_number,
                is_active=is_active,
                legal_person_registration_number=legal_person_registration_number,
                legal_person_phone=legal_person_phone,
                is_verified=is_verified,
                is_store_admin=is_store_admin,
            )

        messages.success(self.request, "کابر ساخته شد")
        return redirect(reverse("admin_panel:user-list"))

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get("HTTP_REFERER"))


class UserUpdateView(AdminUserMixin, UpdateView):
    """for updating User"""

    form_class = AddUserModelForm
    template_name = "admin_panel/users/create.html"
    success_url = reverse_lazy("admin_panel:user-list")
    model = User
    context_object_name = "item"

    def form_valid(self, form):
        password = form.cleaned_data.get("password")
        conform_password = form.cleaned_data.get("conform_password")
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        PhoneNumber = form.cleaned_data.get("PhoneNumber")
        store = form.cleaned_data.get("store")
        legal_person = form.cleaned_data.get("legal_person")
        legal_person_economic_number = form.cleaned_data.get(
            "legal_person_economic_number"
        )
        is_active = form.cleaned_data.get("is_active")
        legal_person_registration_number = form.cleaned_data.get(
            "legal_person_registration_number"
        )
        is_superuser = form.cleaned_data.get("is_superuser")
        legal_person_phone = form.cleaned_data.get("legal_person_phone")
        is_verified = form.cleaned_data.get("is_verified")
        is_store_admin = form.cleaned_data.get("is_store_admin")
        is_staff = form.cleaned_data.get("is_staff")

        if conform_password != password:
            messages.error(self.request, "رمز های وارد با هم متفاوت هستند")
            return redirect(self.request.META.get("HTTP_REFERER"))

        if is_staff or is_store_admin:
            if store is None:
                messages.error(
                    self.request,
                    "برای فعال کردن قابلیت کارمندی یا مدیریت فروشگاه باید فروشگاه انتخاب شود",
                )
                return redirect(self.request.META.get("HTTP_REFERER"))

        if legal_person:
            if (
                    legal_person_economic_number is None or
                    legal_person_registration_number is None or
                    legal_person_phone is None
            ):
                messages.error(
                    self.request,
                    "برای فعال کردن قابلیت افراد حقوقی با اطلاعات زیر کامل شود : شماره اقتصادی , شماره ثبت , شماره افراد حقوقی",
                )
                return redirect(self.request.META.get("HTTP_REFERER"))

        user_object = get_object_or_404(User, pk=self.kwargs["pk"])

        if password is None or password != "" or password.isalnum():
            print(password, "123")
            if not user_object.check_password(password) and user_object != password:
                user_object.set_password(password)

        if PhoneNumber != user_object.PhoneNumber:
            phone_check = User.objects.filter(PhoneNumber=PhoneNumber)
            if phone_check.exists():
                messages.error(self.request, "این شماره قبلا استفاده شده است")
                return redirect(self.request.META.get("HTTP_REFERER"))

        user_object.first_name = first_name
        user_object.last_name = last_name
        user_object.PhoneNumber = PhoneNumber
        user_object.store = store
        user_object.legal_person = legal_person
        user_object.legal_person_economic_number = legal_person_economic_number
        user_object.is_active = is_active
        user_object.legal_person_registration_number = legal_person_registration_number
        user_object.is_superuser = is_superuser
        user_object.legal_person_phone = legal_person_phone
        user_object.is_verified = is_verified
        user_object.is_store_admin = is_store_admin
        user_object.is_staff = is_staff
        user_object.save()

        messages.success(self.request, "تغییرات اعمال شد")

        if self.request.user.id != user_object.id:
            return redirect(reverse("admin_panel:user-list"))
        else:
            return redirect('/')

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get("HTTP_REFERER"))


class UserDetailsView(AdminUserMixin, DetailView):
    """user detail view for admin"""

    model = User
    context_object_name = "item"
    template_name = "admin_panel/users/details.html"

    def get_object(self, queryset=None):
        user = User.objects.filter(id=self.kwargs["pk"]).prefetch_related(
            "address", "store", "blogs", "orders"
        )
        if user.count() != 1:
            raise Http404()
        return user.first()


class UserVerifyView(AdminUserMixin, RedirectView):
    """for VerifyView users"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(User, pk=kwargs.get("pk"))

        if obj == self.request.user:
            messages.warning(
                self.request, "شما نمی توانید این تغییرات را بر حساب خودتان اعمال کنید"
            )
            return reverse("admin_panel:user-list")

        if obj.is_verified:
            obj.is_verified = False
            obj.save()
            messages.warning(self.request, "اطلاعات کابری تایید نشد")
        else:
            obj.is_verified = True
            obj.save()
            messages.success(self.request, "اطلاعات کابری تایید شد")

        return reverse("admin_panel:user-list")


class UserActiveDeactivateView(AdminUserMixin, RedirectView):
    """for ActiveDeactivateView users"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(User, pk=kwargs.get("pk"))

        if obj == self.request.user:
            messages.warning(
                self.request, "شما نمی توانید این تغییرات را بر حساب خودتان اعمال کنید"
            )
            return reverse("admin_panel:user-list")

        if obj.is_active:
            obj.is_active = False
            obj.save()
            messages.warning(
                self.request,
                "حساب غیر فعال شد و این کاربر دیگ توان ورود به سایت را ندارد",
            )
        else:
            obj.is_active = True
            obj.save()
            messages.success(self.request, "حساب فعال شد")

        return reverse("admin_panel:user-list")


class UserDeleteView(AdminUserMixin, View):
    """for deleting users"""

    def get(self, request, *args, **kwargs):
        messages.error(request, "با حذف کاربر موارد دیگه هم حذف خواهمد شد")
        messages.warning(request, "بهتر است به جای حذف کاربر ان را غیر فعال کنید")
        obj = get_object_or_404(User, pk=kwargs.get("pk"))
        return render(request, "admin_panel/users/delete.html", {"item": obj})

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(User, pk=kwargs.get("pk"))
        conform = request.POST.get("conform")

        if obj.PhoneNumber == conform:
            obj.delete()
            messages.info(request, "کاربر مورد نظر حذف شد")
            return redirect("admin_panel:user-list")
        else:
            messages.info(request, "در وارد کردن شماره کاربر دقت کنید")
            return redirect(request.META.get("HTTP_REFERER"))


class UserActivitiesView(AdminUserMixin, ListView):
    """
    نمایش فعالیت‌های کاربر با استفاده از ListView
    """

    template_name = "admin_panel/users/activities.html"
    context_object_name = "activities"
    paginate_by = 100

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["pk"])

        return LogEntry.objects.filter(actor=user).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن کاربر به context
        context["user"] = get_object_or_404(User, pk=self.kwargs["pk"])
        return context
