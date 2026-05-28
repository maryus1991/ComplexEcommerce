from guarantee.models import ActiveProductGuarantee, ProductGuarantee, GuaranteeCompany
from django.views.generic import CreateView, UpdateView, ListView, RedirectView
from admin_panel.forms import GuaranteeModelForm, GuaranteeCompanyModelForm
from user.mixins.logins import AdminUserMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404


class GuaranteeCompanyListView(AdminUserMixin, ListView):
    """ for list the guarantee company"""

    model = GuaranteeCompany
    template_name = "admin_panel/guarantee/company/list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name = "items"
class GuaranteeCompanyCreateView(AdminUserMixin, CreateView):
    """for create company object"""

    model = GuaranteeCompany
    form_class = GuaranteeCompanyModelForm
    template_name = "admin_panel/guarantee/company/create.html"
    success_url = reverse_lazy("admin_panel:company-guarantee-list")

    def form_valid(self, form):
        messages.success(self.request, "ایتم شما با موفقیت ساخته شد")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)
class GuaranteeCompanyUpdateView(AdminUserMixin, UpdateView):
    """for update company object"""

    model = GuaranteeCompany
    form_class = GuaranteeCompanyModelForm
    template_name = "admin_panel/guarantee/company/create.html"
    success_url = reverse_lazy("admin_panel:company-guarantee-list")
    context_object_name = "item"

    def form_valid(self, form):
        messages.success(self.request, "ایتم شما با موفقیت بروز رسانی شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)
class GuaranteeCompanyDelete(AdminUserMixin, RedirectView):
    """for remove the company"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(GuaranteeCompany, id=kwargs.get('pk'))
        obj.delete()
        messages.success(self.request,'حذف شد')

        return reverse("admin_panel:company-guarantee-list")


class GuaranteeListView(AdminUserMixin, ListView ):
    """for list the guarantee of the product"""

    
    template_name = "admin_panel/guarantee/list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name="items"

    def get_queryset(self):
        return ProductGuarantee.objects.prefetch_related('company').all()
class GuaranteeCreateView(AdminUserMixin, CreateView ):
    """for create guarantee"""
    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "admin_panel/guarantee/create.html"
 

    def get_success_url(self):
        return reverse("admin_panel:guarantee-list")
    
    def form_valid(self, form):
        messages.success(self.request, "ایتم شما با موفقیت ساخته شد")
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)
class GuaranteeUpdateView(AdminUserMixin, UpdateView ):
    """for update guarantee"""
    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "admin_panel/guarantee/create.html"
 
    context_object_name = "item"

    def get_success_url(self):
        return reverse("admin_panel:guarantee-list")

    def form_valid(self, form):

        messages.success(self.request, "ایتم شما با موفقیت بروز رسانی شد")
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)
class GuaranteeActiveAndDeactivateView(AdminUserMixin, RedirectView ):
    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        guarantee = get_object_or_404(ProductGuarantee, pk=pk)
        if guarantee.is_active:
            guarantee.is_active = False
            guarantee.save()
            messages.success(self.request, "گارانتی مورد نظر غیر فعال شد")
        else:
            guarantee.is_active = True
            guarantee.save()
            messages.success(self.request, "گارانتی  مورد نظر فعال شد")

        return reverse_lazy("admin_panel:guarantee-list")
class GuaranteeDeleteView(AdminUserMixin, RedirectView ):
    """for delete guarantee """
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(ProductGuarantee, id=kwargs.get('pk'))
        obj.delete()
        messages.success(self.request,'حذف شد')

        return reverse("admin_panel:guarantee-list")


class ActiveGuaranteeListView(AdminUserMixin, ListView ):
    
    """for list the active guarantee of the product"""

    model = ActiveProductGuarantee
    template_name = "admin_panel/product/guarantee/active-list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name = "items"

    def get_queryset(self):
        return self.model.objects.filter(guarantee__id=self.kwargs.get('pk')).order_by(self.ordering).all()

    def get_redirect_url(self, *args, **kwargs):
        
        product = get_object_or_404(ProductGuarantee, pk=kwargs.get("pk"))
        respose = reverse_lazy("admin_panel:product-guarantee-list", kwargs={'pk': product.product.id})
        product.delete()
        messages.info(self.request, "گارانتی  مورد نظر حذف شد")
        return respose