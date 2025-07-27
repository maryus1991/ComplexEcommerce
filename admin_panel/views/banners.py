from django.views.generic import RedirectView, CreateView, UpdateView, ListView
from admin_panel.forms import BannersModelForm
from sitesetting.models import Banners
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from user.mixins.logins import AdminUserMixin
from django.contrib import messages


class BannersListView(AdminUserMixin, ListView):
    """
    for listing the banners
    """

    model = Banners
    context_object_name = "banners"
    template_name = "admin_panel/banners/banners_list.html"
    paginate_by = 10


class BannersCreateView(AdminUserMixin, CreateView):
    """
    for creating a banner
    """

    model = Banners
    form_class = BannersModelForm
    template_name = "admin_panel/banners/banners_form.html"
    success_url = reverse_lazy("admin_panel:banners-list")

    def form_valid(self, form):
        messages.success(self.request, "بنر  مورد نظر با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class BannersUpdateView(AdminUserMixin, UpdateView):
    """for updating a banner"""

    model = Banners
    form_class = BannersModelForm
    template_name = "admin_panel/banners/banners_form.html"
    success_url = reverse_lazy("admin_panel:banners-list")
    context_object_name = "banner"

    def form_valid(self, form):
        messages.success(self.request, "بنر  مورد نظر با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class BannersActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """for activating and deactivating a banner"""

    def get_redirect_url(self, *args, **kwargs):
        banner_id = kwargs.get("pk")
        banner = get_object_or_404(Banners, pk=banner_id)
        if banner.is_active:
            banner.is_active = False
            banner.save()
            messages.success(self.request, "بنر مورد نظر با موفقیت غیر فعال شد")
        else:
            banner.is_active = True
            banner.save()
            messages.success(self.request, "بنر مورد نظر با موفقیت فعال شد")

        return reverse_lazy("admin_panel:banners-list")


class BannersDeleteView(AdminUserMixin, RedirectView):
    """for deleting a banner"""

    def get_redirect_url(self, *args, **kwargs):
        banner_id = kwargs.get("pk")
        banner = get_object_or_404(Banners, pk=banner_id)
        banner.delete()
        messages.info(self.request, "بنر مورد نظر حذف شد")

        return reverse_lazy("admin_panel:banners-list")
