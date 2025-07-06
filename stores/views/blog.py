# store blog
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    CreateView,
    FormView,
    UpdateView,
    RedirectView,
    View,
)
from django.db.models import Q
from django.db.models.aggregates import Count
from django.shortcuts import (
    get_object_or_404,
    reverse,
    render,
    redirect,
    get_list_or_404,
)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.timezone import now
from phonenumbers.phonenumber import PhoneNumber
from django.db import transaction
from django.core.exceptions import (
    PermissionDenied,
    SuspiciousOperation,
    ValidationError,
)
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import UploadedFile
from orders.models import Order
from stores.models import Store, StoreApps
from dashboard.models import Ticket, TicketConversation
from django.utils.dateparse import parse_date
from stores.forms import (
    AddProductForm,
    AddBrandForm,
    AddCategoryForm,
    AddStoreForm,
    StoreSendTicketForm,
    AddStoreUserStaffForm,
    AddStoreAppForm,
    AddStoreBlogForm,
    AddStoreBlogCategoryForm,
    ProductSearchForm,
    BrandAndCategorySearchForm,
    TicketFilterForm,
    OrderFilteringForm,
    StoreBlogFilteringForm,
    StoreUsersStaffFilteringForm,
)
from product.models import (
    Product,
    ProductTag,
    ProductFeature,
    ProductGallery,
    ProductBrand,
    ProductCategory,
)

from django.db.models import Value
from django.db.models.functions import Concat
from blog.models import Blog, BlogCategory
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from user.mixins.logins import UserStoreStaffMixin, AdminUserMixin, StoreAdminUserStaff
from dashboard.forms import TicketConversationForm
import jdatetime

from stores.validators import is_valid_message


User = get_user_model()


