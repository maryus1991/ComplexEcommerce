from django.db.models import Count, Sum, Case, When, IntegerField, Q, Prefetch
from django.db.models.functions import TruncDate, Coalesce
from user.mixins.logins import UserStoreStaffMixin
from django.views.generic import DetailView
from product.models import Product, ProductViews
from stores.models import Store
from orders.models import Order, OrderDetail, StoreSoldOrders
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
        store = self.request.user.store

        views = Product.objects.filter(store=store)
        last_product = views.select_related("category").order_by('-id')[0:6]

        views = (
            views.annotate(views_count=Count('views'))
            .filter(views_count__gt=0)
            .order_by('-views_count')
            .distinct()
            .values('name', 'views_count')
        )

        context['last_product'] = last_product
        context['views'] = views[0:10]
        context['total_view'] = views.aggregate(total=Sum('views_count')).get('total')
        context['orders'] = (
            Order.objects.filter(store=store)
            .select_related("user", "store", "discount")
            .prefetch_related(
                Prefetch(
                    "details",
                    queryset=OrderDetail.objects.select_related("product", "order"),
                )
            )
            .order_by('-id')[0:6]
        )

        item = StoreSoldOrders.objects.filter(store_id=store.id)
        sold_stats = item.aggregate(
            total_price=Coalesce(Sum("price"), 0),
            total_price_not_returned_from_admin=Coalesce(
                Sum("price", filter=Q(is_returned_by_admin=False)), 0
            ),
        )
        context['total_price_not_returned_from_admin'] = sold_stats[
            'total_price_not_returned_from_admin'
        ]
        context['total_price'] = sold_stats['total_price']

        start_date = now().date() - timedelta(days=30)
        daily_sales = (
            item.filter(
                open_date__date__gte=start_date,
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
        sales_by_date = {x['sale_date']: x['daily_total'] for x in daily_sales}

        context['daily_sales'] = [
            {"date": d, "total": sales_by_date.get(d, 0)}
            for d in [start_date + timedelta(days=x) for x in range(30)]
        ]
        return context
