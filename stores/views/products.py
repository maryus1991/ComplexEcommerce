from django.views.generic import (
    ListView,
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
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from stores.models import Store

from stores.forms import (
    AddProductForm,
    AddBrandForm,
    AddCategoryForm,
    AddStoreBlogCategoryForm,
    ProductSearchForm,
    BrandAndCategorySearchForm,
)
from product.models import (
    Product,
    ProductTag,
    ProductFeature,
    ProductGallery,
    ProductBrand,
    ProductCategory,
    ProductSpecifications,
    UserFavorite
)
from orders.models import OrderDetail



from user.mixins.logins import UserStoreStaffMixin, StoreAdminUserStaff



class StoreProductListView(UserStoreStaffMixin, ListView):
    """
    for listing the products of store
    """

    template_name = "store/product/product_list.html"
    ordering = "-id"
    paginate_by = 50
    context_object_name = "products"

    def get_queryset(self):
        # Base queryset

        queryset = Product.objects.filter(
            store=self.request.user.store
        ).prefetch_related("comments", "views").order_by('-id')

        # Process search parameters if form is valid
        params = ProductSearchForm(self.request.GET or None)

        if not params.is_valid():
            return queryset

        cleaned_data = params.cleaned_data

        # Boolean filters
        if cleaned_data.get("is_active"):
            is_active = cleaned_data.get("is_active")

            if is_active == "0":
                queryset = queryset.filter(is_active=False)
            elif is_active == "1":
                queryset = queryset.filter(is_active=True)

        if cleaned_data.get("admin_verify"):
            is_active = cleaned_data.get("admin_verify")

            if is_active == "0":
                queryset = queryset.filter(admin_verified=False)
            elif is_active == "1":
                queryset = queryset.filter(admin_verified=True)

        if cleaned_data.get("have_discount"):
            have_discount = cleaned_data.get("have_discount")

            if have_discount == "0":
                queryset = queryset.filter(have_discount=False)
            elif have_discount == "1":
                queryset = queryset.filter(have_discount=True)

        # Text search
        if name := cleaned_data.get("name"):
            queryset = queryset.filter(
                Q(name__icontains=name) | Q(description__icontains=name)
            )

        # Numeric range filters
        range_filters = {
            "discount": ("discount_min", "discount_max"),
            "count": ("count_min", "count_max"),
            "weight": ("weight_min", "weight_max"),
            "price": ("price_min", "price_max"),
            "height": ("height_min", "height_max"),
            "length": ("length_min", "length_max"),
            "width": ("width_min", "width_max"),
        }

        for field, (min_key, max_key) in range_filters.items():
            if min_val := cleaned_data.get(min_key):
                queryset = queryset.filter(**{f"{field}__gte": min_val})
            if max_val := cleaned_data.get(max_key):
                queryset = queryset.filter(**{f"{field}__lte": max_val})

        # Foreign key filters
        if category := cleaned_data.get("category"):
            queryset = queryset.filter(category_id=category)

        if brand := cleaned_data.get("brand"):
            queryset = queryset.filter(brand_id=brand)

        # Many-to-many filters
        if features := cleaned_data.get("feature"):
            # Clean and split features while handling edge cases
            features = [
                feature.strip() for feature in features.split("-") if feature.strip()
            ]

            # Create a single query with multiple conditions
            query = Q()
            for item in features:
                query |= Q(features__title__icontains=item)

            # Apply the combined filter once
            queryset = queryset.filter(query).distinct()

        if tags := cleaned_data.get("tag"):
            # Clean and split features while handling edge cases
            tags = [tags.strip() for tag in tags.split("-") if tag.strip()]

            # Create a single query with multiple conditions
            query = Q()
            for item in tags:
                query |= Q(tags__name__icontains=item)

            # Apply the combined filter once
            queryset = queryset.filter(query).distinct()

        if ordering := cleaned_data.get("ordering"):
            if ordering == "11":
                queryset = queryset.annotate(views_count=Count("views")).order_by(
                    "-views_count"
                )  # بیشترین بازدید
            elif ordering == "12":
                queryset = queryset.annotate(views_count=Count("views")).order_by(
                    "views_count"
                )  # کمترین بازدید
            elif ordering == "21":
                queryset = queryset.order_by("-price")  # بیشترین قیمت
            elif ordering == "22":
                queryset = queryset.order_by("price")  # کمترین قیمت
            elif ordering == "31":
                queryset = queryset.annotate(comments_count=Count("comments")).order_by(
                    "-comments_count"
                )  # بیشترین تعداد کامنت
            elif ordering == "32":
                queryset = queryset.annotate(comments_count=Count("comments")).order_by(
                    "comments_count"
                )  # کمترین  تعداد کامنت
            elif ordering == "41":
                queryset = queryset.order_by("-count")  # بیشترین موجودی کالا
            elif ordering == "42":
                queryset = queryset.order_by("count")  # کمترین موجودی کالا

        return queryset.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ProductSearchForm(self.request.GET)
        return context


class StoreAddProduct(UserStoreStaffMixin, FormView):
    """
    for add product
    """

    template_name = "store/product/add_product.html"
    form_class = AddProductForm
    success_url = reverse_lazy("store:list-product")

    def form_valid(self, form):
        store = self.request.user.store
        gallery = form.cleaned_data["gallery"]
        product = Product.objects.create(
            store=store,
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            price=form.cleaned_data["price"],
            have_discount=form.cleaned_data["have_discount"],
            discount=form.cleaned_data["discount"],
            picture=form.cleaned_data["picture"],
            count=form.cleaned_data["count"],
            weight=form.cleaned_data["weight"],
            brand=form.cleaned_data["brand"],
            category=form.cleaned_data["category"],
        )
        tags = form.cleaned_data["tags"].split("**")
        features = form.cleaned_data["features"].split("**")
        specs = form.cleaned_data["specs"].split("**")

        for img in gallery:
            ProductGallery.objects.create(product=product, image=img).save()

        if specs:
            ProductSpecifications.objects.filter(product=product).all().delete()

            for spec in specs:
                if spec.isalnum and spec != " " and spec != "" and spec is not None:
                    if len(spec) <= 999:
                        ProductSpecifications.objects.create(product=product, name=spec)

                    else:
                        messages.warning(
                            self.request,
                            'تگ زیر ذخیره نشده است به دلیل بالای 1000 کاراکتر بودن'
                        )
                        messages.warning(
                            self.request,
                            f'{spec}'

                        )
                else:
                    if spec != " " and spec != "" and spec is not None:
                        messages.warning(
                            self.request,
                            f"{spec} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید",
                        )

        if features:
            ProductFeature.objects.filter(product=product).all().delete()

            for feature in features:
                if (
                        feature.isalnum and
                        feature != " " and
                        feature != "" and
                        feature is not None
                ):
                    if len(feature) <= 999:
                        ProductFeature.objects.create(product=product, title=feature)

                    else:
                        messages.warning(
                            self.request,
                            'ویژگی زیر ذخیره نشده است به دلیل بالای 1000 کاراکتر بودن'
                        )
                        messages.warning(
                            self.request,
                            f'{feature}'

                        )

                else:
                    if feature != " " and feature != "" and feature is not None:
                        messages.warning(
                            self.request,
                            f"{feature} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید",
                        )

        if tags:
            ProductTag.objects.filter(Product=product).all().delete()

            for tag in tags:
                if tag.isalnum and tag != " " and tag != "" and tag is not None:
                    if len(tag) <= 999:
                        ProductTag.objects.create(Product=product, name=tag)
                    else:
                        messages.warning(
                            self.request,
                            'تگ زیر ذخیره نشده است به دلیل بالای 1000 کاراکتر بودن'
                        )
                        messages.warning(
                            self.request,
                            f'{tag}'
                        )

                else:
                    if tag != " " and tag != "" and tag is not None:
                        messages.warning(
                            self.request,
                            f"{tag} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید",
                        )

        messages.success(self.request, "محصول شما با موفقیت ذخیره شد")
        product.save()
        return redirect("store:list-product")


    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["category_form"] = AddCategoryForm()
        context["brand_form"] = AddBrandForm()

        return context


class StoreEditProductView(UserStoreStaffMixin, UpdateView):
    """
    for edit product
    """

    form_class = AddProductForm
    model = Product
    template_name = "store/product/add_product.html"
    success_url = reverse_lazy("store:list-product")

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .prefetch_related("features")
            .prefetch_related("tags")
            .prefetch_related("specs")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = self.get_object()
        context["category_form"] = AddCategoryForm()
        context["brand_form"] = AddBrandForm()
        return context

    def form_valid(self, form):

        gallery = form.cleaned_data["gallery"]

        product = Product.objects.get(pk=self.kwargs.get("pk"))
        product.name = form.cleaned_data["name"]
        product.description = form.cleaned_data["description"]
        product.price = form.cleaned_data["price"]
        product.have_discount = form.cleaned_data["have_discount"]
        product.discount = form.cleaned_data["discount"]
        product.count = form.cleaned_data["count"]
        product.weight = form.cleaned_data["weight"]
        product.brand = form.cleaned_data["brand"]
        product.category = form.cleaned_data["category"]

        if form.cleaned_data["picture"]:  # اگر تصویر جدید ارسال شده است
            product.picture = form.cleaned_data["picture"]

        product.save()

        product = self.get_object()

        for img in gallery:
            ProductGallery.objects.create(product=product, image=img).save()

        tags = form.cleaned_data["tags"].split("**")
        features = form.cleaned_data["features"].split("**")
        specs = form.cleaned_data["specs"].split("**")

        if specs:
            ProductSpecifications.objects.filter(product=product).all().delete()

            for spec in specs:
                if spec.isalnum and spec != " " and spec != "" and spec is not None:
                    if len(spec) <= 999:
                        ProductSpecifications.objects.create(product=product, name=spec)

                    else:
                        messages.warning(
                            self.request,
                            'تگ زیر ذخیره نشده است به دلیل بالای 1000 کاراکتر بودن'
                        )
                        messages.warning(
                            self.request,
                            f'{spec}'

                        )
                else:
                    if spec != " " and spec != "" and spec is not None:
                        messages.warning(
                            self.request,
                            f"{spec} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید",
                        )

        if features:
            ProductFeature.objects.filter(product=product).all().delete()

            for feature in features:
                if (
                        feature.isalnum and
                        feature != " " and
                        feature != "" and
                        feature is not None
                ):
                    if len(feature) <= 999:
                        ProductFeature.objects.create(product=product, title=feature)

                    else:
                        messages.warning(
                            self.request,
                            'ویژگی زیر ذخیره نشده است به دلیل بالای 1000 کاراکتر بودن'
                        )
                        messages.warning(
                            self.request,
                            f'{feature}'

                        )

                else:
                    if feature != " " and feature != "" and feature is not None:
                        messages.warning(
                            self.request,
                            f"{feature} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید",
                        )

        if tags:
            ProductTag.objects.filter(Product=product).all().delete()

            for tag in tags:
                if tag.isalnum and tag != " " and tag != "" and tag is not None:
                    if len(tag) <= 999:
                        ProductTag.objects.create(Product=product, name=tag)
                    else:
                        messages.warning(
                            self.request,
                            'تگ زیر ذخیره نشده است به دلیل بالای 1000 کاراکتر بودن'
                        )
                        messages.warning(
                            self.request,
                            f'{tag}'
                        )

                else:
                    if tag != " " and tag != "" and tag is not None:
                        messages.warning(
                            self.request,
                            f"{tag} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید",
                        )

        messages.success(self.request, "تغییرات با موفقیت ثبت شد")
        product.save()
        return redirect("store:list-product")


class StoreEditProductRemoveImg(UserStoreStaffMixin, RedirectView):
    """
    for remove img in editing product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = self.kwargs.get("pk")
        img_id = self.kwargs.get("img_id")
        product = get_object_or_404(
            Product, id=product_id, store=self.request.user.store
        )
        img = get_object_or_404(ProductGallery, id=img_id, product=product)
        img.delete()
        messages.success(self.request, "عکس مورد نظر حذف شد")
        return self.request.META.get("HTTP_REFERER", "/")


class StoreEditActiveOrDeactivateProduct(UserStoreStaffMixin, RedirectView):
    """
    for active or deactivate product in editing product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = self.kwargs.get("pk")

        product = get_object_or_404(
            Product, id=product_id, store=self.request.user.store
        )
        if product.is_active is True:
            product.is_active = False
            product.save()
            OrderDetail.objects.filter(
                product=product,
                order__is_active=True,
                order__is_paid=False,
                order__canceled=False,
                order__Authority__isnull=True,
                order__vip_post=False,
                order__tipax_post_delivery=False,
                order__in_city_delivery=False,
                order__physical_delivery=False,
            ).delete()
            UserFavorite.objects.filter(product=product).delete()
            messages.warning(self.request, "ایتم مورد نظر غیر فعال شد و از تمامی سبد خرید ها حذف شد")
        elif product.is_active is False:
            product.is_active = True
            messages.success(self.request, "محصول مورد نظر فعال شد")
        product.save()
        return self.request.META.get("HTTP_REFERER", "/")


class StoreDeleteProductView(StoreAdminUserStaff, View):
    """
    for delete product
    """

    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get("pk")
        product = get_object_or_404(
            Product, id=product_id, store=self.request.user.store
        )
        messages.warning(
            self.request,
            "با حذف محصول تمام اطلاعات زیر مجموعه ان پاک خواهد شد بهتر است محصول را غیر فعال کنید تا از حذف شدن اطلاعات جلوگیری کنید",
        )
        return render(
            request, "store/product/delete_product_conform.html", {"product": product}
        )

    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get("pk")
        product = get_object_or_404(
            Product, id=product_id, store=self.request.user.store
        )
        product_name = request.POST.get("conform")
        if product_name is not None and product_name != " " and product_name.isalnum():
            if product_name == product.name:
                product.delete()
                messages.success(self.request, "محصول شما حذف شد")
                return redirect(reverse("store:list-product"))
            else:
                messages.warning(
                    self.request, "نام محصول ارسالی با نام اصلی محصول یک سان نیست"
                )
        else:
            messages.warning(self.request, "لطفا در ارسال نام محصول دقت کنید")

        return redirect(request.META.get("HTTP_REFERER", "/"))


class ListBrandView(UserStoreStaffMixin, ListView):
    """
    for list the brands
    """

    model = ProductBrand
    template_name = "store/product/brand/list_brand.html"
    paginate_by = 25
    context_object_name = "brands"

    def get_queryset(self):
        query = (
            super()
            .get_queryset()
            .order_by("name")
            .prefetch_related("products")
            .annotate(product_count=Count("products"))
        )

        params = BrandAndCategorySearchForm(self.request.GET)
        if not params.is_valid():
            return query

        cleaned_params = params.cleaned_data

        if name := cleaned_params.get("name"):
            query = query.filter(name__icontains=name)

        if is_active := cleaned_params.get("is_active"):
            if is_active == "1":
                query = query.filter(is_active=True)
            elif is_active == "0":
                query = query.filter(is_active=False)

        if ordering := cleaned_params.get("ordering"):

            if ordering == "41":  # بیشترین تعداد کالا
                query = query.order_by("-product_count").distinct()
            elif ordering == "42":  # کمترین تعداد کالا
                query = query.order_by("product_count").distinct()
            elif ordering == "51":  # جدید ترین
                query = query.order_by("-id")
            elif ordering == "52":  # قدیمی ترین
                query = query.order_by("id")

        return query

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)

        context["form"] = BrandAndCategorySearchForm()

        return context


