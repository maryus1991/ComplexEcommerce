from django.contrib import messages
from django.db.models.aggregates import Count
from django.views.generic import ListView, UpdateView, CreateView, RedirectView, View
from django.shortcuts import get_object_or_404, redirect, reverse, render
from stores.forms import AddBrandForm, AddCategoryForm
from admin_panel.forms import AddProductForm
from django.urls import reverse_lazy
from user.mixins.logins import AdminUserMixin
from orders.models import OrderDetail
from product.models import (
    Product,
    ProductCategory,
    ProductBrand,
    ProductGallery,
    ProductSpecifications,
    ProductFeature,
    ProductTag,
UserFavorite
)
from admin_panel.search_forms import ProductSearchForm
from stores.forms import BrandAndCategorySearchForm

# product

class ProductSetSortNumber(AdminUserMixin, RedirectView):
    """for set sort number"""
    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs['pk']
        obj = get_object_or_404(Product, pk=pk)
        sort_num = self.request.POST.get(f'{obj.pk}')

        try:
            sort_num = int(sort_num)
        except  Exception as e:
            messages.error(
                self.request,
                'عدد وارد شده باید بین 0 تا 100,000,000 باشد'
            )
            return self.request.META.get('HTTP_REFERER')


        if 0 <= sort_num <= 100_000_000:
            obj.sort_number = sort_num
            obj.save()

            messages.success(
                self.request,
                'ترتیب اعمال شد'
            )
        else:
            messages.error(
                self.request,
                'عدد وارد شده باید بین 0 تا 100,000,000 باشد'
            )

        return self.request.META.get('HTTP_REFERER')


class ProductListView(AdminUserMixin, ListView):
    """for listing products"""

    model = Product
    context_object_name = "items"
    paginate_by = 100
    template_name = "admin_panel/product/list.html"
    ordering = ["-id"]

    def get_queryset(self):

        queryset = Product.objects.prefetch_related(
            "category", 'comments' ,"brand", "store",
            "views", 'features', 'tags', 'specs').order_by('-id')

        # Process search parameters if form is valid
        params = ProductSearchForm(self.request.GET or None)


        if not params.is_valid():
            return queryset

        cleaned_data = params.cleaned_data

        #  store
        if store := cleaned_data.get("store"):
            queryset = queryset.filter(store_id=store)

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
        context['search_form'] = ProductSearchForm()
        return context


