from django.shortcuts import get_object_or_404, reverse, Http404
from django.views.generic import ListView, DetailView, RedirectView
from django.db.models import Q, Count, Prefetch, F
from django.contrib import messages
from django.utils.timezone import now
from user.mixins.logins import CustomLoginRequiredMixin as LoginRequiredMixin

from .models import (
    Product,
    ProductComment,
    UserFavorite,
    ProductCategory,
    ProductBrand,
    ProductCommentLikeAndDislike,
    NotificationUserForProductAvailability,
    ProductViews,
)
from guarantee.models import ProductGuarantee as Guarantee
from stores.models import Store
from .forms import ProductCommentForm
from orders.models import OrderDetail, Order
from sitesetting.models import SiteSetting
from ipware import get_client_ip


# Create your views here.


class ProductListView(ListView):
    """
    list the products
    """

    template_name = "product/shop.html"
    model = Product
    paginate_by = 24
    context_object_name = "products"

    def get_queryset(self):


        products = (
            Product.objects
            .filter(
                is_active=True,
                store__is_active=True,
                store__is_verified=True,
                admin_verified=True,
                brand__is_active=True,
                category__is_active=True,
             )
            .select_related(
                "store",
                "brand",
                "category",
            )
        )

        params = self.request.GET

        available = params.get("available", "").strip().lower() == "on"

        if available:
            products = products.filter(count__gte=1)



        search = params.get("search", "").strip()

        if search:
             if search.isalnum():
                products = products.filter(
                    name__icontains=search
                )



        def get_positive_int_param(name):

            value = params.get(name, "").strip()

            if not value:
                return None

            try:
                number = int(value)

                if number < 0:
                    return None

                return number

            except (TypeError, ValueError):
                return None

        start_price = get_positive_int_param("start_price")
        end_price = get_positive_int_param("end_price")

        if start_price is not None:
            products = products.filter(
                price__gte=start_price
            )

        if end_price is not None:
            products = products.filter(
                price__lte=end_price
            )



        def get_valid_ids(name):


            values = params.getlist(name)

            valid_ids = []

            for value in values:
                value = value.strip()

                if not value:
                    continue

                try:
                    value = int(value)

                    if value > 0:
                        valid_ids.append(value)

                except (TypeError, ValueError):
                    continue

            return valid_ids

        category_ids = get_valid_ids("category")

        if category_ids:
            products = products.filter(
                category_id__in=category_ids,
                category__is_active=True,
            )



        store_ids = get_valid_ids("store")

        if store_ids:
            products = products.filter(
                store_id__in=store_ids
            )



        brand_ids = get_valid_ids("brand")

        if brand_ids:
            products = products.filter(
                brand_id__in=brand_ids,
                brand__is_active=True,
            )



        sort_value = params.get("sort", "").strip()

        sort = None

        if sort_value:
            try:
                sort = int(sort_value)

            except (TypeError, ValueError):
                sort = None

        sort_map = {
            1: ["-have_discount", "-discount"],
            2: ["orders__count"],
            3: ["price"],
            4: ["-price"],
            5: ["-id"],
        }

        if sort in sort_map:
            products = products.order_by(
                *sort_map[sort]
            )

        else:


            site = getattr(self.request, "site", None)

            if site:
                site_sort_map = [
                    (
                        getattr(site, "product_sort_by_count", False),
                        ["-count"],
                    ),
                    (
                        getattr(site, "product_sort_by_highest_price", False),
                        ["-price"],
                    ),
                    (
                        getattr(site, "product_sort_by_lowest_price", False),
                        ["price"],
                    ),
                    (
                        getattr(site, "product_sort_by_sort_number", False),
                        ["-sort_number"],
                    ),
                    (
                        getattr(
                            site,
                            "product_sort_by_category_sort_number",
                            False,
                        ),
                        ["-category__sort_number"],
                    ),
                    (
                        getattr(
                            site,
                            "product_sort_by_brand_sort_number",
                            False,
                        ),
                        ["-brand__sort_number"],
                    ),
                    (
                        getattr(
                            site,
                            "product_sort_by_existing_count",
                            False,
                        ),
                        ["-count"],
                    ),
                ]

                applied_sort = False

                for condition, fields in site_sort_map:
                    if condition:
                        products = products.order_by(*fields)
                        applied_sort = True

                if not applied_sort:
                    products = products.order_by(
                        "-count",
                        "-sort_number",
                    )

            else:
                products = products.order_by(
                    "-count",
                    "-sort_number",
                )

        return products.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = (
            ProductCategory.objects
            .filter(
                is_active=True,
                parent__isnull=True,
            )
            .prefetch_related(
                Prefetch(
                    "child",
                    queryset=ProductCategory.objects.filter(is_active=True).prefetch_related(
                        Prefetch(
                            "child",
                            queryset=ProductCategory.objects.filter(is_active=True).prefetch_related(
                                Prefetch(
                                    "child",
                                    queryset=ProductCategory.objects.filter(is_active=True)
                                )
                            )
                        )
                    )
                )
            )
        )

        context["stores"] = (
            Store.objects.filter(is_active=True, is_verified=True)
            .order_by("-sort_number").distinct()

        )
        context["site_zero_the_count_of_all_product"] = self.request.site.zero_the_count_of_all_product
        context["brands"] = ProductBrand.objects.filter(is_active=True).order_by("-sort_number").all()

        if self.request.user.is_authenticated and self.request.user.is_verified:
            context["user_favorite"] = list(
                UserFavorite.objects.filter(user=self.request.user).values_list(
                    "product_id", flat=True
                )
            )
            context["user_details_orders"] = list(
                OrderDetail.objects.filter(
                    product__is_active=True,
                    order__user=self.request.user,
                    order__is_active=True,
                    order__canceled=False,
                    order__is_paid=False,
                ).values_list("product_id", flat=True)
            )
        else:
            context["user_favorite"] = []
            context["user_details_orders"] = []

        if self.request.user.is_authenticated and self.request.user.colleague_user:
            context["colleague_store_ids"] = set(
                self.request.user.colleague_with_store.values_list("id", flat=True)
            )
        else:
            context["colleague_store_ids"] = set()

        if "search" in dict(self.request.GET.lists()):
            context['search_param'] = dict(self.request.GET.lists())["search"][0]

        site_title = getattr(self.request.site, "title", "") if getattr(self.request, "site", None) else ""
        cat_ids = [int(v) for v in self.request.GET.getlist("category") if v.strip().isdigit()]
        brand_ids = [int(v) for v in self.request.GET.getlist("brand") if v.strip().isdigit()]
        active_category = ProductCategory.objects.filter(pk=cat_ids[0], is_active=True).first() if len(cat_ids) == 1 else None
        active_brand = ProductBrand.objects.filter(pk=brand_ids[0], is_active=True).first() if len(brand_ids) == 1 else None

        if active_category and active_brand:
            page_title = f"{active_category.name} {active_brand.name} | {site_title}"
            page_description = f"خرید آنلاین و بررسی قیمت انواع {active_category.name} برند {active_brand.name} با گارانتی معتبر از {site_title}."
        elif active_category:
            page_title = f"{active_category.name} | خرید و قیمت در {site_title}"
            page_description = f"مشاهده قیمت، مشخصات فنی و خرید آنلاین انواع {active_category.name} با تضمین اصالت کالا در {site_title}."
        elif active_brand:
            page_title = f"محصولات برند {active_brand.name} | {site_title}"
            page_description = f"فروشگاه آنلاین محصولات اورجینال برند {active_brand.name} با بهترین قیمت و ارسال سریع در {site_title}."
        elif context.get("search_param"):
            page_title = f"جستجوی {context['search_param']} | {site_title}"
            page_description = f"نتایج جستجو برای {context['search_param']} در فروشگاه اینترنتی {site_title}."
        else:
            page_title = f"فروشگاه و لیست محصولات | {site_title}"
            page_description = f"مشاهده، مقایسه قیمت و خرید آنلاین تمامی محصولات با گارانتی و ارسال سریع از فروشگاه {site_title}."

        scheme = "https" if self.request.is_secure() else self.request.scheme
        context["active_category"] = active_category
        context["active_brand"] = active_brand
        context["page_title"] = page_title
        context["page_description"] = page_description
        context["page_url"] = f"{scheme}://{self.request.get_host()}{self.request.path}"

        return context