class StoreAddBrandView(UserStoreStaffMixin, CreateView):
    """
    for add brand
    """

    form_class = AddBrandForm
    model = ProductBrand
    template_name = "store/product/brand/add_brand.html"
    success_url = reverse_lazy("store:list-brands")

    def form_valid(self, form):
        messages.success(self.request, "برند شما ساخته شد")
        form.save()
        return redirect(self.request.META.get("HTTP_REFERER", "/"))


class StoreListCategoryView(UserStoreStaffMixin, ListView):
    """
    for list the categories
    """

    model = ProductCategory
    template_name = "store/product/category/list_category.html"
    paginate_by = 25
    context_object_name = "categories"

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, '')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = (
            super()
            .get_queryset()
            .order_by("name")
            .prefetch_related("products")
            .prefetch_related("child")
            .annotate(product_count=Count("products"))
        )

        form = BrandAndCategorySearchForm(self.request.GET)

        if not form.is_valid():
            return query

        cleaned_params = form.cleaned_data

        if name := cleaned_params.get("name"):
            query = query.filter(name__icontains=name)

        if is_active := cleaned_params.get("is_active"):
            if is_active == "1":
                query = query.filter(is_active=True)
            elif is_active == "0":
                query = query.filter(is_active=False)

        if ordering := cleaned_params.get("ordering"):
            if ordering == "41":  # بیشترین تعداد کالا
                query = query.order_by("-product_count").distinct()
            elif ordering == "42":  # کمترین تعداد کالا
                query = query.order_by("product_count").distinct()
            elif ordering == "51":  # جدید ترین
                query = query.order_by("-id")
            elif ordering == "52":  # قدیمی ترین
                query = query.order_by("id")

        if parent := cleaned_params.get("category_parent"):
            query = query.filter(parent_id=parent)

        return query.all()

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)

        context["form"] = BrandAndCategorySearchForm()

        return context


class StoreAddCategoryView(UserStoreStaffMixin, CreateView):
    """
    for add category for store
    """

    form_class = AddCategoryForm
    model = ProductCategory
    template_name = "store/product/category/add_category.html"
    success_url = reverse_lazy("store:list-category")

    def form_valid(self, form):
        messages.success(self.request, "دسته شما ساخته شد")
        form.save()
        return redirect(self.request.META.get("HTTP_REFERER", "/"))