class ProductCreateView(AdminUserMixin, CreateView):
    """
    for creating a products
    """

    model = Product
    form_class = AddProductForm
    template_name = "admin_panel/product/create.html"
    success_url = reverse_lazy("admin_panel:product-list")

    def form_valid(self, form):
        gallery = form.cleaned_data["gallery"]
        product = Product.objects.create(
            store=form.cleaned_data["store"],
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
            length=form.cleaned_data["length"],
            width=form.cleaned_data["width"],
            height=form.cleaned_data["height"],
            sort_number=form.cleaned_data["sort_number"],
            sort_number_newest_products=form.cleaned_data["sort_number_newest_products"],
            sort_number_most_sell=form.cleaned_data["sort_number_most_sell"],
            sort_number_discount=form.cleaned_data["sort_number_discount"],
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

        messages.success(self.request, "محصول شما با موفقیت ساخته شد")
        product.save()
        return redirect(reverse("admin_panel:product-update", kwargs={'pk': product.id}))
    
    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["category_form"] = AddCategoryForm()
        context["brand_form"] = AddBrandForm()

        return context


class ProductUpdateView(AdminUserMixin, UpdateView):
    """
    for updating a product
    """

    model = Product
    form_class = AddProductForm
    template_name = "admin_panel/product/create.html"
    success_url = reverse_lazy("admin_panel:product-list")
    context_object_name = "product"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .prefetch_related("features", "tags", "specs", "gallery", "store")
        )
        return queryset

    def form_valid(self, form):

        store = self.request.user.store
        product = Product.objects.get(pk=self.kwargs.get("pk"), store=store)
        product.name = form.cleaned_data["name"]
        product.description = form.cleaned_data["description"]
        product.price = form.cleaned_data["price"]
        product.have_discount = form.cleaned_data["have_discount"]
        product.discount = form.cleaned_data["discount"]
        product.count = form.cleaned_data["count"]
        product.weight = form.cleaned_data["weight"]
        product.brand = form.cleaned_data["brand"]
        product.category = form.cleaned_data["category"]

        product.length=int(form.cleaned_data.get("length"))
        product.width=int(form.cleaned_data.get("width"))
        product.height=int(form.cleaned_data.get("height"))
        product.sort_number=int(form.cleaned_data.get("sort_number"))
        product.sort_number_newest_products=int(form.cleaned_data.get("sort_number_newest_products"))
        product.sort_number_most_sell=int(form.cleaned_data.get("sort_number_most_sell"))
        product.sort_number_discount=int(form.cleaned_data.get("sort_number_discount"))

        if form.cleaned_data["picture"]:  # اگر تصویر جدید ارسال شده است
            product.picture = form.cleaned_data["picture"]

        product.save()

        product = self.get_object()

        gallery = form.cleaned_data["gallery"]

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
        return redirect(reverse("admin_panel:product-update", kwargs={'pk': product.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["category_form"] = AddCategoryForm()
        context["brand_form"] = AddBrandForm()

        return context


class ProductActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """
    for active or deactivate product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = kwargs.get("pk")
        product = get_object_or_404(Product, pk=product_id)
        if product.is_active:
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
        else:
            product.is_active = True
            product.save()
            messages.success(self.request, "ایتم مورد نظر فعال شد")

        return reverse_lazy("admin_panel:product-list")


class ProductAdminVerifiedView(AdminUserMixin, RedirectView):
    """
    for admin verify product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = kwargs.get("pk")
        product = get_object_or_404(Product, pk=product_id)
        if product.admin_verified:
            product.admin_verified = False
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
            messages.warning(self.request, "ایتم مورد نظر مورد تایید ادمین قرار نگرفت و از تمامی سبد خرید ها حذف شد")
        else:
            product.admin_verified = True
            product.save()
            messages.success(self.request, "ایتم مورد نظر مورد تایید ادمین قرار گرفت")

        return reverse_lazy("admin_panel:product-list")


class ProductDeleteView(AdminUserMixin, View):
    """
    for delete product
    """

    def get(self, *args, **kwargs):
        obj = get_object_or_404(Product, pk=kwargs.get("pk"))
        messages.warning(self.request, "بهتر است به جای حذف محصول ان را غیر فعال کنید")
        return render(self.request, "admin_panel/product/delete.html", {"item": obj})

    def post(self, *args, **kwargs):
        obj = get_object_or_404(Product, pk=kwargs.get("pk"))
        conform = self.request.POST.get("conform")

        if conform == "delete":
            obj.delete()
            messages.info(self.request, "محصول حذف شد")
        else:
            messages.warning(self.request, "در وارد کردن عبارت دقت فرمایید")

        return redirect("admin_panel:product-list")


class StoreEditProductRemoveImg(AdminUserMixin, RedirectView):
    """
    for remove img in editing product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = kwargs.get("pk")
        img_id = kwargs.get("img_id")
        product = get_object_or_404(Product, id=product_id)
        img = get_object_or_404(ProductGallery, id=img_id, product=product)
        img.delete()
        messages.success(self.request, "عکس مورد نظر حذف شد")
        return self.request.META.get("HTTP_REFERER", "/")


# category


class ProductCategoryListView(AdminUserMixin, ListView):
    """for listing product categories"""

    model = ProductCategory
    template_name = "admin_panel/product/category/list.html"
    ordering = "-id"
    paginate_by = 25
    context_object_name = "items"

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




class ProductCategoryChangeSortNumber(AdminUserMixin, RedirectView):
    """for change sort number product categories"""

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        category = get_object_or_404(ProductCategory, pk=pk)
        sort_number = self.request.POST[f'{pk}']

        try:
            sort_number = int(sort_number)
            if 1000 >= sort_number >= 0:
                category.sort_number = sort_number
                category.save()
                messages.success(
                    self.request,
                    'ثبت شد'
                )
                print(sort_number, type(sort_number))
                return reverse("admin_panel:product-category-list")

            else:
                messages.error(
                    self.request,
                    'عدد وارد شده باید بین 0 الی 1000 باشد'
                )
        except Exception as e:
            messages.error(
                self.request,
                'در وارد کردن عدد دقت فرمایید'
            )

        return reverse("admin_panel:product-category-list")


class ProductCategoryCreateView(AdminUserMixin, CreateView):
    """
    for creating a category for products
    """

    model = ProductCategory
    form_class = AddCategoryForm
    template_name = "admin_panel/product/category/create.html"
    success_url = reverse_lazy("admin_panel:product-category-list")

    def form_valid(self, form):
        messages.success(self.request, "ایتم شما با موفقیت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class ProductCategoryUpdateView(AdminUserMixin, UpdateView):
    """
    for updating a category for products
    """

    model = ProductCategory
    form_class = AddCategoryForm
    template_name = "admin_panel/product/category/create.html"
    success_url = reverse_lazy("admin_panel:product-category-list")
    context_object_name = "item"

    def form_valid(self, form):
        messages.success(self.request, "ایتم شما با موفقیت بروزرسانی شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class ProductCategoryActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """
    for active or deactivate category for products
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        category = get_object_or_404(ProductCategory, pk=pk)
        if category.is_active:
            category.is_active = False
            category.save()
            messages.success(self.request, "دسته مورد نظر غیر فعال شد")
        else:
            category.is_active = True
            category.save()
            messages.success(self.request, "دسته مورد نظر فعال شد")

        return reverse_lazy("admin_panel:product-category-list")


class ProductCategoryDeleteView(AdminUserMixin, View):
    """
    for delete category
    """

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(ProductCategory, pk=kwargs.get("pk"))
        messages.warning(request, "بهتر است به جای حذف کردن دسته را غیر فعال کنید")
        return render(
            request, "admin_panel/product/category/delete.html", {"item": obj}
        )

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(ProductCategory, pk=kwargs.get("pk"))
        conform = request.POST.get("conform")

        if conform == "delete":
            obj.delete()
            messages.info(request, "ایتم مورد نظر حذف شد")
        else:
            messages.warning(request, "در وارد کردن عبارت دقت فرمایید")

        return redirect("admin_panel:product-category-list")


# brand


class ProductBrandListView(AdminUserMixin, ListView):
    """for listing product brands"""

    model = ProductBrand
    context_object_name = "items"
    paginate_by = 25
    template_name = "admin_panel/product/brand/list.html"
    ordering = "-id"

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


class ProductBrandChangeSortNumber(AdminUserMixin, RedirectView):
    """for change sort number product Brand"""

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        brand = get_object_or_404(ProductBrand, pk=pk)
        sort_number = self.request.POST[f'{pk}']

        try:
            sort_number = int(sort_number)
            if 1000 >= sort_number >= 0:
                brand.sort_number = sort_number
                brand.save()
                messages.success(
                    self.request,
                    'ثبت شد'
                )
                return reverse("admin_panel:product-brand-list")

            else:
                messages.error(
                    self.request,
                    'عدد وارد شده باید بین 0 الی 1000 باشد'
                )
        except Exception as e:
            messages.error(
                self.request,
                'در وارد کردن عدد دقت فرمایید'
            )

        return reverse("admin_panel:product-brand-list")


class ProductBrandCreateView(AdminUserMixin, CreateView):
    """
    for creating a brands for products
    """

    model = ProductBrand
    form_class = AddBrandForm
    template_name = "admin_panel/product/brand/create.html"
    success_url = reverse_lazy("admin_panel:product-brand-list")

    def form_valid(self, form):
        messages.success(self.request, "برند مورد نظر با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class ProductBrandUpdateView(AdminUserMixin, UpdateView):
    """
    for updating a slider
    """

    model = ProductBrand
    form_class = AddBrandForm
    template_name = "admin_panel/product/brand/create.html"
    success_url = reverse_lazy("admin_panel:product-brand-list")
    context_object_name = "item"

    def form_valid(self, form):
        messages.success(self.request, "برند با موفقت بروز رسانی شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class ProductBrandActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """
    for active or deactivate slider
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        brand = get_object_or_404(ProductBrand, pk=pk)
        if brand.is_active:
            brand.is_active = False
            brand.save()
            messages.success(self.request, "برند مورد نظر غیر فعال شد")
        else:
            brand.is_active = True
            brand.save()
            messages.success(self.request, "برند مورد نظر فعال شد")

        return reverse_lazy("admin_panel:product-brand-list")


class ProductBrandDeleteView(AdminUserMixin, View):
    """
    for delete brand
    """

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(ProductBrand, pk=kwargs.get("pk"))
        messages.warning(request, "بهتر است به جای حذف کردن برند را غیر فعال کنید")
        return render(request, "admin_panel/product/brand/delete.html", {"item": obj})

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(ProductBrand, pk=kwargs.get("pk"))
        conform = request.POST.get("conform")

        if conform == "delete":
            obj.delete()
            messages.info(request, "ایتم مورد نظر حذف شد")
        else:
            messages.warning(request, "در وارد کردن عبارت دقت فرمایید")

        return redirect("admin_panel:product-brand-list")
