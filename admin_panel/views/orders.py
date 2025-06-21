from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect, render , reverse
from django.urls import reverse_lazy
from orders.models import Order
from user.mixins.logins import AdminUserMixin

class OrderListView(AdminUserMixin, ListView):
    """for listing the orders"""
    model = Order
    context_object_name = 'items'
    template_name = 'admin_panel/orders/list.html'
    ordering = '-id'
    paginate_by = 25

class OrderDetailView(AdminUserMixin, DetailView):
    """for listing the orders"""
    model = Order
    context_object_name = 'order'
    template_name = 'admin_panel/orders/details.html'

    def get_object(self):
        order = Order.objects.filter(pk=self.kwargs['pk']
             ).prefetch_related(
    'address', 'user', 'store').first()
        return order
