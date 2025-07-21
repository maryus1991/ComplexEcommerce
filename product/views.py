from django.shortcuts import render, get_object_or_404, reverse, Http404
from django.views.generic import ListView, DetailView, RedirectView
from django.db.models import Q, Count
from django.contrib import messages

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

        # get the url params
        url_params = dict(self.request.GET.lists())
        have_filter_url = False

        # get the product obj
        products = Product.objects.filter(
                is_active=True,
                store__is_active=True,
                store__is_verified=True,
                admin_verified=True,
                brand__is_active=True,
                category__is_active=True,
            ).prefetch_related("features").prefetch_related("tags").prefetch_related("specs").order_by("-count").order_by("-sort_number")


        if "available" in url_params:
            if url_params["available"] == ["on"]:
                available = True
            else:
                available = False
        else:
            available = False

        # handle the search query

        have_search_query = False
        if "search" in url_params:
            search = url_params["search"]
            if len(search) == 1 and not search[0].isspace():
                search = search[0]
                if search.isalnum():
                    have_search_query = True
                else:
                    search = None
            else:
                search = None
        else:
            search = None

        # handle the price range

        have_start_price = False
        start_price = None
        if "start_price" in url_params:
            start_price = url_params["start_price"]
            if len(start_price) == 1:
                start_price = start_price[0]
                if start_price.isdigit():
                    have_start_price = True
            else:
                start_price = None

        have_end_price = False
        end_price = None
        if "end_price" in url_params:
            end_price = url_params["end_price"]

            if len(end_price) == 1:
                end_price = end_price[0]
                if end_price.isdigit():
                    have_end_price = True
            else:
                end_price = None

        # get the url params if exist

        if "category" in url_params:
            products = products.filter(
                Q(category_id__in=url_params["category"]),
                Q(category__is_active=True),
            )

        if "store" in url_params:
            products = products.filter(store_id__in=url_params["store"])

        if "brand" in url_params:
            products = products.filter(
                Q(brand_id__in=url_params["brand"]),
                Q(brand__is_active=True)
            )

        if available:
            products = products.filter(count__gte=1)

        if have_start_price and start_price:
            products = products.filter(price__gte=start_price)

        if have_end_price and end_price:
            products = products.filter(price__lte=end_price)

        if have_search_query and search is not None:
            products = products.filter(
                Q(name__icontains=search) |
                Q(specs__name__icontains=search) |
                Q(tags__name__icontains=search) |
                Q(features__title__icontains=search)
            )

        sort = None
        if "sort" in url_params:
            sort = url_params["sort"]
            if len(sort) == 1:
                sort = sort[0]
                if sort.isdigit():
                    sort = int(sort)
                    if 1 <= sort <= 5:
                        if sort == 1:
                            products = products.order_by( '-have_discount','-discount')
                        elif sort == 2:
                            products = products.order_by("orders__count").distinct()
                        elif sort == 3:
                            products = products.order_by("price")
                        elif sort == 4:
                            products = products.order_by("-price")
                        elif sort == 5:
                            products = products.order_by("-id")
                    else:
                        sort = None
                else:
                    sort = None
            else:
                sort = None


        return products.distinct().all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = (
            ProductCategory.objects.exclude(parent__isnull=False)
            .prefetch_related("child")
            .order_by("-sort_number")
            .all()
        )

        context["stores"] = (
            Store.objects.filter(is_active=True, products__count__gt=0, is_verified=True)
            .order_by("-sort_number").distinct()
            .all()
        )

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
    model = Product
    context_object_name = "product"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                is_active=True,
                store__is_active=True,
                store__is_verified=True,
                admin_verified=True,
                brand__is_active=True,
                category__is_active=True,
            )
            .prefetch_related("features")
            .prefetch_related("tags")
            .prefetch_related("specs")
        )

    def get_context_data(self, **kwargs):

        try:
            ip, is_rout = get_client_ip(self.request)
            product_view_object = ProductViews.objects.get_or_create(
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

        # check if the product is the user favorite or not
        if self.request.user.is_authenticated:
            is_favorite_product = UserFavorite.objects.filter(
                user=self.request.user, product=self.object
            ).exists()

        else:
            is_favorite_product = False
        context = super().get_context_data(**kwargs)
        context["is_favorite_product"] = is_favorite_product

        # get the product comments and add comment form

        context["comment_form"] = ProductCommentForm()
        comments = (
            self.object.comments.annotate(
                like_count=Count("like", filter=Q(like__like=True)),
                dislike_count=Count("like", filter=Q(like__like=False)),
            )
            .order_by("-id")
            .all()[0:50]
        )
        context["comments"] = comments

        # get the same product
        obj = self.object
        same_product = (
            Product.objects.filter(
                Q(is_active=True), Q(admin_verified=True) |
                Q(brand=obj.brand) , Q(brand__is_active=True) |
                Q(category=obj.category) , Q(category__is_active=True) |
                Q(tags__name=obj.tags.name)
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
