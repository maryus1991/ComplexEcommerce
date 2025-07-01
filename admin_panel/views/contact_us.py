from django.shortcuts import get_object_or_404, reverse
from django.views.generic import ListView, DetailView, RedirectView
from sitesetting.models import ContactUs
from user.mixins.logins import AdminUserMixin
from django.contrib import messages


class ContactUsListView(AdminUserMixin, ListView):
    """
    for listing the ContactUs obj
    """

    model = ContactUs
    context_object_name = "items"
    template_name = "admin_panel/contactUs/list.html"
    paginate_by = 20


class ContactUsDetails(AdminUserMixin, DetailView):
    """for detail an obj of ContactUs model"""

    model = ContactUs
    template_name = "admin_panel/contactUs/detials.html"
    context_object_name = "item"

    def get_object(self, queryset=None):
        item = super().get_object()
        item.admin_read = True
        item.save()
        return item


class ContactUsDeleteView(AdminUserMixin, RedirectView):
    """for deleting an  ContactUs model"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(ContactUs, pk=kwargs.get("pk"))
        obj.delete()
        messages.info(self.request, "ایتم مورد نظر حذف شد")

        return reverse("admin_panel:contact-list")
