from django.shortcuts import get_object_or_404, reverse, Http404
from django.views.generic import ListView, DetailView, RedirectView
from django.db.models import Q, Count, Prefetch
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
                parent__isnull=True,
            )
            .select_related(
                "store",
                "brand",
                "category",

            )
            .prefetch_related(
                "features",
                "tags",
                "specs",

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

        if "search" in dict(self.request.GET.lists()):
            context['search_param'] = dict(self.request.GET.lists())["search"][0]


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
            )
            .prefetch_related(
                'gallery',
                'features',
                'tags',
                'specs',


                # Product children
                Prefetch(
                    'child',
                    queryset=Product.objects.filter(
                        is_active=True,
                    ),
                    to_attr='active_children',
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

                # Parent children
                Prefetch(
                    'parent__child',
                    queryset=Product.objects.filter(
                        is_active=True,
                    ),
                    to_attr='active_children',
                ),
            ),
            pk=self.kwargs["pk"],
        )

        return product_obj



    def get_context_data(self, **kwargs):



        # check if the product is the user favorite or not
        if self.request.user.is_authenticated:
            is_favorite_product = UserFavorite.objects.filter(
                user=self.request.user, product=self.object
            ).exists()

        else:
            is_favorite_product = False
        context = super().get_context_data(**kwargs)
        context["is_favorite_product"] = is_favorite_product
        context["product_store"] = self.object.store.id

        # get the product comments and add comment form

        context["comment_form"] = ProductCommentForm()
        comments = (
            self.object.comments.annotate(
                like_count=Count("like", filter=Q(like__like=True)),
                dislike_count=Count("like", filter=Q(like__like=False)),
            ).select_related("user")
            .order_by("-id")
            .all()[0:50]
        )
        context["comments"] = comments

        # get the same product
        obj = self.object
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
            .exclude(id=obj.id)
            .distinct()
            .order_by("-id")
        )
        context["same_product"] = same_product

        if self.request.user.is_authenticated:

            order = Order.objects.get_or_create(
                user=self.request.user,
                store=obj.store,
                is_active=True,
                is_paid=False,
                canceled=False,
            )[0]

            context["user_order"] = order
            context["colleague_with_store"] = self.request.user.colleague_with_store.values_list("id", flat=True)
            context["user_order_detail"] = order.details.filter(
                product=obj,
            ).first()

            context["user_favorite"] = list(
                UserFavorite.objects.filter(user=self.request.user).values_list(
                    "product_id", flat=True
                )
            )
        else:
            context["user_favorite"] = []
            context["user_order"] = []
            context["user_order_detail"] = []

        try:
            context["site_zero_the_count_of_all_product"] = self.request.site.zero_the_count_of_all_product

            ip, is_rout = get_client_ip(self.request)
            product_view_object = ProductViews.objects.get_or_create(
                created_at__gte=now().replace(hour=0, minute=0, second=0, microsecond=0),
                user=self.request.user if self.request.user.is_authenticated else None,
                product=self.object,
                ip=ip,
            )
            if not product_view_object[1]:
                product_view_object[0].count += 1
                product_view_object[0].save()

            if product_view_object[0].count == 0:
                product_view_object[0].count = 1
                product_view_object[0].save()

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
        print(1)
        if self.request.method == "POST":
            # check the request
            comment_form = ProductCommentForm(self.request.POST)
            print(2)
            if comment_form.is_valid():
                print(3)
                subject = comment_form.cleaned_data["subject"]
                comment = comment_form.cleaned_data["comment"]
                suggest_product = comment_form.cleaned_data["suggest_product"]

                comment_obj = ProductComment.objects.create(
                    Product=product,
                    user=self.request.user,
                    subject=subject,
                    comment=comment,
                    suggest_product=suggest_product,
                ).save()
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
            ProductComment, pk=self.kwargs["pk"]
        )

        # allowed the super user or store staff or comment creator to remove the comment
        if (
            self.request.user.is_superuser
            or (self.request.user.store == comment.Product.store)
            or (self.request.user == comment.user)
        ):
            comment.delete()

        messages.info(self.request, "نظر شما حذف شد")

        return reverse("product:detail", kwargs={"pk": comment.Product.pk})


class AddLikeComment(LoginRequiredMixin, RedirectView):
    """
    for like a comment and redirect the request to product detail page
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        comment = get_object_or_404(ProductComment, pk=self.kwargs["comment_id"])
        obj = ProductCommentLikeAndDislike.objects.get_or_create(
            comment=comment,
            user=self.request.user,
        )[0]
        obj.like = True
        obj.save()
        messages.info(self.request, "نظر شما ثبت شد")

        return reverse("product:detail", kwargs={"pk": self.kwargs["pk"]})


class DisLikeComment(LoginRequiredMixin, RedirectView):
    """
    for dislike a comment and redirect the request to product detail page
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        comment = get_object_or_404(ProductComment, pk=self.kwargs["comment_id"])
        if comment.Product.id == self.kwargs["pk"]:
            obj = ProductCommentLikeAndDislike.objects.get_or_create(
                comment=comment,
                user=self.request.user,
            )[0]
            obj.like = False
            obj.save()
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
