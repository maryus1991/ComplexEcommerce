from django.contrib import messages
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.utils.timezone import now, datetime, timedelta

from .models import Blog, BlogView, BlogCategory, BlogTag
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
        Returns active records annotated with their blog view counts
        """

        item = (
            super()
            .get_queryset()
            .filter(is_active=True, admin_verified=True, category__is_active=True)
            .annotate(view_count=Count("views"))
        )

        url_params = dict(self.request.GET.lists())

        if "category" in url_params:
            category = url_params["category"]
            category_list = []

            # Handle both single values and lists
            categories = [category] if isinstance(category, str) else category

            for num in categories:
                # Check if the value is a digit (more efficient than try/except for this case)
                if isinstance(num, str) and num.isdigit():
                    try:
                        category_list.append(int(num))
                    except (ValueError, TypeError):
                        continue  # Skip invalid values
                elif isinstance(num, int):
                    category_list.append(num)

            # Only apply filter if we have valid categories
            if category_list:
                item = item.filter(category__in=category_list)

            # Process start date

        if "start_date" in url_params or "end_date" in url_params:
            if url_params["start_date"][0] != "" or url_params["end_date"][0] != "":
                start_date = None
                end_date = None

                # Helper function to parse and validate dates
                def parse_jalali_date(date_str, field_name):
                    try:
                        if not isinstance(date_str, str):
                            date_str = (
                                "".join(date_str)
                                if isinstance(date_str, (list, tuple))
                                else str(date_str)
                            )

                        parts = date_str.split("-")

                        if len(parts) != 3:
                            raise ValueError("Invalid date format")

                        year, month, day = map(int, parts)
                        jalali_date = jdatetime.date(year, month, day)
                        gregorian_date = parse_date(
                            jalali_date.togregorian().strftime("%Y-%m-%d")
                        )

                        if gregorian_date is None:
                            raise ValueError("Date conversion failed")

                        return gregorian_date
                    except (ValueError, TypeError, IndexError) as e:
                        messages.error(
                            self.request,
                            f"لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                        )
                        return None

                # Process start date
                if "start_date" in url_params:

                    if url_params["start_date"][0] != " ":

                        start_date = parse_jalali_date(url_params["start_date"], "شروع")

                # Process end date
                if "end_date" in url_params:
                    if url_params["end_date"][0] != " ":
                        end_date = parse_jalali_date(url_params["end_date"], "پایان")

                # Apply date filtering
                if start_date and end_date:
                    if start_date > end_date:
                        messages.error(
                            self.request, "تاریخ شروع باید قبل از تاریخ پایان باشد"
                        )
                    else:
                        item = item.filter(updated_at__range=[start_date, end_date])
                elif start_date:
                    item = item.filter(updated_at__gte=start_date)
                elif end_date:
                    item = item.filter(updated_at__lte=end_date)

        if "newset" in url_params:
            item = item.order_by("-id")

        if "hottest" in url_params:
            item = item.order_by("-view_count")

        if "today" in url_params:
            item = item.filter(updated_at__date=now())

        if "yesterday" in url_params:
            item = item.filter(updated_at__date=now() - timedelta(days=1))

        if "ordering" in url_params:
            ordering = url_params["ordering"][0]

            if ordering == "1":
                item = item.order_by("-view_count")
            elif ordering == "2":
                item = item.order_by("-id")
            elif ordering == "3":
                item = item.order_by("-view_count")

        return item.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = (
            BlogCategory.objects.filter(parent=None).prefetch_related("children").all()
        )

        context["date_input"] = BlogFilterForm()

        return context


class DetailArticleView(DetailView):
    """
    for detail article
    """

    template_name = "blog/article-details.html"
    model = Blog
    context_object_name = "post"

    def get_object(self):
        pk = self.kwargs["pk"]
        obj = get_object_or_404(
            self.model,
            pk=pk,
            is_active=True,
            admin_verified=True,
            category__is_active=True,
        )
        return self.get_queryset().filter(id=obj.id).prefetch_related("tags").first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            ip, is_rout = get_client_ip(self.request)
            view = BlogView.objects.get_or_create(ip=ip, blog_id=self.kwargs["pk"])

            if not view[1]:
                view[0].count += 1
                view[0].save()

            if view[0].count == 0:
                view[0].count = 1
                view[0].save()

        except Exception as e:
            pass

        last_posts = Blog.objects.filter(is_active=True).all().order_by("-id")[:4]
        categories = (
            BlogCategory.objects.filter(is_active=True)
            .annotate(post_count=Count("blogs"))
            .all()
            .order_by("-post_count")[:4]
        )

        context["last_posts"] = last_posts
        context["categories"] = categories
        return context
