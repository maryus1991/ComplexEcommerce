from django.db.models import Count, Sum, Case, When, IntegerField
from django.db.models.functions import TruncDate
from user.mixins.logins import UserStoreStaffMixin
from django.views.generic import DetailView
from product.models import Product, ProductViews
from stores.models import Store
from orders.models import Order, StoreSoldOrders
from django.utils.timezone import timedelta, now

from django.db.models.functions import TruncDate, Coalesce
from datetime import timedelta
from django.utils.timezone import now

class StoreMainPage(UserStoreStaffMixin, DetailView):
    """
    for main page of store detail view
    """

    template_name = "store/index2.html"
    pk_url_kwarg = None
    context_object_name = "store"

    def get_object(self, queryset=None):
        return self.request.user.store

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        views = Product.objects.filter(
            store=self.request.user.store
        )
        last_product = views.order_by('-id').all()[0:6]
        views = views.annotate(
            views_count=Count('views')
        ).filter(
            views_count__gt=0
        ).order_by(
            '-views_count'
        ).distinct().values('name', 'views_count')

        context['last_product'] = last_product
        context['views'] = views
        context['total_view'] = views.aggregate(total=Sum('views_count')).get('total')

        context['orders'] = Order.objects.filter(store=self.request.user.store).order_by('-id').all()[0:6]

        item = StoreSoldOrders.objects.filter(
            store_id=self.request.user.store.id
        )

        context['total_price_not_returned_from_admin'] = sum(list(
            item.filter(is_returned_by_admin=False).values_list("price", flat=True)
        ))

        context['total_price'] = sum(list(
            item.values_list("price", flat=True)
        ))

        daily_sales = (
            item.filter(
                open_date__date__gte=now().date() - timedelta(days=30),
            )
            .annotate(
                sale_date=TruncDate("open_date"),
                valid_sale=Case(
                    When(price__gt=0, then="price"),  # فقط قیمت‌های مثبت
                    default=0,
                    output_field=IntegerField(),
                ),
            )
            .values("sale_date")
            .annotate(daily_total=Sum("valid_sale"))
        )

        context['daily_sales'] = [{"date": d, "total": dict(map(lambda x: (x['sale_date'], x['daily_total']),
         daily_sales)).get(d, 0) } for d in [(now().date() - timedelta(days=30)) + timedelta(days=x) for x in range(30)]]

        return context
