from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from sitesetting.models import SiteSetting
from admin_panel.forms import SiteSettingModelForm
from user.mixins.logins import AdminUserMixin

from django.contrib import messages

class UpdateSiteSettingView(AdminUserMixin, UpdateView):
    """
    for updating site setting
    """
    model = SiteSetting
    template_name = 'admin_panel/site_setting/site_setting.html'
    form_class = SiteSettingModelForm
    success_url = reverse_lazy('admin_panel:update-site-setting')
    context_object_name = 'site'

    def get_object(self):
        site = SiteSetting.objects
        if site.exists() and site.count() == 1:
            return site.first()
        else:
            site.all().delete()
            return site.get_or_create()[0]


    def form_valid(self, form):
        messages.success(
            self.request,
            'تنظیمات سایت با موفقیت تغییر یافت'
        )
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get('HTTP_REFERER'))

