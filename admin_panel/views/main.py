from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView,
    UpdateView,
    RedirectView,
    CreateView,
View
)
from django.shortcuts import get_object_or_404
from user.mixins.logins import AdminUserMixin
from admin_panel.forms import FastLinksModelForm, QuestionAndAnswerModelForm
from sitesetting.models import FastLinks, QuestionAndAnswer
from django.contrib import messages
# import psutil
# from django.http.response import JsonResponse
from product.models import Product
from orders.models import Order, StoreSoldOrders
from django.db.models import Count, Sum, Case, When, IntegerField
from django.utils.timezone import timedelta, now
from django.db.models.functions import TruncDate, Coalesce
from admin_panel.models import DailyViewCount


# class StatsApi(AdminUserMixin, View):
#     """for get the server data """
#     def get(self, request):
#         stats = {
#             'cpu': psutil.cpu_percent(),
#             'ram': psutil.virtual_memory().percent,
#             'disk': psutil.disk_usage('/').percent,
#             'upload': psutil.net_io_counters().bytes_sent,
#             'download': psutil.net_io_counters().bytes_recv
#         }
#
#         return JsonResponse(stats)


class HomePageView(AdminUserMixin, TemplateView):
    template_name = "admin_panel/index2.html"

    from django.db.models import Count, Sum, Case, When, IntegerField
    from django.db.models.functions import TruncDate
    from datetime import timedelta
    from django.utils.timezone import now

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['last_product'] = Product.objects.order_by('-id')[:6]

        views_qs = Product.objects.annotate(
            views_count=Count('views')
        ).filter(
            views_count__gt=0
        ).order_by(
            '-views_count'
        ).values('name', 'views_count')

        context['views'] = views_qs
        total_view = views_qs.aggregate(total=Sum('views_count'))['total'] or 0
        context['total_view'] = total_view


        today = now().date()
        yesterday = today - timedelta(days=1)

        total_view = total_view

        DailyViewCount.objects.update_or_create(date=today,
                                                defaults={
                                                    'count':
                                                        total_view
                                                })

        yesterday_view = DailyViewCount.objects.filter(date=yesterday).first()
        yesterday_count = yesterday_view.count if yesterday_view else 0

        if yesterday_count > 0:
            percentage_change = ((total_view - yesterday_count) / yesterday_count) * 100
        else:
            percentage_change = 100 if total_view > 0 else 0

        context['view_percentage_change'] = round(percentage_change, 2)

        start_date = today - timedelta(days=29)
        existing_dates = set(
            DailyViewCount.objects.filter(date__gte=start_date).values_list('date', flat=True)
        )
        missing_dates = [start_date + timedelta(days=i) for i in range(30) if
                         (start_date + timedelta(days=i)) not in existing_dates]
        if missing_dates:
            DailyViewCount.objects.bulk_create([DailyViewCount(date=d, count=0) for d in missing_dates])


        context['views_list_by_date'] = DailyViewCount.objects.order_by('date')

        context['orders'] = Order.objects.order_by('-id')[:6]

        item = StoreSoldOrders.objects

        context['total_price_not_returned_from_admin'] = item.filter(
            is_returned_by_admin=False
        ).aggregate(total=Sum('price'))['total'] or 0

        context['total_price'] = item.aggregate(total=Sum('price'))['total'] or 0

        daily_sales_qs = item.filter(
            open_date__date__gte=start_date,
        ).annotate(
            sale_date=TruncDate("open_date"),
            valid_sale=Case(
                When(price__gt=0, then="price"),
                default=0,
                output_field=IntegerField(),
            ),
        ).values("sale_date").annotate(daily_total=Sum("valid_sale"))

        sales_map = {entry['sale_date']: entry['daily_total'] for entry in daily_sales_qs}

        context['daily_sales'] = [
            {
                "date": start_date + timedelta(days=i),
                "total": sales_map.get(start_date + timedelta(days=i), 0)
            } for i in range(30)
        ]

        return context


class FastLinksListView(AdminUserMixin, ListView):
    """for listing FastLinks items for admin"""

    model = FastLinks
    paginate_by = 25
    context_object_name = "items"
    template_name = "admin_panel/fastlinks/list.html"

    def dispatch(self, request, *args, **kwargs):
        messages.warning(
            self.request,
            'توجه داشته باشید که طبق قالب 8 لینک اول نمایش خواهند شد'
        )
        return super().dispatch(request, *args, **kwargs)