class ProductDetailView(DetailView):
    """
    product detail page
    """

    template_name = "product/product-details.html"

    context_object_name = "product"

    def get_object(self, queryset=None):
        product_obj = get_object_or_404(
            Product.objects
            .filter(
                is_active=True,
                store__is_active=True,
                store__is_verified=True,
                admin_verified=True,
                brand__is_active=True,
                category__is_active=True,
            )
            .select_related(
                'brand',
                'category',
                'store',
                'parent',
                'parent__store',
            )
            .prefetch_related(
                'gallery',
                'features',
                'tags',
                'specs',

                # Product comments (used in JSON-LD structured data)
                Prefetch(
                    'comments',
                    queryset=ProductComment.objects.select_related('user'),
                ),

                # Product children
                Prefetch(
                    'child',
                    queryset=Product.objects.filter(
                        is_active=True,
                    ).select_related('store'),
                ),

                # Guarantees
                Prefetch(
                    'guarantee',
                    queryset=Guarantee.objects.select_related('company'),
                ),

                # Parent relations
                'parent__gallery',
                'parent__features',
                'parent__specs',
                'parent__tags',

                # Parent children
                Prefetch(
                    'parent__child',
                    queryset=Product.objects.filter(
                        is_active=True,
                    ).select_related('store'),
                ),
            ),
            pk=self.kwargs["pk"],
        )

        return product_obj



    def get_context_data(self, **kwargs):



        context = super().get_context_data(**kwargs)
        obj = self.object
        context["product_store"] = obj.store_id

        # get the product comments and add comment form
        context["comment_form"] = ProductCommentForm()
        comments = (
            obj.comments.annotate(
                like_count=Count("like", filter=Q(like__like=True)),
                dislike_count=Count("like", filter=Q(like__like=False)),
            ).select_related("user")
            .order_by("-id")
            .all()[0:50]
        )
        context["comments"] = comments

        # get the same product
        same_product = (
            Product.objects.filter(
                Q(is_active=True),
                Q(admin_verified=True),
                (
                        Q(brand=obj.brand, brand__is_active=True) |
                        Q(category=obj.category, category__is_active=True) |
                        Q(category__parent=obj.category, category__parent__is_active=True)
                )
            )
            .select_related("store", "brand", "category")
            .exclude(id=obj.id)
            .distinct()
            .order_by("-id")[:16]
        )
        context["same_product"] = same_product

        if self.request.user.is_authenticated:
            user_favorite = list(
                UserFavorite.objects.filter(user=self.request.user).values_list(
                    "product_id", flat=True
                )
            )
            context["user_favorite"] = user_favorite
            context["is_favorite_product"] = obj.id in user_favorite

            order = (
                Order.objects.filter(
                    user=self.request.user,
                    store=obj.store,
                    is_active=True,
                    is_paid=False,
                    canceled=False,
                )
                .select_related("discount")
                .prefetch_related(
                    Prefetch(
                        "details",
                        queryset=OrderDetail.objects.select_related("product", "order"),
                    )
                )
                .first()
            )
            if order is None:
                order = Order.objects.create(
                    user=self.request.user,
                    store=obj.store,
                    is_active=True,
                    is_paid=False,
                    canceled=False,
                )
                order._prefetched_objects_cache = {"details": []}

            order_details = list(order.details.all())
            for d in order_details:
                d.order = order

            context["user_order"] = order
            context["colleague_with_store"] = (
                list(self.request.user.colleague_with_store.values_list("id", flat=True))
                if self.request.user.colleague_user
                else []
            )
            context["user_order_detail"] = next(
                (d for d in order_details if d.product_id == obj.id), None
            )
        else:
            context["is_favorite_product"] = False
            context["user_favorite"] = []
            context["user_order"] = []
            context["user_order_detail"] = []
            context["colleague_with_store"] = []

        try:
            context["site_zero_the_count_of_all_product"] = self.request.site.zero_the_count_of_all_product

            ip, is_rout = get_client_ip(self.request)
            product_view_object, created = ProductViews.objects.get_or_create(
                created_at__gte=now().replace(hour=0, minute=0, second=0, microsecond=0),
                user=self.request.user if self.request.user.is_authenticated else None,
                product=self.object,
                ip=ip,
                defaults={"count": 1},
            )
            if not created:
                ProductViews.objects.filter(pk=product_view_object.pk).update(
                    count=F("count") + 1
                )

        except Exception as e:
            pass

        return context


