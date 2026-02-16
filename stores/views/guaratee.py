from guarantee.models import ActiveProductGuarantee, ProductGuarantee, Product
from django.views.generic import CreateView, UpdateView, ListView, RedirectView
from admin_panel.forms import GuaranteeModelForm
from user.mixins.logins import UserStoreStaffMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect



class GuaranteeListView(UserStoreStaffMixin, ListView ):
    
    """for list the guarantee of the product"""

    model = ProductGuarantee
    template_name = "store/product/guarantee/list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name = "items"

    def get_queryset(self):
        return self.model.objects.filter(product__id=self.kwargs.get('pk'), product__store=self.request.user.store).order_by(self.ordering).all()

class ActiveGuaranteeListView(UserStoreStaffMixin, ListView ):
    
    """for list the active guarantee of the product"""

    model = ActiveProductGuarantee
    template_name = "store/product/guarantee/active-list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name = "items"

    def get_queryset(self):
        return self.model.objects.filter(guarantee__id=self.kwargs.get('pk'), guarantee__product__store=self.request.user.store).order_by(self.ordering).all()


class GuaranteeCreateView(UserStoreStaffMixin, CreateView ):
    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "store/product/guarantee/create.html"
    success_url = "store:product-guarantee-list"

    def get_form_class(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.request.user.store.products.all()
        return kwargs

    def get_success_url(self):
        return reverse(self.success_url, kwargs={'pk': self.object.product.id})

    def form_valid(self, form):
        get_object_or_404(Product, form.product.id)
        form.save()
        messages.success(self.request, "ایتم شما با موفقیت ساخته شد")
        return redirect(self.get_success_url)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class GuaranteeUpdateView(UserStoreStaffMixin, UpdateView ):
    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "store/product/guarantee/create.html"
    success_url = "store:product-guarantee-list"
    context_object_name = "item"

    def get_success_url(self):
        return reverse(self.success_url, kwargs={'pk': self.object.product.id})
    
    def get_form_class(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.request.user.store.products.all()
        return kwargs
    
    def form_valid(self, form):
        get_object_or_404(Product, form.product.id)
        form.save()
        messages.success(self.request, "ایتم شما با موفقیت بروزرسانی شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class GuaranteeActiveAndDeactivateView(UserStoreStaffMixin, RedirectView ):
    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        guarantee = get_object_or_404(ProductGuarantee, pk=pk,  guarantee__product__store=self.request.user.store)
        if guarantee.is_active:
            guarantee.is_active = False
            guarantee.save()
            messages.success(self.request, "گارانتی مورد نظر غیر فعال شد")
        else:
            guarantee.is_active = True
            guarantee.save()
            messages.success(self.request, "گارانتی  مورد نظر فعال شد")

        return reverse_lazy("store:product-guarantee-list", kwargs={'pk': guarantee.product.id})


class GuaranteeDeleteView(UserStoreStaffMixin, RedirectView ):
    def get_redirect_url(self, *args, **kwargs):
        
        product = get_object_or_404(ProductGuarantee, pk=kwargs.get("pk"),  guarantee__product__store=self.request.user.store)
        respose = reverse_lazy("store:product-guarantee-list", kwargs={'pk': product.product.id})
        product.delete()
        messages.info(self.request, "گارانتی  مورد نظر حذف شد")
        return respose