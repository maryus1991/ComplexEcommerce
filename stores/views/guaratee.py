from guarantee.models import ActiveProductGuarantee, ProductGuarantee
from django.views.generic import CreateView, ListView, RedirectView
from user.mixins.logins import UserStoreStaffMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from admin_panel.forms import ActiveGuaranteeModelForm, GuaranteeModelForm
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from user.models import User
from utils.send_otp import send_guarantee_message


class ActiveGuaranteeListView(UserStoreStaffMixin, ListView):
    """ for list the actived guarantee """

    model = ActiveProductGuarantee
    template_name = "store/guarantee/active/list.html"
    ordering = "-id"
    paginate_by = 100
    context_object_name = "items"

    def get_queryset(self):
        return super().get_queryset().filter(guarantee__product__store=self.request.user.store).prefetch_related("guarantee", "user", "guarantee__company", "guarantee__product").order_by(self.ordering).all()
class ActiveGuaranteeCreateView(UserStoreStaffMixin, CreateView):
    """for create active guaranatee"""

    model = ActiveProductGuarantee
    form_class = ActiveGuaranteeModelForm
    template_name = "store/guarantee/active/create.html"
    success_url = reverse_lazy("store:active-guarantee-list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.store.can_store_add_product_guarantee:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, "شما به این صفحه دسترسی ندارید")
        return redirect("store:active-guarantee-list")


    def form_valid(self, form):
        
        if form.instance.guarantee.product.store != self.request.user.store:
            messages.error(self.request, "گارانتی را باید انتخاب کنید که محصول برای فروشگاه شما باشد")
            return self.form_invalid(form)
        
        
        if str(form.instance.phone_number).replace(" ", "") != "" :
            user = User.objects.filter(PhoneNumber = form.instance.phone_number )
            if user.exists() :
                form.instance.user = user.first()
        else:
            form.add_error("phone_number", " شماره نباید خالی بماند " )
            messages.error(self.request, " شماره نباید خالی بماند " )
            return super().form_invalid(form)
    
        form.instance.date_of_started = now()
        form.instance.date_of_expire = now() + relativedelta(
            months=form.instance.guarantee.months_of_expire
        )
        messages.success(self.request, "ایتم شما با موفقیت ساخته شد")

        send_guarantee_message.delay({
            'receptor': str(form.instance.phone_number).replace(" ", "") ,
            'token2':   str(form.instance.phone_number).replace(" ", ""),
            'template': "Guarantee",
            'token':   f"{form.instance.guarantee.serial_number}",
            'token10': f"{form.instance.guarantee.months_of_expire}",
            'token20': f"{form.instance.serial_number}",
            'type': 'sms',
        })

        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)
 
class ActiveGuaranteeDelete(UserStoreStaffMixin, RedirectView):
    """for remove active guaranatee"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.store.can_store_add_product_guarantee:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, "شما به این صفحه دسترسی ندارید")
        return redirect("store:active-guarantee-list")
    
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(ActiveProductGuarantee, id=kwargs.get('pk'))

        if obj.guarantee.product.store == self.request.user.store:

            obj.delete()
            messages.success(self.request,'حذف شد')
        else : 
            messages.error(self.request,'شما اجازه حذف ندارید')
            

        return reverse("store:active-guarantee-list")


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
        return redirect("store:product-guarantee-list")

 
    def form_valid(self, form):
 
        messages.success(self.request, "ایتم شما با موفقیت ساخته شد")
        return super().form_valid(form)


    def get_success_url(self):
        return reverse("store:product-guarantee-list", )


    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)
 