class AddProductComment(LoginRequiredMixin, RedirectView):
    """
    for create a comment and redirect the request to product detail page
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["pk"])

        if self.request.method == "POST":
            # check the request
            comment_form = ProductCommentForm(self.request.POST)

            if comment_form.is_valid():

                subject = comment_form.cleaned_data["subject"]
                comment = comment_form.cleaned_data["comment"]
                suggest_product = comment_form.cleaned_data["suggest_product"]

                ProductComment.objects.create(
                    Product=product,
                    user=self.request.user,
                    subject=subject,
                    comment=comment,
                    suggest_product=suggest_product,
                )
                messages.success(self.request, "نظر شما ثبت شد")

            else:
                messages.error(self.request, "لطفا در ارسال اطلاعات دقت کنید")
        return super().get_redirect_url(*args, **kwargs)


class RemoveProductComment(LoginRequiredMixin, RedirectView):
    """
    for remove a comment and redirect the request to product detail page
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        # get the comment obj
        comment: ProductComment = get_object_or_404(
            ProductComment.objects.select_related("Product", "Product__store", "user"),
            pk=self.kwargs["pk"],
        )
        product_pk = comment.Product_id

        # allowed the super user or store staff or comment creator to remove the comment
        if (
            self.request.user.is_superuser
            or (self.request.user.store_id == comment.Product.store_id)
            or (self.request.user.id == comment.user_id)
        ):
            comment.delete()

        messages.info(self.request, "نظر شما حذف شد")

        return reverse("product:detail", kwargs={"pk": product_pk})