class StoreAddBlog(UserStoreStaffMixin, FormView):
    """
    for add blog as store
    """

    template_name = "store/blog/add.html"
    form_class = AddStoreBlogForm
    success_url = reverse_lazy("store:blog-list")

    def form_valid(self, form):
        form.instance.store = self.request.user.store
        form.instance.user = self.request.user
        form.instance.is_active = False
        form.save()
        messages.success(
            self.request,
            "پست شما با موفقیت ایجاد شد لطفا برای انتشار ان پست را فعال کنید",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_form"] = AddStoreBlogCategoryForm()
        return context


class StoreBlogListView(UserStoreStaffMixin, ListView):
    """
    for list all store
    """

    model = Blog
    template_name = "store/blog/list.html"
    context_object_name = "blogs"
    paginate_by = 25

    def get_queryset(self):
        query = (
            super()
            .get_queryset()
            .filter(store=self.request.user.store)
            .prefetch_related("views")
        )

        form = StoreBlogFilteringForm(self.request.GET)

        if not form.is_valid():
            return query

        data = form.cleaned_data

        if user_number := data.get("user_number"):
            query = query.filter(user__PhoneNumber=user_number)
        if start_date := data.get("start_date"):
            query = query.filter(updated_at__gte=start_date, is_active=True)
        if end_date := data.get("end_date"):
            query = query.filter(updated_at__lte=end_date, is_active=True)
        if category := data.get("category"):
            query = query.filter(category=category)
        if is_active := data.get("is_active"):
            if is_active == "11":
                query = query.filter(is_active=True)
            elif is_active == "12":
                query = query.filter(is_active=False)

        if ordering := data.get("ordering"):
            if ordering == "11":  # جدید ترین
                query = query.order_by("-id")
            elif ordering == "12":  # قدیمی ترین
                query = query.order_by("id")
            elif ordering == "21":  # بیشترین بازدید
                query = query.annotate(view_count=Count("views")).order_by(
                    "-view_count"
                )
            elif ordering == "22":  # کمترین بازید
                query = query.annotate(view_count=Count("views")).order_by("view_count")

        if title := data.get("title"):
            query = query.filter(
                Q(title__icontains=title) | Q(content__icontains=title)
            )

        return query

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["form"] = StoreBlogFilteringForm()

        return data


class StoreBlogUpdateView(UserStoreStaffMixin, UpdateView):
    """
    for update blog posts
    """

    template_name = "store/blog/add.html"
    form_class = AddStoreBlogForm
    success_url = reverse_lazy("store:blog-list")
    model = Blog

    def form_valid(self, form):
        form.instance.store = self.request.user.store
        form.instance.user = self.request.user
        form.instance.is_active = False
        form.save()
        messages.success(
            self.request,
            "پست شما با موفقیت بروزرسانی شد لطفا برای انتشار ان پست را فعال کنید",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_form"] = AddStoreBlogCategoryForm()
        return context


class StoreBlogDeleteView(StoreAdminUserStaff, View):
    """
    for delete blog posts
    """

    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        post = get_object_or_404(Blog, pk=pk, store=self.request.user.store)
        messages.warning(
            request,
            "با حذف این پست تمامی اطلاعات به صورت کامل حذف می شوند بهتر است انرا غیر فعال کنید",
        )
        return render(request, "store/blog/delete.html", {"post": post})

    def post(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        post = get_object_or_404(Blog, pk=pk, store=self.request.user.store)

        post_title: str = request.POST.get("conform")

        if not post_title.isspace():
            if post_title == post.title:
                post.delete()
                messages.info(request, "پست شما با موفقیت حذف شد")

            else:
                messages.error(request, "در وارد کردن اطلاعات خواسته شده دقت کنید")
        else:
            messages.error(request, "در وارد کردن اطلاعات خواسته شده دقت کنید")

        return redirect("store:blog-list")


class StoreActiveOrDeactivate(UserStoreStaffMixin, RedirectView):
    """
    for active or deactivate posts
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs["pk"]

        post = get_object_or_404(Blog, pk=pk, store=self.request.user.store)

        if post.is_active:
            post.is_active = False
            post.updated_at = now()
            post.save()

            messages.warning(
                self.request,
                "پست شما غیر فعال شد  و برای کابران غیر قابل مشاهده میباشد",
            )
        else:
            post.is_active = True
            post.updated_at = now()
            post.save()

            messages.success(
                self.request,
                "پست شما فعال شد  و انتشار یافت و برای کابران قابل مشاهده میباشد",
            )

        return reverse("store:blog-list")


class StoreBlogAddCategories(UserStoreStaffMixin, FormView):
    """
    for add blog categories
    """

    template_name = "store/blog/category/add.html"
    form_class = AddStoreBlogCategoryForm
    success_url = reverse_lazy("store:blog-list-category")

    def form_valid(self, form):
        form.instance.is_active = True
        form.save()
        messages.success(self.request, "دسته با موفقیت ساخته شد")
        return redirect(self.request.META.get("HTTP_REFERER"))

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get("HTTP_REFERER"))


class StoreBlogListCategories(UserStoreStaffMixin, ListView):
    """
    for list all blog categories
    """

    model = BlogCategory
    template_name = "store/blog/category/list.html"
    context_object_name = "categories"
    paginate_by = 25

    from django.db.models import Count, Q

    def get_queryset(self):
        # دریافت کوئری‌ست پایه با prefetch_related برای بهینه‌سازی
        query = super().get_queryset().prefetch_related("blogs")

        # دریافت پارامترهای فیلتر از request
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        views = self.request.GET.get("views")
        posts = self.request.GET.get("posts")

        # فیلتر بر اساس جستجو (نام یا توضیحات)
        if search:
            query = query.filter(name__icontains=search)

        # فیلتر بر اساس وضعیت فعال/غیرفعال
        if status == "active":
            query = query.filter(is_active=True)
        elif status == "inactive":
            query = query.filter(is_active=False)

        # فیلتر بر اساس تعداد پست‌ها
        if posts:
            # ابتدا تعداد پست‌ها را annotate کنیم
            query = query.annotate(posts_count=Count("blogs"))

            if posts == "most_posts":
                query = query.order_by("-posts_count")
            elif posts == "least_posts":
                query = query.order_by("posts_count")
            elif posts.isdigit():
                # فیلتر بر اساس تعداد دقیق پست‌ها
                query = query.filter(posts_count=int(posts))

        return query.distinct()
