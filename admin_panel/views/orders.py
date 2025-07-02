from django.contrib import messages
from django.views.generic import ListView, DetailView, View, RedirectView
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from orders.models import Order, StoreSoldOrders, Store
from user.mixins.logins import AdminUserMixin
from django.db.models.aggregates import Count
from django.utils.timezone import now


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