from guarantee.models import ActiveProductGuarantee, ProductGuarantee, GuaranteeCompany
from django.views.generic import CreateView, UpdateView, ListView, RedirectView
from admin_panel.forms import GuaranteeModelForm
from user.mixins.logins import AdminUserMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404


class GuaranteeCompanyListView(AdminUserMixin, ListView):pass
class GuaranteeCompanyCreateView(AdminUserMixin, CreateView):pass
class GuaranteeCompanyUpdateView(AdminUserMixin, UpdateView):pass
class GuaranteeCompanyDelete(AdminUserMixin, RedirectView):pass


class GuaranteeListView(AdminUserMixin, ListView ):
    
    """for list the guarantee of the product"""

    model = ProductGuarantee
    template_name = "admin_panel/product/guarantee/list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name = "items"

    def get_queryset(self):
        return self.model.objects.filter(product__id=self.kwargs.get('pk')).prefetch_related('actives_guarantee').order_by(self.ordering).all()

class ActiveGuaranteeListView(AdminUserMixin, ListView ):
    
    """for list the active guarantee of the product"""

    model = ActiveProductGuarantee
    template_name = "admin_panel/product/guarantee/active-list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name = "items"

    def get_queryset(self):
        return self.model.objects.filter(guarantee__id=self.kwargs.get('pk')).order_by(self.ordering).all()

class GuaranteeCreateView(AdminUserMixin, CreateView ):
    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "admin_panel/product/guarantee/create.html"
    success_url = "admin_panel:product-guarantee-list"

    def get_success_url(self):
        return reverse(self.success_url, kwargs={'pk': self.object.product.id})
    

    def form_valid(self, form):
        
        if  form.instance.product.guarantee.count() == 0 : 

            messages.success(self.request, "ایتم شما با موفقیت ساخته شد")
            return super().form_valid(form)

        else:
            messages.error(self.request, "شما نمی توانید بیشتر از یک گارانتی برای هر محصول بسازید")
            return self.form_invalid(form)


    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)

class GuaranteeUpdateView(AdminUserMixin, UpdateView ):
    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "admin_panel/product/guarantee/create.html"
    success_url = "admin_panel:product-guarantee-list"
    context_object_name = "item"

    def get_success_url(self):
        return reverse(self.success_url, kwargs={'pk': self.object.product.id})

    def form_valid(self, form):
        
        if  form.instance.product.guarantee.count() == 1 and self.get_object().product == form.instance.product: 
            

            messages.success(self.request, "ایتم شما با موفقیت بروز رسانی شد")
            return super().form_valid(form)

        else:
            messages.error(self.request, "شما نمی توانید بیشتر از یک گارانتی برای هر محصول بسازید")
            return self.form_invalid(form)
  

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

        return reverse_lazy("admin_panel:product-guarantee-list", kwargs={'pk': guarantee.product.id})

class GuaranteeDeleteView(AdminUserMixin, RedirectView ):
    def get_redirect_url(self, *args, **kwargs):
        
        product = get_object_or_404(ProductGuarantee, pk=kwargs.get("pk"))
        respose = reverse_lazy("admin_panel:product-guarantee-list", kwargs={'pk': product.product.id})
        product.delete()
        messages.info(self.request, "گارانتی  مورد نظر حذف شد")
        return respose