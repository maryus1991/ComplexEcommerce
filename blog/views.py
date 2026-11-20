from django.contrib import messages
from django.db.models import Count, Prefetch, F
from django.shortcuts import  get_object_or_404

from django.views.generic import ListView, DetailView
from django.utils.timezone import now, datetime, timedelta
from stores.models import Store
from .models import Blog, BlogView, BlogCategory
from ipware import get_client_ip
from django.utils.dateparse import parse_date
from .forms import BlogFilterForm

import jdatetime


class ListArticlesView(ListView):
    """
    for listing articles
    """

    template_name = "blog/articles.html"
    model = Blog
    context_object_name = "posts"
    paginate_by = 20



    def get_queryset(self):
        """
        Returns active records with their view counts.

        All GET parameters are validated before being used in queries,
        so invalid, empty, duplicated, or malformed parameters are ignored
        instead of raising exceptions.
        """

        item = (
            super()
            .get_queryset()
            .filter(
                is_active=True,
                admin_verified=True,
                category__is_active=True,
                store__is_active=True,
                store__is_verified=True,
            )
            .annotate(
                view_count=Count("views")
            )
            .select_related(
                "store",
                "category",
            )
            .order_by("-sort_number")
        )

        params = self.request.GET



        def get_valid_ids(param_name):


            values = params.getlist(param_name)

            valid_ids = []

            for value in values:
                value = value.strip()

                if not value:
                    continue

                try:
                    number = int(value)

                    if number > 0:
                        valid_ids.append(number)

                except (TypeError, ValueError):
                    continue

            return valid_ids


        store_ids = get_valid_ids("store")

        if store_ids:
            item = item.filter(
                store_id__in=store_ids
            )


        category_ids = get_valid_ids("category")

        if category_ids:
            item = item.filter(
                category_id__in=category_ids,
                category__is_active=True,
            )



        def parse_jalali_date(value, field_name):
            """
            Safely converts a Jalali date:

                1405-01-15

            to a Gregorian date.

            Invalid values return None and show an error message.
            """

            value = value.strip()

            if not value:
                return None

            try:
                parts = value.split("-")

                if len(parts) != 3:
                    raise ValueError

                year, month, day = map(int, parts)

                jalali_date = jdatetime.date(
                    year,
                    month,
                    day,
                )

                gregorian_date = jalali_date.togregorian()

                return gregorian_date

            except (
                    ValueError,
                    TypeError,
                    OverflowError,
            ):
                messages.error(
                    self.request,
                    f"لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید "
                    f"(فرمت: yyyy-mm-dd)",
                )

                return None



        start_date_value = params.get("start_date", "").strip()
        end_date_value = params.get("end_date", "").strip()

        start_date = None
        end_date = None

        if start_date_value:
            start_date = parse_jalali_date(
                start_date_value,
                "شروع",
            )

        if end_date_value:
            end_date = parse_jalali_date(
                end_date_value,
                "پایان",
            )


        if start_date and end_date:

            if start_date > end_date:
                messages.error(
                    self.request,
                    "تاریخ شروع باید قبل از تاریخ پایان باشد",
                )

            else:
                item = item.filter(
                    updated_at__range=[
                        start_date,
                        end_date,
                    ]
                )

        elif start_date:

            item = item.filter(
                updated_at__gte=start_date
            )

        elif end_date:

            item = item.filter(
                updated_at__lte=end_date
            )



        if params.get("newset") is not None:
            item = item.order_by("-id")


        if params.get("hottest") is not None:
            item = item.order_by("-view_count")


        if params.get("today") is not None:
            today = now().date()

            item = item.filter(
                updated_at__date=today
            )



        if params.get("yesterday") is not None:
            yesterday = (
                    now() - timedelta(days=1)
            ).date()

            item = item.filter(
                updated_at__date=yesterday
            )


        ordering = params.get("ordering", "").strip()

        ordering_map = {
            "1": "-view_count",
            "2": "-id",
            "3": "-view_count",
        }

        if ordering in ordering_map:
            item = item.order_by(
                ordering_map[ordering]
            )


        return item



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_category_qs = BlogCategory.objects.filter(
            is_active=True
        ).order_by("-sort_number")

        context["categories"] = (
            BlogCategory.objects
            .filter(
                is_active=True,
                parent__isnull=True,
            )
            .order_by("-sort_number")
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=active_category_qs.prefetch_related(
                        Prefetch(
                            "children",
                            queryset=active_category_qs.prefetch_related(
                                Prefetch(
                                    "children",
                                    queryset=active_category_qs,
                                )
                            ),
                        )
                    ),
                )
            )
        )

        context["stores"] = (
            Store.objects.filter(is_active=True, is_verified=True)
            .order_by("-sort_number").distinct()
            .all()
        )

        context["date_input"] = BlogFilterForm(self.request.GET)

        return context


class DetailArticleView(DetailView):
    """
    for detail article
    """

    template_name = "blog/article-details.html"

    context_object_name = "post"

    def get_object(self):


        return  get_object_or_404(
            Blog.objects.filter(is_active=True, admin_verified=True, category__is_active=True,).select_related("category", "user", "store"),
            pk=self.kwargs["pk"],

        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            ip, is_rout = get_client_ip(self.request)
            view, created = BlogView.objects.get_or_create(
                ip=ip,
                blog_id=self.kwargs["pk"],
                defaults={"count": 1},
            )
            if not created:
                BlogView.objects.filter(pk=view.pk).update(count=F("count") + 1)

        except Exception as e:
            pass

        last_posts = Blog.objects.filter(is_active=True).all().order_by("-id")[:4]
        categories = (
            BlogCategory.objects.filter(is_active=True)
            .annotate(post_count=Count("blogs"))

            .order_by("-post_count")[:4]
        )

        context["last_posts"] = last_posts
        context["categories"] = categories
        return context
