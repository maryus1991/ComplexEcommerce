from django.views.generic import RedirectView, CreateView, UpdateView, ListView, View, DetailView
from django.shortcuts import get_object_or_404, redirect, reverse, render, Http404
from django.urls import reverse_lazy
from user.mixins.logins import AdminUserMixin
from stores.models import Store
from django.contrib import messages
from stores.forms import AddStoreForm
from utils.tipax_price_calc import validate_city
from django.core.exceptions import ValidationError


class StoreListView(AdminUserMixin, ListView):
    """
    for listing the stores
    """
    model = Store
    context_object_name = 'items'
    template_name = 'admin_panel/store/list.html'


class StoreCreateView(AdminUserMixin, CreateView):
    """
    for creating a new store
    """
    form_class = AddStoreForm
    template_name = 'admin_panel/store/create.html'
    success_url = reverse_lazy('admin_panel:store-list')

    def form_valid(self, form):
        data = form.cleaned_data

        if data.get('have_in_same_city_delivery') and data.get('in_same_city_delivery_price') is None:
            messages.error(self.request, 'برای فعال کردن پست درون شهری باید هزینه ان وارد شود')
            return redirect(self.request.META.get('HTTP_REFERER'))

        if data.get('have_official_invoice'):
            if (data.get('have_official_invoice') is None or
                    data.get('official_invoice_price') is None or
                    data.get('economic_number') is None or
                    data.get('registration_number') is None or
                    data.get('official_invoice_phone_number') is None):
                messages.error(self.request,
                               'برای فعال شدن صدور فاکتور رسمی باید همه فیلد های مربوط به فاکتور رسمی پر شود')
                return redirect(self.request.META.get('HTTP_REFERER'))

        if self.request.user.store.orgin_city != data.get('orgin_city'):
            validate_city_result = validate_city(data.get('orgin_city'))

            if validate_city_result is None:
                messages.error(
                    self.request,
                    'مشکلی پیش امد'
                )
                return redirect(self.request.META.get('HTTP_REFERER', '/'))

            if len(validate_city_result) > 1:
                messages.warning(
                    self.request,
                    f'''
                    شهر شما یافت نشد لطفا در نشونتن ان دقت فرمایید
                    لیست شهر های پیدا شده با این اسم ارسالی شما 
                        {" , ".join([x['title'] for x in list(validate_city_result)])}''')
                return redirect(self.request.META.get('HTTP_REFERER', '/'))

            if len(validate_city_result) == 1:
                form.instance.orgin_city_id = validate_city_result[0]['id']

        messages.success(self.request, '  فروشگاه ساخته شد')
        form.instance.is_verified = False

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, form.errors
        )
        return super().form_invalid(form)


class StoreUpdateView(AdminUserMixin, UpdateView):
    """
    for update a store
    """
    model = Store
    form_class = AddStoreForm
    template_name = 'admin_panel/store/create.html'
    success_url = reverse_lazy('admin_panel:store-list')
    context_object_name = 'item'

    def form_valid(self, form):
        data = form.cleaned_data

        if data.get('have_in_same_city_delivery') and data.get('in_same_city_delivery_price') is None:
            messages.error(self.request, 'برای فعال کردن پست درون شهری باید هزینه ان وارد شود')
            return redirect(self.request.META.get('HTTP_REFERER'))

        if data.get('have_official_invoice'):
            if (data.get('have_official_invoice') is None or
                    data.get('official_invoice_price') is None or
                    data.get('economic_number') is None or
                    data.get('registration_number') is None or
                    data.get('official_invoice_phone_number') is None):
                messages.error(self.request,
                               'برای فعال شدن صدور فاکتور رسمی باید همه فیلد های مربوط به فاکتور رسمی پر شود')
                return redirect(self.request.META.get('HTTP_REFERER'))

        if self.request.user.store.orgin_city != data.get('orgin_city'):
            validate_city_result = validate_city(data.get('orgin_city'))

            if validate_city_result is None:
                messages.error(
                    self.request,
                    'مشکلی پیش امد'
                )
                return redirect(self.request.META.get('HTTP_REFERER', '/'))

            if len(validate_city_result) > 1:
                messages.warning(
                    self.request,
                    f'''
                    شهر شما یافت نشد لطفا در نشونتن ان دقت فرمایید
                    لیست شهر های پیدا شده با این اسم ارسالی شما 
                        {" , ".join([x['title'] for x in list(validate_city_result)])}''')
                return redirect(self.request.META.get('HTTP_REFERER', '/'))

            if len(validate_city_result) == 1:
                form.instance.orgin_city_id = validate_city_result[0]['id']

        messages.success(self.request, 'اطلاعات شما با موقیت ثبت شد')
        form.instance.is_verified = False

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, form.errors
        )
        return super().form_invalid(form)


class StoreDetailView(AdminUserMixin, DetailView):
    """
    for store detail view
    """
    model = Store
    context_object_name = 'item'
    template_name = 'admin_panel/store/details.html'

    def get_object(self, queryset=None):
        user = self.model.objects.filter(
            pk=self.kwargs['pk']
        ).prefetch_related(
            'blogs', 'products', 'users', 'orders'
        )

        if user.count() != 1:
            raise Http404()

        return user.first()


class StoreVerifyView(AdminUserMixin, RedirectView):
    """
    for verify store
    """

    def get_redirect_url(self, *args, **kwargs):
        store = get_object_or_404(Store, pk=self.kwargs['pk'])
        if store.is_verified:
            store.is_verified = False
            store.save()
            messages.warning(self.request, 'وضعیت اطلاعات فروشگاه تایید نشد')
        else:
            store.is_verified = True
            store.save()
            messages.success(self.request, 'وضعیت اطلاعات فروشگاه تایید شد')

        return reverse('admin_panel:store-list')


class StoreActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """for active and deactivate store view"""

    def get_redirect_url(self, *args, **kwargs):
        store = get_object_or_404(Store, pk=self.kwargs['pk'])
        if store.is_active:
            store.is_active = False
            store.save()
            messages.warning(self.request, 'وضعیت اطلاعات فروشگاه غیر فعال شد')
        else:
            store.is_active = True
            store.save()
            messages.success(self.request, 'وضعیت اطلاعات فروشگاه فعال شد')

        return reverse('admin_panel:store-list')


class StoreDeleteView(AdminUserMixin, View):
    """for delete store"""

    def get(self, request, *args, **kwargs):
        messages.error(
            request, 'با حذف این فرشگاه تمام محصولات و پست و کاربران ان حذف خواهند شد '
        )
        messages.warning(request,
                         'بهتر است که به جای حذف فروشگاه ان را غیر فعال کنید و از حذف این همه اطلاعات جلوگیری کنید')
        obj = get_object_or_404(Store, pk=self.kwargs['pk'])
        obj = Store.objects.filter(id=obj.id).prefetch_related('products').prefetch_related('users').first()
        return render(request, 'admin_panel/store/delete.html', {'item': obj})

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(Store, pk=self.kwargs['pk'])
        obj = Store.objects.filter(id=obj.id).prefetch_related('products').prefetch_related('users').prefetch_related(
            'blogs').first()

        if obj.name == request.POST.get('conform'):
            obj.delete()
            messages.warning(request, 'فروشگاه مورد نظر حذف شد')
        else:
            messages.warning(request, 'در وارد کردن نام فروشگاه دقت کنید')

        return redirect('admin_panel:store-list')