class AddLikeComment(LoginRequiredMixin, RedirectView):
    """
    for like a comment and redirect the request to product detail page
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        comment = get_object_or_404(ProductComment, pk=self.kwargs["comment_id"])
        ProductCommentLikeAndDislike.objects.update_or_create(
            comment=comment,
            user=self.request.user,
            defaults={"like": True},
        )
        messages.info(self.request, "نظر شما ثبت شد")

        return reverse("product:detail", kwargs={"pk": self.kwargs["pk"]})


class DisLikeComment(LoginRequiredMixin, RedirectView):
    """
    for dislike a comment and redirect the request to product detail page
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        comment = get_object_or_404(ProductComment, pk=self.kwargs["comment_id"])
        if comment.Product_id == self.kwargs["pk"]:
            ProductCommentLikeAndDislike.objects.update_or_create(
                comment=comment,
                user=self.request.user,
                defaults={"like": False},
            )
            messages.info(self.request, "نظر شما ثبت شد")

            return reverse("product:detail", kwargs={"pk": self.kwargs["pk"]})

        else:
            return Http404("not found")


class AddUserToProductAvailability(LoginRequiredMixin, RedirectView):
    """
    for add a user to product availability
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["pk"])
        NotificationUserForProductAvailability.objects.get_or_create(
            product=product,
            user=self.request.user,
        )
        messages.success(
            self.request,
            "در اولین فرصت بعد از موجود شدن محصول با پیامک به شما اطلاع رسانی خواهد شد",
        )

        return reverse("product:detail", kwargs={"pk": self.kwargs["pk"]})
