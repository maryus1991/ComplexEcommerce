from django.contrib import messages
from django.views.generic import ListView, DetailView, View, RedirectView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from orders.models import Order, StoreSoldOrders, Store, ReturnsOrders, SpecificsOrders
from user.mixins.logins import AdminUserMixin
from django.db.models.aggregates import Count
from django.utils.timezone import now
from admin_panel.forms import SpecificsOrdersModelForm
from sitesetting.models import SiteSetting
from utils.send_otp import send_message


class ChangeStatusToDeliveredToUser(AdminUserMixin, RedirectView):
    """for set sending id and change status to DeliveredToUser"""

    def get_redirect_url(self, *args, **kwargs):

        order = get_object_or_404(
            Order, pk=self.kwargs["pk"]
        )

        order.delivered_to_user = True
        send_id = self.request.GET.get("sending_id")

        order.sending_id = send_id if send_id else 'تحویل شده به کاربر'
        order.save()
        messages.success(self.request, "تغییرات ثبت شد")

        if SiteSetting.objects.first().send_message_when_set_sending_id:
            send_message.delay(
                str(order.user.PhoneNumber).replace(" ", ""),
                f"""محموله شما ارسال شد 
                code:{order.sending_id}
                """,  # noqa
            )


        return self.request.META.get("HTTP_REFERER")


class OrderListView(AdminUserMixin, ListView):
    """for listing the orders"""

    model = Order
    context_object_name = "items"
    template_name = "admin_panel/orders/list.html"
    ordering = "-id"
    paginate_by = 25

    def get_queryset(self):
        return super().get_queryset().prefetch_related('store', 'address', 'user')


class OrderSoldListView(AdminUserMixin, ListView):
    """for listing the orders"""

    model = StoreSoldOrders
    context_object_name = "items"
    template_name = "admin_panel/orders/sold-list.html"
    ordering = "-id"
    paginate_by = 100

    def get_queryset(self):
        return super().get_queryset().prefetch_related("store", 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stores'] = Store.objects.annotate(
            order_count=Count('store_sold_orders')
        ).filter(
            order_count__gte=1
        ).all()
        return context


class OrderDetailView(AdminUserMixin, DetailView):
    """for listing the orders"""

    model = Order
    context_object_name = "order"
    template_name = "admin_panel/orders/details.html"

    def get_object(self, queryset=None):
        order = (
            Order.objects.filter(pk=self.kwargs["pk"])
            .prefetch_related("address", "user", "store")
            .first()
        )
        return order


class OrderSoledChangeStatus(AdminUserMixin, RedirectView):

    """for change soled order status"""

    def get_redirect_url(self, *args, **kwargs):
        store_id = self.kwargs["pk"]
        items = StoreSoldOrders.objects.filter(store_id=store_id, is_returned_by_admin=False).all()

        for item in items:
            item.is_returned_by_admin = True
            item.paid_by_admin_date = now()
            item.save()

        messages.success(
            self.request,
            'حساب مورد نظر تصفیه شد'
        )

        return reverse("admin_panel:orders-sold-list")


class SpecificsOrdersListView(AdminUserMixin, ListView):
    """for listing the orders"""
    model = SpecificsOrders
    paginate_by = 25
    context_object_name = "items"
    template_name = "admin_panel/orders/specifics/list.html"


class SpecificsOrderDetailView(AdminUserMixin, DetailView):
    """for listing the orders"""
    model = SpecificsOrders
    context_object_name = "item"
    template_name = "admin_panel/orders/specifics/details.html"


class SpecificsOrderCreateView(AdminUserMixin, CreateView):
    """for create the orders"""

    form_class = SpecificsOrdersModelForm
    model = SpecificsOrders
    template_name = "admin_panel/orders/specifics/create.html"
    success_url = reverse_lazy("admin_panel:specifics-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            'ثبت شد'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            form.errors
        )
        return super().form_valid(form)


class SpecificsOrdersUpdateView(AdminUserMixin, UpdateView):
    """for update the orders"""

    form_class = SpecificsOrdersModelForm
    model = SpecificsOrders
    template_name = "admin_panel/orders/specifics/create.html"
    success_url = reverse_lazy("admin_panel:specifics-list")
    context_object_name = "item"

    def form_valid(self, form):

        if self.object.is_paid:
            messages.error(
                self.request,'شما نمی توانید فاکتوری که پرداخت شده رو بروزرسانی کنید'
            )
            return redirect("admin_panel:specifics-list")
        
        messages.success(
            self.request,
            'ثبت شد'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            form.errors
        )
        return super().form_valid(form)

class SpecificsOrdersDeleteView(AdminUserMixin, RedirectView):
    """for delete orders"""

    def get_redirect_url(self, *args, **kwargs):

        obj = get_object_or_404(SpecificsOrders, pk=self.kwargs["pk"])
        if not obj.is_paid and obj.Authority is None:
            obj.delete()
            messages.success(
                self.request,
                'حذف شد'
            )

        else:
            messages.error(
                self.request,
                'شما نمی توانید فاکتور پرداخت شده رو پاک کنید'
            )
        return reverse('admin_panel:specifics-list')

# return order

class ReturnOrderList(AdminUserMixin, ListView):
    """return order list"""
    model = ReturnsOrders
    template_name = 'admin_panel/orders/returns/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return super().get_queryset().order_by('-id')


class ReturnOrderDetail(AdminUserMixin, DetailView):
    """return order detail"""
    model = ReturnsOrders
    template_name = 'admin_panel/orders/returns/details.html'
    context_object_name = 'item'

    def get_object(self, queryset=None):
        return get_object_or_404(ReturnsOrders, pk=self.kwargs['pk'])


class ReturnOrderAcceptByAdmin(AdminUserMixin, RedirectView):
    """return order accept by store"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(ReturnsOrders, pk=self.kwargs['pk'])
        if obj.send_request_to_return_this_order_by_admin:
            obj.date_close_request = now()
            obj.accept_by_admin = True
            obj.accept_by_store = True
            obj.save()
            messages.success(
                self.request,
                'تایید شد و مرجوعی توسط ادمین انجام میشه'
            )
        else:
            messages.error(
                self.request,
                'فروشگاه درخواست پرگشتی توسط ادمین را نداده است'
            )
        return reverse('admin_panel:return-order-list')


