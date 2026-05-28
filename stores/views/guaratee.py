from guarantee.models import ActiveProductGuarantee, ProductGuarantee
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
        return self.model.objects.prefetch_related('company').order_by(self.ordering).all()


class GuaranteeCreateView(UserStoreStaffMixin, CreateView):
    """for create guarantee for store"""

    model = ProductGuarantee
    form_class = GuaranteeModelForm
    template_name = "store/product/guarantee/create.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.store.can_store_add_product_guarantee:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, "شما به این صفحه دسترسی ندارید")
        return redirect("store:list-product")

 
    def form_valid(self, form):
 
        messages.success(self.request, "ایتم شما با موفقیت ساخته شد")
        return super().form_valid(form)


    def get_success_url(self):
        return reverse("store:product-guarantee-list", )


    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)
 