class FasLinksSetSortNumber(AdminUserMixin, RedirectView):
    """
    for set sort number for links
    """

    def get_redirect_url(self, *args, **kwargs):

        pk = kwargs.get('pk')
        sort_number = self.request.POST.get(f'{pk}')

        try:
            sort_number = int(sort_number)
            if 100 >= sort_number >= 0:
                post = get_object_or_404(FastLinks, pk=pk)
                post.sort_number = sort_number
                post.save()
                messages.success(self.request,'ثبت شد')
            else:
                messages.error(
                    self.request,
                    'عدد وارد شده باید بین 0 تا 100 باشد'
                )

        except Exception as e:
            messages.error(
                self.request,
                'لطفا در وارد کردن عدد دقت فرمایید'
            )

        return self.request.META.get('HTTP_REFERER')



class FastLinksCreateView(AdminUserMixin, CreateView):
    """for create obj in FastLinks model"""

    form_class = FastLinksModelForm
    model = FastLinks
    template_name = "admin_panel/fastlinks/create.html"
    context_object_name = "items"
    success_url = reverse_lazy("admin_panel:fast-links-list")

    def form_valid(self, form):
        messages.success(self.request, "ایتم  مورد نظر با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class FastLinksUpdateView(AdminUserMixin, UpdateView):
    """for update items in FastLinks"""

    form_class = FastLinksModelForm
    model = FastLinks
    template_name = "admin_panel/fastlinks/create.html"
    context_object_name = "item"
    success_url = reverse_lazy("admin_panel:fast-links-list")

    def form_valid(self, form):
        messages.success(self.request, "ایتم  مورد نظر با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,form.errors.as_text())
        return super().form_invalid(form)


class FastLinksActiveAndDeactivate(AdminUserMixin, RedirectView):
    """for active and deactivate items in FastLinks model"""

    def get_redirect_url(self, *args, **kwargs):
        item_id = kwargs.get("pk")
        item = get_object_or_404(FastLinks, pk=item_id)
        if item.is_active:
            item.is_active = False
            item.save()
            messages.success(self.request, "ایتم مورد نظر با موفقیت غیر فعال شد")
        else:
            item.is_active = True
            item.save()
            messages.success(self.request, "ایتم مورد نظر با موفقیت فعال شد")

        return reverse_lazy("admin_panel:fast-links-list")


class FastLinksDelete(AdminUserMixin, RedirectView):
    """for delete item in FastLinks model"""

    def get_redirect_url(self, *args, **kwargs):
        item_id = kwargs.get("pk")
        item = get_object_or_404(FastLinks, pk=item_id)
        item.delete()
        messages.info(self.request, "ایتم مورد نظر حذف شد")

        return reverse_lazy("admin_panel:fast-links-list")


class QuestionAndAnswerListView(AdminUserMixin, ListView):
    """for listing QuestionAndAnswer  items for admin"""

    model = QuestionAndAnswer
    paginate_by = 25
    context_object_name = "items"
    template_name = "admin_panel/Q&A/list.html"


class QuestionAndAnswerCreateView(AdminUserMixin, CreateView):
    """for create obj in QuestionAndAnswer  model"""

    form_class = QuestionAndAnswerModelForm
    model = QuestionAndAnswer
    template_name = "admin_panel/Q&A/create.html"
    context_object_name = "items"
    success_url = reverse_lazy("admin_panel:Q&A-list")

    def form_valid(self, form):
        messages.success(self.request, "ایتم  مورد نظر با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class QuestionAndAnswerUpdateView(AdminUserMixin, UpdateView):
    """for update items in QuestionAndAnswer"""

    form_class = QuestionAndAnswerModelForm
    model = QuestionAndAnswer
    template_name = "admin_panel/Q&A/create.html"
    context_object_name = "item"
    success_url = reverse_lazy("admin_panel:Q&A-list")

    def form_valid(self, form):
        messages.success(self.request, "ایتم  مورد نظر با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class QuestionAndAnswerActiveAndDeactivate(AdminUserMixin, RedirectView):
    """for active and deactivate items in QuestionAndAnswer  model"""

    def get_redirect_url(self, *args, **kwargs):
        item_id = kwargs.get("pk")
        item = get_object_or_404(QuestionAndAnswer, pk=item_id)
        if item.is_active:
            item.is_active = False
            item.save()
            messages.success(self.request, "ایتم مورد نظر با موفقیت غیر فعال شد")
        else:
            item.is_active = True
            item.save()
            messages.success(self.request, "ایتم مورد نظر با موفقیت فعال شد")

        return reverse_lazy("admin_panel:Q&A-list")


class QuestionAndAnswerDelete(AdminUserMixin, RedirectView):
    """for delete item in QuestionAndAnswer  model"""

    def get_redirect_url(self, *args, **kwargs):
        item_id = kwargs.get("pk")
        item = get_object_or_404(QuestionAndAnswer, pk=item_id)
        item.delete()
        messages.info(self.request, "ایتم مورد نظر حذف شد")

        return reverse_lazy("admin_panel:Q&A-list")
