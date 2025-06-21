from django.views.generic import ListView, UpdateView, CreateView, RedirectView, View
from django.shortcuts import get_object_or_404, redirect, reverse, render
from stores.forms import AddProductForm, AddBrandForm ,AddCategoryForm
from product.models import Product, ProductCategory, ProductBrand
from django.urls import reverse_lazy

from user.mixins.logins import AdminUserMixin

# product

class ProductListView(AdminUserMixin, ListView):
    """for listing products"""
    model = Product
    context_object_name = 'items'
    paginate_by = 35
    template_name = 'admin_panel/product/list.html'

class ProductCreateView(AdminUserMixin, CreateView):
    """
    for creating a products
    """
    model = Product
    form_class = AddProductForm
    template_name = 'admin_panel/product/create.html'
    success_url = reverse_lazy('admin_panel:product-list')

class ProductUpdateView(AdminUserMixin, UpdateView):
    """
    for updating a product
    """
    model = Product
    form_class = AddProductForm
    template_name = 'admin_panel/product/create.html'
    success_url = reverse_lazy('admin_panel:product-list')
    context_object_name = 'item'

class ProductActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """
    for active or deactivate product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        if product.is_active:
            product.is_active = False
            product.save()
            messages.success(
                self.request,
                'ایتم مورد نظر غیر فعال شد'
            )
        else:
            product.is_active = True
            product.save()
            messages.success(
                self.request,
                'ایتم مورد نظر فعال شد'
            )

        return reverse_lazy('admin_panel:product-list')

class ProductAdminVerifiedView(AdminUserMixin, RedirectView):
    """
    for admin verify product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        if product.admin_verified:
            product.admin_verified = False
            product.save()
            messages.success(
                self.request,
                'ایتم مورد نظر مورد تایید ادمین قرار نگرفت'
            )
        else:
            product.admin_verified = True
            product.save()
            messages.success(
                self.request,
                'ایتم مورد نظر مورد تایید ادمین قرار گرفت'
            )

        return reverse_lazy('admin_panel:product-list')

class ProductDeleteView(AdminUserMixin, View):
    """
    for delete product
    """
    pass


# category

class ProductCategoryListView(AdminUserMixin, ListView):
    """for listing product categories"""
    model = ProductCategory
    ProductCategory = 'items'
    paginate_by = 25
    template_name = 'admin_panel/product/category/list.html'

class ProductCategoryCreateView(AdminUserMixin, CreateView):
    """
    for creating a category for products
    """
    model = ProductCategory
    form_class = AddCategoryForm
    template_name = 'admin_panel/product/category/create.html'
    success_url = reverse_lazy('admin_panel:product-category-list')

class ProductCategoryUpdateView(AdminUserMixin, UpdateView):
    """
    for updating a category for products
    """
    model = ProductCategory
    form_class = AddCategoryForm
    template_name = 'admin_panel/product/category/create.html'
    success_url = reverse_lazy('admin_panel:product-category-list')
    context_object_name = 'item'

class ProductCategoryActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """
    for active or deactivate category for products
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get('pk')
        category = get_object_or_404(ProductCategory, pk=pk)
        if category.is_active:
            category.is_active = False
            category.save()
            messages.success(
                self.request,
                'دسته مورد نظر غیر فعال شد'
            )
        else:
            category.is_active = True
            category.save()
            messages.success(
                self.request,
                'دسته مورد نظر فعال شد'
            )

        return reverse_lazy('admin_panel:product-category-list')

class ProductCategoryDeleteView(AdminUserMixin, View):
    """
    for delete slider
    """
    pass

# brand

class ProductBrandListView(AdminUserMixin, ListView):
    """for listing product brands"""
    model = ProductBrand
    context_object_name = 'items'
    paginate_by = 25
    template_name = 'admin_panel/product/brand/list.html'

class ProductBrandCreateView(AdminUserMixin, CreateView):
    """
    for creating a brands for products
    """
    model = ProductBrand
    form_class = AddBrandForm
    template_name = 'admin_panel/product/brand/create.html'
    success_url = reverse_lazy('admin_panel:product-brand-list')

    def form_valid(self, form):
        messages.success(self.request, 'برند مورد نظر با موفقت ساخته شد')
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
    template_name = 'admin_panel/product/brand/create.html'
    success_url = reverse_lazy('admin_panel:product-brand-list')
    context_object_name = 'item'

    def form_valid(self, form):
        messages.success(self.request, 'برند با موفقت ساخته شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

class ProductBrandActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """
    for active or deactivate slider
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get('pk')
        brand = get_object_or_404(ProductBrand, pk=pk)
        if brand.is_active:
            brand.is_active = False
            brand.save()
            messages.success(
                self.request,
                'برند مورد نظر غیر فعال شد'
            )
        else:
            brand.is_active = True
            brand.save()
            messages.success(
                self.request,
                'برند مورد نظر فعال شد'
            )

        return reverse_lazy('admin_panel:product-brand-list')

class ProductBrandDeleteView(AdminUserMixin, View):
    """
    for delete slider
    """

    pass

