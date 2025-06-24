from orders.models import Discount
from django.views.generic import RedirectView, CreateView, UpdateView, View, ListView
from django.shortcuts import redirect, get_object_or_404, render, reverse
from django.urls import reverse_lazy
from user.mixins.logins import AdminUserMixin
from admin_panel.forms import AddDiscountForm
from django.contrib import messages


class DiscountListView(AdminUserMixin, ListView):
    """for listing discounts"""
    model = Discount
    paginate_by = 25
    context_object_name = 'items'
    template_name = 'admin_panel/discount/list.html'

class DiscountCreateView(AdminUserMixin, CreateView):
    """for create discount"""
    form_class = AddDiscountForm
    template_name = 'admin_panel/discount/create.html'
    success_url = reverse_lazy('admin_panel:discount-list')

    def form_valid(self, form):
        messages.success(self.request, 'کد تخفیف شما ساخته شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class DiscountUpdateView(AdminUserMixin, UpdateView):
    """for update discount"""
    form_class = AddDiscountForm
    model = Discount
    template_name = 'admin_panel/discount/create.html'
    success_url = reverse_lazy('admin_panel:discount-list')
    context_object_name = 'item'

    def form_valid(self, form):
        messages.success(self.request, 'کد تخفیف شما بروزرسانی شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

class DiscountActiveAndDeActivate(AdminUserMixin, RedirectView):
    """for active and de activate an object"""
    def get_redirect_url(self, *args, **kwargs):
        item = get_object_or_404(Discount, pk=self.kwargs['pk'])

        if item.is_active:
            item.is_active = False
            item.save()
            messages.warning(self.request, 'ایتم غیر فعال شد')
        else:
            item.is_active = True
            item.save()
            messages.success(self.request, 'ایتم فعال شد')

        return reverse('admin_panel:discount-list')

class DiscountDeleteView(AdminUserMixin, RedirectView):
    """for delete discount"""

    def get_redirect_url(self, *args, **kwargs):
        item = get_object_or_404(Discount, pk=self.kwargs['pk'])
        item.delete()
        messages.success(self.request, 'کد تخفیف حذف شد')
        return reverse('admin_panel:discount-list')



