from django.views.generic import RedirectView, CreateView, UpdateView, ListView, View, DetailView
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, reverse, render, Http404
from django.urls import reverse_lazy
from user.mixins.logins import AdminUserMixin
from admin_panel.forms import AddUserModelForm
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class UserListView(AdminUserMixin, ListView):
    """for listing Users"""
    model = User
    context_object_name = 'items'
    template_name = 'admin_panel/users/list.html'
    paginate_by = 25


class UserCreateView(AdminUserMixin, CreateView):
    """for creating User"""
    form_class = AddUserModelForm
    template_name = 'admin_panel/users/create.html'
    success_url = reverse_lazy('admin_panel:user-list')

    def form_valid(self, form):

        password = form.cleaned_data.get('password')
        conform_password = form.cleaned_data.get('conform_password')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        PhoneNumber = form.cleaned_data.get('PhoneNumber')
        store = form.cleaned_data.get('store')
        legal_person = form.cleaned_data.get('legal_person')
        legal_person_economic_number = form.cleaned_data.get('legal_person_economic_number')
        is_active = form.cleaned_data.get('is_active')
        legal_person_registration_number = form.cleaned_data.get('legal_person_registration_number')
        is_superuser = form.cleaned_data.get('is_superuser')
        legal_person_phone = form.cleaned_data.get('legal_person_phone')
        is_verified = form.cleaned_data.get('is_verified')
        is_store_admin = form.cleaned_data.get('is_store_admin')
        is_staff = form.cleaned_data.get('is_staff')

        if conform_password != password:
            messages.error(self.request, 'رمز های وارد با هم متفاوت هستند')
            return redirect(self.request.META.get('HTTP_REFERER'))

        if password is None or password == '' or not password.isalnum():
            messages.error(self.request, 'رمز باید وارد شود')
            return redirect(self.request.META.get('HTTP_REFERER'))


        if is_staff or is_store_admin:
            if store is None:
                messages.error(self.request, 'برای فعال کردن قابلیت کارمندی یا مدیریت فروشگاه باید فروشگاه انتخاب شود')
                return redirect(self.request.META.get('HTTP_REFERER'))

        if legal_person:
            if legal_person_economic_number is None or legal_person_registration_number is None or legal_person_phone is None:
                messages.error(self.request,
                               'برای فعال کردن قابلیت افراد حقوقی با اطلاعات زیر کامل شود : شماره اقتصادی , شماره ثبت , شماره افراد حقوقی')
                return redirect(self.request.META.get('HTTP_REFERER'))

        if is_superuser:
            User.objects.create_superuser(password=password,
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
            User.objects.create_staff_user(password=password,
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
            User.objects.create_user(password=password,
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

        messages.success(
            self.request,
            'کابر ساخته شد'
        )
        return redirect(reverse('admin_panel:user-list'))

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get('HTTP_REFERER'))


class UserUpdateView(AdminUserMixin, UpdateView):
    """for updating User"""

    form_class = AddUserModelForm
    template_name = 'admin_panel/users/create.html'
    success_url = reverse_lazy('admin_panel:user-list')
    model = User
    context_object_name = 'item'

    def form_valid(self, form):
        password = form.cleaned_data.get('password')
        conform_password = form.cleaned_data.get('conform_password')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        PhoneNumber = form.cleaned_data.get('PhoneNumber')
        store = form.cleaned_data.get('store')
        legal_person = form.cleaned_data.get('legal_person')
        legal_person_economic_number = form.cleaned_data.get('legal_person_economic_number')
        is_active = form.cleaned_data.get('is_active')
        legal_person_registration_number = form.cleaned_data.get('legal_person_registration_number')
        is_superuser = form.cleaned_data.get('is_superuser')
        legal_person_phone = form.cleaned_data.get('legal_person_phone')
        is_verified = form.cleaned_data.get('is_verified')
        is_store_admin = form.cleaned_data.get('is_store_admin')
        is_staff = form.cleaned_data.get('is_staff')

        if conform_password != password:
            messages.error(self.request, 'رمز های وارد با هم متفاوت هستند')
            return redirect(self.request.META.get('HTTP_REFERER'))

        if is_staff or is_store_admin:
            if store is None:
                messages.error(self.request, 'برای فعال کردن قابلیت کارمندی یا مدیریت فروشگاه باید فروشگاه انتخاب شود')
                return redirect(self.request.META.get('HTTP_REFERER'))

        if legal_person:
            if legal_person_economic_number is None or legal_person_registration_number is None or legal_person_phone is None:
                messages.error(self.request,
                               'برای فعال کردن قابلیت افراد حقوقی با اطلاعات زیر کامل شود : شماره اقتصادی , شماره ثبت , شماره افراد حقوقی')
                return redirect(self.request.META.get('HTTP_REFERER'))

        user_object = get_object_or_404(User, pk=self.kwargs['pk'])

        if password is None or password != '' or password.isalnum():
            print(password, '123')
            if not user_object.check_password(password) and user_object != password:
                user_object.set_password(password)

        if PhoneNumber != user_object.PhoneNumber:
            phone_check = User.objects.filter(PhoneNumber=PhoneNumber)
            if phone_check.exists():
                messages.error(self.request, 'این شماره قبلا استفاده شده است')
                return redirect(self.request.META.get('HTTP_REFERER'))

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

        messages.success(
            self.request,
            'تغییرات اعمال شد'
        )

        return redirect(reverse('admin_panel:user-list'))

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get('HTTP_REFERER'))


class UserDetailsView(AdminUserMixin, DetailView):
    """ user detail view for admin"""
    model = User
    context_object_name = 'item'
    template_name = 'admin_panel/users/details.html'

    def get_object(self, queryset=None):
        user = User.objects.filter(id=self.kwargs['pk']
                            ).prefetch_related(
            'address', 'store', 'blogs', 'orders'
        )
        if user.count() != 1:
            raise Http404()
        return user.first()


class UserVerifyView(AdminUserMixin, RedirectView):
    """for VerifyView users"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(User, pk=kwargs.get('pk'))

        if obj == self.request.user:
            messages.warning(self.request, 'شما نمی توانید این تغییرات را بر حساب خودتان اعمال کنید')
            return reverse('admin_panel:user-list')

        if obj.is_verified:
            obj.is_verified = False
            obj.save()
            messages.warning(self.request, 'اطلاعات کابری تایید نشد')
        else:
            obj.is_verified = True
            obj.save()
            messages.success(self.request, 'اطلاعات کابری تایید شد')

        return reverse('admin_panel:user-list')


class UserActiveDeactivateView(AdminUserMixin, RedirectView):
    """for ActiveDeactivateView users"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(User, pk=kwargs.get('pk'))

        if obj == self.request.user:
            messages.warning(self.request, 'شما نمی توانید این تغییرات را بر حساب خودتان اعمال کنید')
            return reverse('admin_panel:user-list')

        if obj.is_active:
            obj.is_active = False
            obj.save()
            messages.warning(self.request, 'حساب غیر فعال شد و این کاربر دیگ توان ورود به سایت را ندارد')
        else:
            obj.is_active = True
            obj.save()
            messages.success(self.request, 'حساب فعال شد')

        return reverse('admin_panel:user-list')


class UserDeleteView(AdminUserMixin, View):
    """for deleting users"""
    def get(self, request, *args, **kwargs):
        messages.error(request ,'با حذف کاربر موارد دیگه هم حذف خواهمد شد')
        messages.warning(request ,'بهتر است به جای حذف کاربر ان را غیر فعال کنید')
        obj = get_object_or_404(User, pk=kwargs.get('pk'))
        return render(request, 'admin_panel/users/delete.html', {'item': obj})

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(User, pk=kwargs.get('pk'))
        conform = request.POST.get('conform')

        if obj.PhoneNumber == conform:
            obj.delete()
            messages.info(request, 'کاربر مورد نظر حذف شد')
            return redirect('admin_panel:user-list')
        else:
            messages.info(request, 'در وارد کردن شماره کاربر دقت کنید')
            return redirect(request.META.get('HTTP_REFERER'))

class UserActivitiesView(AdminUserMixin, ListView):
    """
    نمایش فعالیت‌های کاربر با استفاده از ListView
    """
    template_name = 'admin_panel/users/activities.html'
    context_object_name = 'activities'
    paginate_by = 50

    def get_queryset(self):
        user = get_object_or_404(
            User,
            pk=self.kwargs['pk']
        )

        return LogEntry.objects.filter(
            actor=user
        ).order_by('-timestamp')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن کاربر به context
        context['user'] = get_object_or_404(
            User,
            pk=self.kwargs['pk']
        )
        return context