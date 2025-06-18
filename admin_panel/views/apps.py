from django.views.generic import RedirectView, CreateView, UpdateView, ListView, View

from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, redirect
from user.mixins.logins import AdminUserMixin
from django.contrib import messages

from stores.models import StoreApps
from admin_panel.forms import UsedAppModelForm


class AppsListView(AdminUserMixin, ListView):
    """
    for listing the banners
    """
    model = StoreApps
    context_object_name = 'items'
    template_name = 'admin_panel/apps/list.html'
    paginate_by = 20


class AppsCreateView(AdminUserMixin, CreateView):
    """
    for creating a apps
    """
    model = StoreApps
    form_class = UsedAppModelForm
    template_name = 'admin_panel/apps/create.html'
    success_url = reverse_lazy('admin_panel:apps-list')

    def form_valid(self, form):
        messages.success(self.request, 'برنامه  مورد نظر با موفقت افزوده شد شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class AppsUpdateView(AdminUserMixin, UpdateView):
    """for updating a apps"""
    model = StoreApps
    form_class = UsedAppModelForm
    template_name = 'admin_panel/apps/create.html'
    success_url = reverse_lazy('admin_panel:apps-list')

    def form_valid(self, form):
        messages.success(self.request, 'برنامه  مورد نظر با موفقت افزوده شد شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class AppsActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """for activating and deactivating a apps"""

    def get_redirect_url(self, *args, **kwargs):
        app_id = kwargs.get('pk')
        app = get_object_or_404(StoreApps, pk=app_id)
        if app.admin_verified:
            app.admin_verified = False
            app.is_active = False
            app.save()
            messages.success(self.request, 'برنامه مورد نظر با موفقیت غیر فعال شد')
        else:
            app.admin_verified = True
            app.is_active = True
            app.save()
            messages.success(self.request, 'برنامه مورد نظر با موفقیت فعال شد')

        return reverse_lazy('admin_panel:apps-list')


class AppsDeleteView(AdminUserMixin, View):
    """for deleting a banner"""

    def get(self, *args, **kwargs):
        pk = kwargs.get('pk')
        obj = get_object_or_404(StoreApps, pk=pk)
        messages.warning(self.request, f'بهتر است برنامه را غیر فعال کنید اما در صورت تمایل برای حذف اسم برنامه را وارد کنید و بعد از حذف  {obj.store.name} را مطلع کنید')
        return render(self.request, 'admin_panel/apps/delete.html', {'item': obj})

    def post(self, *args, **kwargs):
        pk = kwargs.get('pk')
        obj = get_object_or_404(StoreApps, pk=pk)
        confirm = self.request.POST.get('conform')

        if confirm == obj.name:
            obj.delete()
            messages.info(self.request, 'برنامه مورد نظر حذف شد')
        else:
            messages.error(self.request, 'لطفا اسم برنامه را درست وارد کنید')

        return redirect('admin_panel:apps-list')
