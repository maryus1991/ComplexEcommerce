from django.contrib import messages
from django.views.generic import ListView, UpdateView, CreateView, RedirectView, View
from django.shortcuts import get_object_or_404, redirect, reverse, render
from stores.forms import AddBrandForm, AddCategoryForm
from admin_panel.forms import AddProductForm
from django.urls import reverse_lazy
from user.mixins.logins import AdminUserMixin

from product.models import (
    Product,
    ProductCategory,
    ProductBrand,
    ProductGallery,
    ProductSpecifications,
    ProductFeature,
    ProductTag,
)

# product


class ProductListView(AdminUserMixin, ListView):
    """for listing products"""

    model = Product
    context_object_name = "items"
    paginate_by = 35
    template_name = "admin_panel/product/list.html"
    ordering = ["-id"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("category", "brand", "store", "views")
        )


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
                    ProductSpecifications.objects.create(product=product, name=spec)
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
                    ProductFeature.objects.create(product=product, title=feature)
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
                    ProductTag.objects.create(Product=product, name=tag)
                else:
                    if tag != " " and tag != "" and tag is not None:
                        messages.warning(
                            self.request,
                            f"{tag} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید",
                        )

        messages.success(self.request, "محصول شما با موفقیت شاخته شد")
        product.save()
        return redirect(self.success_url)

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

        gallery = form.cleaned_data["gallery"]
        product = Product.objects.filter(pk=self.kwargs.get("pk")).update(
            name=form.cleaned_data["name"],
            store=form.cleaned_data["store"],
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
                    ProductSpecifications.objects.create(product=product, name=spec)
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
                    ProductFeature.objects.create(product=product, title=feature)
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
                    ProductTag.objects.create(Product=product, name=tag)
                else:
                    if tag != " " and tag != "" and tag is not None:
                        messages.warning(
                            self.request,
                            f"{tag} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید",
                        )

        messages.success(self.request, "تغییرات با موفقیت ثبت شد")
        product.save()
        return redirect(self.success_url)

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
            messages.warning(self.request, "ایتم مورد نظر غیر فعال شد")
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
            messages.warning(self.request, "ایتم مورد نظر مورد تایید ادمین قرار نگرفت")
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
        return self.model.objects.prefetch_related(
            "products", "parent", "child"
        ).order_by(self.ordering)


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
        return super().get_queryset().prefetch_related("products")


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
