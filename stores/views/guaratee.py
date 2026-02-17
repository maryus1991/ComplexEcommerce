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

    def dispatch(self, request, *args, **kwargs):
        
        if request.user.store.can_store_add_product_guarantee:
        
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'شما به این صفحه دسترسی ندارید')
            return redirect('store:list-product')
    

    def get_queryset(self):
        return self.model.objects.filter(product__id=self.kwargs.get('pk'), product__store=self.request.user.store).prefetch_related('actives_guarantee').order_by(self.ordering).all()

class ActiveGuaranteeListView(UserStoreStaffMixin, ListView ):
    
    """for list the active guarantee of the product"""

    model = ActiveProductGuarantee
    template_name = "store/product/guarantee/active-list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name = "items"

    def dispatch(self, request, *args, **kwargs):
        
        if request.user.store.can_store_add_product_guarantee:
        
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'شما به این صفحه دسترسی ندارید')
            return redirect('store:list-product')


    def get_queryset(self):
        return self.model.objects.filter(guarantee__id=self.kwargs.get('pk'), guarantee__product__store=self.request.user.store).order_by(self.ordering).all()


class GuaranteeCreateView(UserStoreStaffMixin, CreateView):
    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "store/product/guarantee/create.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.store.can_store_add_product_guarantee:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, "شما به این صفحه دسترسی ندارید")
        return redirect("store:list-product")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        pk = self.kwargs.get("pk")

        if pk:
            product = get_object_or_404(
                Product,
                pk=pk,
                store=self.request.user.store
            )
            form.fields["product"].initial = product
            form.fields["product"].queryset = Product.objects.filter(pk=product.pk)
            form.fields["product"].widget.attrs["readonly"] = True

        else:
            form.fields["product"].queryset = Product.objects.filter(
                store=self.request.user.store
            )

        return form

    def form_valid(self, form):
        pk = self.kwargs.get("pk")

        if pk:
            product = get_object_or_404(
                Product,
                pk=pk,
                store=self.request.user.store
            )
            form.instance.product = product

        messages.success(self.request, "آیتم شما با موفقیت ساخته شد")
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs.get("pk")
        if pk:
            return reverse("store:product-guarantee-list", kwargs={"pk": pk})
        return reverse("store:list-product")

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class GuaranteeUpdateView(UserStoreStaffMixin, UpdateView ):
    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "store/product/guarantee/create.html"
    success_url = "store:product-guarantee-list"
    context_object_name = "item"


    def dispatch(self, request, *args, **kwargs):
        
        if request.user.store.can_store_add_product_guarantee:
        
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'شما به این صفحه دسترسی ندارید')
            return redirect('store:list-product')

    def get_success_url(self):
        return reverse(self.success_url, kwargs={'pk': self.object.product.id})
    
    def get_form(self):
 
        kwargs = super().get_form()
        kwargs.fields['product'].disabled = True

        return kwargs
    
    def form_valid(self, form):
        form.cleaned_data['product'] = get_object_or_404(Product, id=self.get_object().product.id, store=self.request.user.store)
        form.save()
        messages.success(self.request, "ایتم شما با موفقیت بروزرسانی شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class GuaranteeActiveAndDeactivateView(UserStoreStaffMixin, RedirectView ):

    def dispatch(self, request, *args, **kwargs):
        
        if request.user.store.can_store_add_product_guarantee:
        
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'شما به این صفحه دسترسی ندارید')
            return redirect('store:list-product')
        
    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        guarantee = get_object_or_404(ProductGuarantee, pk=pk,  product__store=self.request.user.store)
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

    def dispatch(self, request, *args, **kwargs):
        
        if request.user.store.can_store_add_product_guarantee:
        
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'شما به این صفحه دسترسی ندارید')
            return redirect('store:list-product')
        
    def get_redirect_url(self, *args, **kwargs):
        
        guarantee = get_object_or_404(ProductGuarantee, pk=kwargs.get("pk"),  product__store=self.request.user.store)
        respose = reverse_lazy("store:product-guarantee-list", kwargs={'pk': guarantee.product.id})
        if guarantee.actives_guarantee.exists():
            messages.info(self.request, "گارانتی مورد نظر برای برخی کاربران فعال شده و نمیشه ان را حذف کرد")
            return respose    
        guarantee.delete()
        messages.info(self.request, "گارانتی  مورد نظر حذف شد")
        return respose