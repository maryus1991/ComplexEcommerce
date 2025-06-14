from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    CreateView,
    FormView,
    UpdateView,
    RedirectView
, View
)
from django.db.models import Q
from django.db.models.aggregates import Count
from django.shortcuts import (get_object_or_404
, reverse
, render
, redirect
, get_list_or_404)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.timezone import now
from phonenumbers.phonenumber import PhoneNumber
from django.db import transaction
from django.core.exceptions import PermissionDenied, SuspiciousOperation, ValidationError
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import UploadedFile
from orders.models import Order
from .models import Store, StoreComment, StoreTag, StoreCategory, StoreApps
from dashboard.models import Ticket, TicketConversation
from django.utils.dateparse import parse_date
from .forms import (
    AddProductForm
, AddBrandForm
, AddCategoryForm
, AddStoreForm
, StoreSendTicketForm
, AddStoreUserStaffForm
, AddStoreAppForm
, AddStoreBlogForm
, AddStoreBlogCategoryForm
, ProductSearchForm
, BrandAndCategorySearchForm
, TicketFilterForm
, OrderFilteringForm
, StoreBlogFilteringForm
, StoreUsersStaffFilteringForm
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
from blog.models import (
    Blog, BlogCategory
)
from django.views.generic import ListView
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from user.mixins.logins import (UserStoreStaffMixin,
                                AdminUserMixin,
                                StoreAdminUserStaff)
from dashboard.forms import TicketConversationForm
import jdatetime

from .validators import is_valid_message
from utils.tipax_price_calc import validate_city

User = get_user_model()


class StoreDetailView(DetailView):
    """
    for store detail view
    """
    model = Store
    template_name = 'store_detail.html'


class StoreMainPage(UserStoreStaffMixin, DetailView):
    """
    for main page of store detail view
    """

    template_name = 'store/index2.html'
    pk_url_kwarg = None

    def get_object(self):
        return self.request.user.store

    def get_queryset(self):
        return self.request.user.store


class StoreProductListView(UserStoreStaffMixin, ListView):
    """
    for listing the products of store
    """

    template_name = 'store/product/product_list.html'
    ordering = '-id'
    paginate_by = 50
    context_object_name = 'products'

    def get_queryset(self):
        # Base queryset
        queryset = Product.objects.filter(store=self.request.user.store
                                          ).prefetch_related('comments', 'views')

        # Process search parameters if form is valid
        params = ProductSearchForm(self.request.GET or None)

        if not params.is_valid():
            return queryset

        cleaned_data = params.cleaned_data

        # Boolean filters
        if cleaned_data.get('is_active'):
            is_active = cleaned_data.get('is_active')

            if is_active == '0':
                queryset = queryset.filter(is_active=False)
            elif is_active == '1':
                queryset = queryset.filter(is_active=True)

        if cleaned_data.get('have_discount'):
            have_discount = cleaned_data.get('have_discount')

            if have_discount == '0':
                queryset = queryset.filter(have_discount=False)
            elif have_discount == '1':
                queryset = queryset.filter(have_discount=True)

        # Text search
        if name := cleaned_data.get('name'):
            queryset = queryset.filter(
                Q(name__icontains=name) |
                Q(description__icontains=name)
            )

        # Numeric range filters
        range_filters = {
            'discount': ('discount_min', 'discount_max'),
            'count': ('count_min', 'count_max'),
            'weight': ('weight_min', 'weight_max'),
            'price': ('price_min', 'price_max'),
            'height': ('height_min', 'height_max'),
            'length': ('length_min', 'length_max'),
            'width': ('width_min', 'width_max'),
        }

        for field, (min_key, max_key) in range_filters.items():
            if min_val := cleaned_data.get(min_key):
                queryset = queryset.filter(**{f'{field}__gte': min_val})
            if max_val := cleaned_data.get(max_key):
                queryset = queryset.filter(**{f'{field}__lte': max_val})

        # Foreign key filters
        if category := cleaned_data.get('category'):
            queryset = queryset.filter(category_id=category)

        if brand := cleaned_data.get('brand'):
            queryset = queryset.filter(brand_id=brand)

        # Many-to-many filters
        if features := cleaned_data.get('feature'):
            # Clean and split features while handling edge cases
            features = [feature.strip() for feature in features.split('-') if feature.strip()]

            # Create a single query with multiple conditions
            query = Q()
            for item in features:
                query |= Q(features__title__icontains=item)

            # Apply the combined filter once
            queryset = queryset.filter(query).distinct()

        if tags := cleaned_data.get('tag'):
            # Clean and split features while handling edge cases
            tags = [tags.strip() for tag in tags.split('-') if tag.strip()]

            # Create a single query with multiple conditions
            query = Q()
            for item in tags:
                query |= Q(tags__name__icontains=item)

            # Apply the combined filter once
            queryset = queryset.filter(query).distinct()

        if ordering := cleaned_data.get('ordering'):
            if ordering == '11':
                queryset = queryset.annotate(views_count=Count('views')).order_by('-views_count')  # بیشترین بازدید
            elif ordering == '12':
                queryset = queryset.annotate(views_count=Count('views')).order_by('views_count')  # کمترین بازدید
            elif ordering == '21':
                queryset = queryset.order_by('-price')  # بیشترین قیمت
            elif ordering == '22':
                queryset = queryset.order_by('price')  # کمترین قیمت
            elif ordering == '31':
                queryset = queryset.annotate(comments_count=Count('comments')).order_by(
                    '-comments_count')  # بیشترین تعداد کامنت
            elif ordering == '32':
                queryset = queryset.annotate(comments_count=Count('comments')).order_by(
                    'comments_count')  # کمترین  تعداد کامنت
            elif ordering == '41':
                queryset = queryset.order_by('-count')  # بیشترین موجودی کالا
            elif ordering == '42':
                queryset = queryset.order_by('count')  # کمترین موجودی کالا

        return queryset.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ProductSearchForm(
            self.request.GET
        )
        return context


class StoreAddProduct(UserStoreStaffMixin, FormView):
    """
    for add product
    """
    template_name = 'store/product/add_product.html'
    form_class = AddProductForm
    success_url = reverse_lazy('store:list-product')

    def form_valid(self, form):
        store = self.request.user.store
        tags = form.cleaned_data['tags'].split('**')
        features = form.cleaned_data['features'].split('**')
        gallery = form.cleaned_data['gallery']
        product = Product.objects.create(
            store=store,
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            price=form.cleaned_data['price'],
            have_discount=form.cleaned_data['have_discount'],
            discount=form.cleaned_data['discount'],
            picture=form.cleaned_data['picture'],
            count=form.cleaned_data['count'],
            weight=form.cleaned_data['weight'],
            brand=form.cleaned_data['brand'],
            category=form.cleaned_data['category'],

        )

        for img in gallery:
            ProductGallery.objects.create(product=product, image=img).save()

        for feature in features:
            if feature.isalnum and feature != ' ' and feature is not None:
                ProductFeature.objects.create(product=product, title=feature)
            else:
                messages.warning(self.request,
                                 f'{feature} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید'
                                 )
        for tags in tags:
            if tags.isalnum and tags != ' ' and tags is not None:
                ProductTag.objects.create(Product=product, name=tags)
            else:
                messages.warning(self.request,
                                 f'{tags} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید'
                                 )

        messages.success(self.request,
                         'محصول شما با موفقیت ذخیره شد')
        product.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category_form'] = AddCategoryForm()
        context['brand_form'] = AddBrandForm()

        return context


class StoreEditProductView(UserStoreStaffMixin, UpdateView):
    """
    for edit product
    """
    form_class = AddProductForm
    model = Product
    template_name = 'store/product/add_product.html'
    success_url = reverse_lazy('store:list-product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.get_object()
        return context

    def form_valid(self, form):
        store = self.request.user.store
        tags = form.cleaned_data['tags'].split('**')
        features = form.cleaned_data['features'].split('**')
        gallery = form.cleaned_data['gallery']
        product = Product.objects.filter(pk=self.kwargs.get('pk'), store=store).update(
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            price=form.cleaned_data['price'],
            have_discount=form.cleaned_data['have_discount'],
            discount=form.cleaned_data['discount'],
            picture=form.cleaned_data['picture'],
            count=form.cleaned_data['count'],
            weight=form.cleaned_data['weight'],
            brand=form.cleaned_data['brand'],
            category=form.cleaned_data['category'],

        )

        product = self.get_object()

        for img in gallery:
            ProductGallery.objects.create(product=product, image=img).save()

        ProductFeature.objects.filter(product=product).delete()
        for feature in features:
            if feature.isalnum and feature != ' ' and feature is not None:
                ProductFeature.objects.create(product=product, title=feature)
            else:
                messages.warning(self.request,
                                 f'{feature} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید'
                                 )

        ProductTag.objects.filter(Product=product).delete()
        for tags in tags:
            if tags.isalnum and tags != ' ' and tags is not None:
                ProductTag.objects.create(Product=product, name=tags)
            else:
                messages.warning(self.request,
                                 f'{tags} تایید نشد لطفا فقط از اعداد و حروف استفاده کنید'
                                 )

        messages.success(self.request,
                         'تغییرات شما با موفقیت ثبت شد')
        product.save()
        return super().form_valid(form)


class StoreEditProductRemoveImg(UserStoreStaffMixin, RedirectView):
    """
    for remove img in editing product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        img_id = self.kwargs.get('img_id')
        product = get_object_or_404(Product, id=product_id, store=self.request.user.store)
        img = get_object_or_404(ProductGallery, id=img_id, product=product)
        img.delete()
        messages.success(self.request,
                         'عکس مورد نظر حذف شد')
        return self.request.META.get('HTTP_REFERER', '/')


class StoreEditActiveOrDeactivateProduct(UserStoreStaffMixin, RedirectView):
    """
    for active or deactivate product in editing product
    """

    def get_redirect_url(self, *args, **kwargs):
        product_id = self.kwargs.get('pk')

        product = get_object_or_404(Product, id=product_id, store=self.request.user.store)
        if product.is_active is True:
            product.is_active = False
            messages.success(self.request
                             , 'محصول مورد نظر غیر فعال شد')
        elif product.is_active is False:
            product.is_active = True
            messages.success(self.request
                             , 'محصول مورد نظر فعال شد')
        product.save()
        return self.request.META.get('HTTP_REFERER', '/')


class StoreDeleteProductView(StoreAdminUserStaff, View):
    """
    for delete product
    """

    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, id=product_id, store=self.request.user.store)
        messages.warning(self.request,
                         'با حذف محصول تمام اطلاعات زیر مجموعه ان پاک خواهد شد بهتر است محصول را غیر فعال کنید تا از حذف شدن اطلاعات جلوگیری کنید')
        return render(request, 'store/delete_product_conform.html', {'product': product})

    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, id=product_id, store=self.request.user.store)
        product_name = request.POST.get('conform')
        if product_name is not None and product_name != ' ' and product_name.isalnum():
            if product_name == product.name:
                product.delete()
                messages.success(self.request, 'محصول شما حذف شد')
                return redirect(reverse('store:list-product'))
            else:
                messages.warning(self.request, 'نام محصول ارسالی با نام اصلی محصول یک سان نیست')
        else:
            messages.warning(self.request, 'لطفا در ارسال نام محصول دقت کنید')

        return redirect(request.META.get('HTTP_REFERER', '/'))


class ListBrandView(UserStoreStaffMixin, ListView):
    """
    for list the brands
    """
    model = ProductBrand
    template_name = 'store/product/brand/list_brand.html'
    paginate_by = 25
    context_object_name = 'brands'

    def get_queryset(self):
        query = super().get_queryset().order_by('name'
                                                ).prefetch_related('products'
                                                                   ).annotate(product_count=Count('products'))

        params = BrandAndCategorySearchForm(self.request.GET)
        if not params.is_valid():
            return query

        cleaned_params = params.cleaned_data

        if name := cleaned_params.get('name'):
            query = query.filter(name__icontains=name)

        if is_active := cleaned_params.get('is_active'):
            if is_active == '1':
                query = query.filter(is_active=True)
            elif is_active == '0':
                query = query.filter(is_active=False)

        if ordering := cleaned_params.get('ordering'):

            if ordering == '41':  # بیشترین تعداد کالا
                query = query.order_by('-product_count').distinct()
            elif ordering == '42':  # کمترین تعداد کالا
                query = query.order_by('product_count').distinct()
            elif ordering == '51':  # جدید ترین
                query = query.order_by('-id')
            elif ordering == '52':  # قدیمی ترین
                query = query.order_by('id')

        return query

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):
        context = super().get_context_data(**kwargs)

        context['form'] = BrandAndCategorySearchForm()

        return context


class StoreAddBrandView(UserStoreStaffMixin, CreateView):
    """
    for add brand
    """
    form_class = AddBrandForm
    model = ProductBrand
    template_name = 'store/product/brand/add_brand.html'
    success_url = reverse_lazy('store:list-brands')

    def form_valid(self, form):
        messages.success(self.request,
                         'برند شما ساخته شد')
        form.save()
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class StoreListCategoryView(UserStoreStaffMixin, ListView):
    """
    for list the categories
    """
    model = ProductCategory
    template_name = 'store/product/category/list_category.html'
    paginate_by = 25
    context_object_name = 'categories'

    def get_queryset(self):
        query = super().get_queryset().order_by('name'
                                                ).prefetch_related('products').prefetch_related('child').annotate(
            product_count=Count('products'))

        form = BrandAndCategorySearchForm(self.request.GET)

        if not form.is_valid():
            return query

        cleaned_params = form.cleaned_data

        if name := cleaned_params.get('name'):
            query = query.filter(name__icontains=name)

        if is_active := cleaned_params.get('is_active'):
            if is_active == '1':
                query = query.filter(is_active=True)
            elif is_active == '0':
                query = query.filter(is_active=False)

        if ordering := cleaned_params.get('ordering'):
            if ordering == '41':  # بیشترین تعداد کالا
                query = query.order_by('-product_count').distinct()
            elif ordering == '42':  # کمترین تعداد کالا
                query = query.order_by('product_count').distinct()
            elif ordering == '51':  # جدید ترین
                query = query.order_by('-id')
            elif ordering == '52':  # قدیمی ترین
                query = query.order_by('id')

        if parent := cleaned_params.get('category_parent'):
            query = query.filter(parent_id=parent)

        return query.all()

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):
        context = super().get_context_data(**kwargs)

        context['form'] = BrandAndCategorySearchForm()

        return context


class StoreAddCategoryView(UserStoreStaffMixin, CreateView):
    """
    for add category for store
    """
    form_class = AddCategoryForm
    model = ProductCategory
    template_name = 'store/product/category/add_category.html'
    success_url = reverse_lazy('store:list-category')

    def form_valid(self, form):
        messages.success(self.request,
                         'دسته شما ساخته شد')
        form.save()
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


####
# store settings

class StoreUpdateInformationView(StoreAdminUserStaff, UpdateView):
    """
    for update information
    """
    template_name = 'store/add_store.html'
    form_class = AddStoreForm
    model = Store
    success_url = reverse_lazy('store:update')

    def get_object(self, queryset=None):
        return get_object_or_404(Store, id=self.request.user.store.id, is_active=True, is_verified=True)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):

        data = form.cleaned_data

        if data.get('have_official_invoice'):
            if (data.get('have_official_invoice') is None or
                data.get('official_invoice_price') is None or
                data.get('economic_number') is None or
                data.get('registration_number') is None or
                data.get('official_invoice_phone_number') is None):

                    raise ValidationError('برای فعال شدن صدور فاکتور رسمی باید همه فیلد های مربوط به فاکتور رسمی پر شود')

        if self.request.user.store.orgin_city != data.get('orgin_city'):
            validate_city_result = validate_city(data.get('orgin_city'))

            if validate_city_result is None:
                messages.error(
                    self.request,
                    'مشکلی پیش امد'
                )
                return redirect(self.request.META.get('HTTP_REFERER', '/'))

            if len(validate_city_result) > 1:
                messages.warning(
                    self.request,
                    f'''
                    شهر شما یافت نشد لطفا در نشونتن ان دقت فرمایید
                    لیست شهر های پیدا شده با این اسم ارسالی شما 
                        {" , ".join([x['title'] for x in list(validate_city_result)])}''')
                return redirect(self.request.META.get('HTTP_REFERER', '/'))

            if len(validate_city_result) == 1:
                form.instance.orgin_city_id  = validate_city_result[0]['id']

        messages.success(self.request, 'اطلاعات شما با موقیت ثبت شد')

        return super().form_valid(form)


# close tickets

class StoreCloseTicketViewSenderSide(UserStoreStaffMixin, RedirectView):
    """
    for close ticket
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(Ticket, pk=pk, user=self.request.user)
        if obj.user == self.request.user:
            obj.close_ticket = True
            obj.close_at = now()
            obj.save()
        messages.info(self.request,
                      'تیکت شما بسته شد')
        return self.request.META.get('HTTP_REFERER', '/')


class StoreCloseTicketViewReceiverSide(UserStoreStaffMixin, RedirectView):
    """
    for close ticket
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(Ticket, pk=pk)
        if obj.store is None and self.request.user.is_superuser:
            obj.close_ticket = True
            obj.close_at = now()
            obj.save()

        if obj.store == self.request.user.store:
            obj.close_ticket = True
            obj.close_at = now()
            obj.save()

        messages.info(self.request,
                      'تیکت شما بسته شد')

        return self.request.META.get('HTTP_REFERER', '/')


# send tickets

class StoreSendTicketView(UserStoreStaffMixin, CreateView):
    """
    for send ticket as store for other stores or admin
    """
    template_name = 'store/tickets/send_ticket.html'
    form_class = StoreSendTicketForm
    model = Ticket
    success_url = reverse_lazy('store:send-ticket')

    def form_valid(self, form):
        store = form.cleaned_data['store']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message_message']

        ticket = Ticket.objects.create(store=store, subject=subject, user=self.request.user)
        TicketConversation.objects.create(
            ticket=ticket,
            message=message,
            is_read_by_client=True,
            date_read_by_client=now()
        )

        messages.success(self.request,
                         'تیکت شما با موفقیت ارسال شد')

        return redirect('store:list-sended-ticket')


class StoreSendTicketsListView(UserStoreStaffMixin, ListView):
    """
    for list the sended tickets
    """
    model = Ticket
    template_name = 'store/tickets/sended_tickets_list.html'
    context_object_name = 'tickets'
    paginate_by = 25

    def get_queryset(self):
        query = super().get_queryset().filter(
            user=self.request.user
        ).order_by('-closed_at')

        form = TicketFilterForm(self.request.GET)

        if not form.is_valid():
            return query.all()

        cleaned_data = form.cleaned_data

        if subject := cleaned_data.get('subject'):
            query = query.filter(
                Q(subject=subject) |
                Q(message__message=subject)
            )

        if store_name := cleaned_data.get('store_name'):
            query = query.filter(
                Q(store__name=store_name) |
                Q(user__store__name=store_name,
                  user__store__isnull=False)
            )

        if user_name := cleaned_data.get('user_name'):
            query = query.filter(
                Q(store__name=user_name) |
                Q(user__store__name=user_name,
                  user__store__isnull=False)
            )

        if user_number := cleaned_data.get('user_number'):
            query = query.filter(
                Q(store__phone=user_number) |
                Q(store__phone2=user_number) |
                Q(user__PhoneNumber=user_number) |
                Q(user__store__isnull=False,
                  store__phone2=user_number) |
                Q(user__store__isnull=False,
                  store__phone=user_number)
            )

        if start_date := cleaned_data.get('start_date'):
            parts = str(start_date).split('-')

            if len(parts) != 3:
                messages.error(
                    self.request,
                    f'لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)'
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(
                    year, month, day
                ).strftime('%Y-%m-%d'))

            query = query.filter(
                date__gte=jalali_date,
            )

        if end_date := cleaned_data.get('end_date'):
            parts = str(end_date).split('-')

            if len(parts) != 3:
                messages.error(
                    self.request,
                    f'لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)'
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(
                    year, month, day
                ).strftime('%Y-%m-%d'))

            query = query.filter(
                date__lte=jalali_date,
            )

        if ticket_status := cleaned_data.get('ticket_status'):
            if ticket_status == '11':  # 'بسته'
                query = query.filter(
                    close_ticket=True
                )
            elif ticket_status == '12':  # 'باز'
                query = query.filter(
                    close_ticket=False
                )
            elif ticket_status == '21':  # خوانده نشده
                query = query.filter(
                    message__is_read_by_client=False
                )
            elif ticket_status == '22':  # خوانده شده
                query = query.filter(
                    message__is_read_by_client=True
                )

        if tsrir := cleaned_data.get('ticket_status_read_in_responder'):
            if tsrir == '11':  # خوانده شده توسط دریافت کننده
                query = query.filter(
                    message__is_read_by_server=False
                )
            elif tsrir == '12':  # خوانده نشده توسط دریافت کننده
                query = query.filter(
                    message__is_read_by_server=True
                )

        if ordering := cleaned_data.get('ordering'):
            if ordering == '11':  # جدیدترین
                query = query.order_by('-id')
            elif ordering == '12':  # قدیمی ترین
                query = query.order_by('id')

        return query.distinct().all()

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context['form'] = TicketFilterForm()
        return context


class StoreConversationsView(UserStoreStaffMixin, View):
    """
    for ticket conversations for sender
    """
    template_name = 'store/tickets/conversations.html'

    def get(self, request, *args, **kwargs):
        form = TicketConversationForm()
        obj = get_object_or_404(Ticket, id=self.kwargs['pk'], user=self.request.user)

        for message in obj.message.filter(is_read_by_client=False).all():
            message.is_read_by_client = True
            message.save()

        return render(request, self.template_name, {'form': form, 'obj': obj})

    def post(self, request, *args, **kwargs):

        obj = get_object_or_404(Ticket, id=self.kwargs['pk'], user=self.request.user, close_ticket=False)

        if 'message' not in request.POST or not request.POST['message'].strip():
            messages.error(request, 'لطفا پیام معتبر وارد کنید')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        message = request.POST['message'].strip()

        if not is_valid_message(message):
            messages.error(request,
                           'پیام شما حاوی کاراکترهای غیرمجاز است. فقط از حروف، اعداد و علائم نگارشی متداول استفاده کنید.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        TicketConversation.objects.create(
            ticket=obj,
            is_read_by_client=True,
            date_read_by_client=now(),
            message=message
        )

        messages.success(request, 'پیام شما با موفقیت ارسال شد')
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


# receive tickets

class StoreReceiveTicketListView(UserStoreStaffMixin, ListView):
    """
    for listing the received ticket
    """
    model = Ticket
    template_name = 'store/tickets/received_tickets_list.html'
    context_object_name = 'tickets'
    paginate_by = 25

    def get_queryset(self):
        query = super().get_queryset().filter(
            store=self.request.user.store,
        ).order_by('-closed_at')

        form = TicketFilterForm(self.request.GET)

        if not form.is_valid():
            return query.all()

        cleaned_data = form.cleaned_data

        if subject := cleaned_data.get('subject'):
            query = query.filter(
                Q(subject=subject) |
                Q(message__message=subject)
            ).distinct()

        if store_name := cleaned_data.get('store_name'):
            query = query.filter(
                Q(store__name=store_name) |
                Q(user__store__name=store_name,
                  user__store__isnull=False)
            )

        if user_name := cleaned_data.get('user_name'):
            query = query.filter(
                Q(store__name=user_name) |
                Q(user__store__name=user_name,
                  user__store__isnull=False)
            )

        if user_number := cleaned_data.get('user_number'):
            query = query.filter(
                Q(store__phone=user_number) |
                Q(store__phone2=user_number) |
                Q(user__PhoneNumber=user_number) |
                Q(user__store__isnull=False,
                  store__phone2=user_number) |
                Q(user__store__isnull=False,
                  store__phone=user_number)
            )

        if start_date := cleaned_data.get('start_date'):
            parts = str(start_date).split('-')

            if len(parts) != 3:
                messages.error(
                    self.request,
                    f'لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)'
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(
                    year, month, day
                ).strftime('%Y-%m-%d'))

            query = query.filter(
                date__gte=jalali_date,
            )

        if end_date := cleaned_data.get('end_date'):
            parts = str(end_date).split('-')

            if len(parts) != 3:
                messages.error(
                    self.request,
                    f'لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)'
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(
                    year, month, day
                ).strftime('%Y-%m-%d'))

            query = query.filter(
                date__lte=jalali_date,
            )

        if ticket_status := cleaned_data.get('ticket_status'):
            if ticket_status == '11':  # 'بسته'
                query = query.filter(
                    close_ticket=True
                )
            elif ticket_status == '12':  # 'باز'
                query = query.filter(
                    close_ticket=False
                )
            elif ticket_status == '21':  # خوانده نشده
                query = query.filter(
                    message__is_read_by_client=False
                )
            elif ticket_status == '22':  # خوانده شده
                query = query.filter(
                    message__is_read_by_client=True
                )

        if tsrir := cleaned_data.get('ticket_status_read_in_responder'):
            if tsrir == '11':  # خوانده شده توسط دریافت کننده
                query = query.filter(
                    message__is_read_by_server=False
                )
            elif tsrir == '12':  # خوانده نشده توسط دریافت کننده
                query = query.filter(
                    message__is_read_by_server=True
                )

        if ordering := cleaned_data.get('ordering'):
            if ordering == '11':  # جدیدترین
                query = query.order_by('-id')
            elif ordering == '12':  # قدیمی ترین
                query = query.order_by('id')

        return query.distinct().all()

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context['form'] = TicketFilterForm()
        return context


class StoreResponseToUsersTicketView(UserStoreStaffMixin, View):
    """
    for listing the received ticket
    """

    template_name = 'store/tickets/conversations.html'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        obj = get_object_or_404(Ticket, pk=pk, store=self.request.user.store)

        for message in obj.message.filter(is_read_by_server=False, date_read_by_admin=None).all():
            message.is_read_by_server = True
            message.date_read_by_admin = now()
            message.save()

        return render(request, self.template_name, {'obj': obj})

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        obj = get_object_or_404(Ticket, pk=pk, store=self.request.user.store, close_ticket=False)

        if 'message' not in request.POST or not request.POST['message'].strip():
            messages.error(request, 'لطفا پیام معتبر وارد کنید')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        message = request.POST['message'].strip()

        if not is_valid_message(message):
            messages.error(request,
                           'پیام شما حاوی کاراکترهای غیرمجاز است. فقط از حروف، اعداد و علائم نگارشی متداول استفاده کنید.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        TicketConversation.objects.create(
            ticket=obj,
            is_read_by_server=True,
            date_read_by_admin=now(),
            message=message,
            admin_message=True
        )
        messages.success(request, 'پیام شما با موفقیت ارسال شد')

        return redirect(self.request.META.get('HTTP_REFERER', '/'))


# orders

class StoreOrdersView(UserStoreStaffMixin, ListView):
    """
    for listing the orders
    """

    model = Order
    template_name = 'store/orders/orders-list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # دریافت کوئری‌ست پایه
        query = super().get_queryset().filter(store=self.request.user.store)

        # ایجاد فرم فیلتر با داده‌های GET
        form = OrderFilteringForm(self.request.GET)

        if not form.is_valid():
            return query

        data = form.cleaned_data
        if data.get('brands'):
            query = query.filter(
                details__product__brand=data.get('brands')
            )
        if data.get('category'):
            query = query.filter(
                details__product__category=data.get('category')
            )

        if features := data.get('product_features_search'):
            features = [feature.strip() for feature in features.split('-') if feature.strip()]

            if features:
                q_obj = Q()
                for feature in features:
                    q_obj |= Q(details__product__features__title__icontains=feature)

                query = query.filter(q_obj).annotate(
                    features_info=Concat(
                        'details__product__features__title',
                        Value(' '),
                    )
                ).filter(
                    features_info__icontains=features[0]  # جستجوی ترکیبی
                )

        if tags := data.get('product_tags_search'):
            tags = [tag.strip() for tag in tags.split('-') if tag.strip()]

            if tags:
                q_obj = Q()
                for tag in tags:
                    q_obj |= Q(details__product__tags__name__icontains=tag)

                query = query.filter(q_obj).annotate(
                    product_info=Concat(
                        'details__product__tags__name',
                        Value(' '),
                    )
                ).filter(
                    product_info__icontains=tags[0]  # یا همینجا جستجو دقیق‌تر
                )

        if product_search := data.get('product_search'):
            names = [name.strip() for name in product_search.split('-') if name.strip()]

            if names:
                q_obj = Q()
                for name in names:
                    q_obj |= Q(details__product__name__icontains=name)

                query = query.filter(q_obj).annotate(
                    product_info=Concat(
                        'details__product__name',
                        Value(' '),
                    )
                ).filter(
                    product_info__icontains=names[0]  # یا همینجا جستجو دقیق‌تر
                )

        # فیلتر بر اساس شماره کاربر
        if data.get('user_phone_number'):
            query = query.filter(user__PhoneNumber=data['user_phone_number'])

        # فیلتر بر اساس آدرس
        if data.get('address_search'):
            query = query.filter(

                Q(address__province__icontains=data.get('address_search')) |
                Q(address__city__icontains=data.get('address_search')) |
                Q(address__address__icontains=data.get('address_search')) |
                Q(address__zipcode__icontains=data.get('address_search')) |
                Q(address__additional_decryption__icontains=data.get('address_search'))
            )

        # فیلتر بر اساس کد پیگیری ارسال
        if data.get('sending_id'):
            query = query.filter(sending_id__icontains=data['sending_id'])

        # فیلتر بر اساس شماره کارت
        if data.get('cart'):
            query = query.filter(cart__icontains=data['cart'])

        # فیلتر بر اساس کد پیگیری پرداخت
        if data.get('payment_id'):
            query = query.filter(payment_id__icontains=data['payment_id'])

        # فیلتر بر اساس کد تخفیف
        if data.get('discount'):
            query = query.filter(discount=data['discount'])

        # فیلتر بر اساس تاریخ باز شدن سفارش
        if data.get('start_date'):
            parts = str(data.get('start_date')).split('-')

            if len(parts) != 3:
                messages.error(
                    self.request,
                    f'لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)'
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(
                    year, month, day
                ).strftime('%Y-%m-%d'))

            query = query.filter(date__gte=jalali_date)
        if data.get('end_date'):
            parts = str(data.get('end_date')).split('-')

            if len(parts) != 3:
                messages.error(
                    self.request,
                    f'لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)'
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(
                    year, month, day
                ).strftime('%Y-%m-%d'))

            query = query.filter(date__lte=jalali_date)

        # فیلتر بر اساس تاریخ پرداخت/کنسل
        if data.get('start_second_date'):
            parts = str(data.get('start_second_date')).split('-')

            if len(parts) != 3:
                messages.error(
                    self.request,
                    f'لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)'
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(
                    year, month, day
                ).strftime('%Y-%m-%d'))
            query = query.filter(second_date__gte=jalali_date)
        if data.get('end_second_date'):
            parts = str(data.get('end_second_date')).split('-')

            if len(parts) != 3:
                messages.error(
                    self.request,
                    f'لطفاً تاریخ {field_name} را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)'
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(
                    year, month, day
                ).strftime('%Y-%m-%d'))
            query = query.filter(second_date__lte=jalali_date)

        # فیلتر بر اساس نحوه ارسال
        if data.get('deliver_status'):
            if data['deliver_status'] == '11':  # پست
                query = query.filter(vip_post=True)
            elif data['deliver_status'] == '12':  # تیپاکس
                query = query.filter(tipax_post_delivery=True)
            elif data['deliver_status'] == '21':  # درون شهری
                query = query.filter(in_city_delivery=True)
            elif data['deliver_status'] == '22':  # حضوری
                query = query.filter(physical_delivery=True)

        # فیلتر بر اساس وضعیت پرداخت
        if data.get('payment_status'):
            if data['payment_status'] == '11':  # پرداخت شده
                query = query.filter(is_paid=True)
            elif data['payment_status'] == '12':  # درحال ارسال
                query = query.filter(is_paid=True, sending=True, delivered_to_user=False)
            elif data['payment_status'] == '21':  # تحویل شده
                query = query.filter(is_paid=True, sending=True, delivered_to_user=False)

        # فیلتر بر اساس وضعیت کلی
        if data.get('official_status'):
            if data['official_status'] == '11':  # کنسل شده
                query = query.filter(canceled=True)
            elif data['official_status'] == '12':  # پرداخت شده
                query = query.filter(is_paid=True)
            elif data['official_status'] == '21':  # باز
                query = query.filter(is_paid=False, canceled=False, is_active=True)

        # فیلتر بر اساس وضعیت فاکتور
        if data.get('invoice_status'):
            if data['invoice_status'] == '11':  # رسمی
                query = query.filter(official_invoice=True)
            elif data['invoice_status'] == '12':  # غیر رسمی
                query = query.filter(official_invoice=False)

        # فیلتر بر اساس وضعیت فاکتور رسمی
        if data.get('invoice_status_ready_pdf'):
            if data['invoice_status_ready_pdf'] == '11':  # تحویل داده شده
                query = query.filter(official_invoice_conformed_given_to_user=True)
            elif data['invoice_status_ready_pdf'] == '12':  # تحویل داده نشده
                query = query.filter(official_invoice_conformed_given_to_user=False)

        # فیلتر بر اساس وضعیت تخفیف
        if data.get('use_discount_code'):
            if data['use_discount_code'] == '11':  # با تخفیف
                query = query.filter(discount__isnull=False)
            elif data['use_discount_code'] == '12':  # بدون تخفیف
                query = query.filter(discount__isnull=True)

        # فیلتر بر اساس محدوده قیمت کل
        if data.get('min_total_price'):
            query = query.filter(total_price__gte=data['min_total_price'])
        if data.get('max_total_price'):
            query = query.filter(total_price__lte=data['max_total_price'])

        # فیلتر بر اساس محدوده وزن
        if data.get('min_total_weight'):
            query = query.filter(total_weight__gte=data['min_total_weight'])
        if data.get('max_total_weight'):
            query = query.filter(total_weight__lte=data['max_total_weight'])

        # فیلتر بر اساس ابعاد
        if data.get('min_total_length'):
            query = query.filter(total_length__gte=data['min_total_length'])
        if data.get('max_total_length'):
            query = query.filter(total_length__lte=data['max_total_length'])

        if data.get('min_total_width'):
            query = query.filter(total_width__gte=data['min_total_width'])
        if data.get('max_total_width'):
            query = query.filter(total_width__lte=data['max_total_width'])

        if data.get('min_total_height'):
            query = query.filter(total_height__gte=data['min_total_height'])
        if data.get('max_total_height'):
            query = query.filter(total_height__lte=data['max_total_height'])

        # فیلتر بر اساس قیمت تخفیف
        if data.get('min_discount_code_price'):
            query = query.filter(discount_code_price__gte=data['min_discount_code_price'])
        if data.get('max_discount_code_price'):
            query = query.filter(discount_code_price__lte=data['max_discount_code_price'])

        # فیلتر بر اساس قیمت ارسال
        if data.get('min_delivery_price'):
            query = query.filter(delivery_price__gte=data['min_delivery_price'])
        if data.get('max_delivery_price'):
            query = query.filter(delivery_price__lte=data['max_delivery_price'])

        # فیلتر بر اساس تعداد کالا
        if data.get('min_count_of_product'):
            query = query.filter(details__count__gte=data['min_count_of_product'])
        if data.get('max_count_of_product'):
            query = query.filter(details__count__lte=data['max_count_of_product'])

        return query.distinct()

    def get_context_data(self, *, object_list=..., **kwargs):

        context = super().get_context_data(**kwargs)

        context['form'] = OrderFilteringForm()
        return context


class StoreOrderDetailView(UserStoreStaffMixin, DetailView):
    """
    for watch the detials of orders
    """
    model = Order
    template_name = 'store/orders/order-detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get('pk'), store=self.request.user.store)


class AddOfficialInvoiceView(UserStoreStaffMixin, View):
    """
    Handles secure upload of official invoice PDFs for orders
    with comprehensive validation and error handling.
    """

    # Security constants
    MAX_FILE_SIZE = 50 * 1024 * 1024
    ALLOWED_MIME_TYPES = ['application/pdf']
    ALLOWED_FILE_EXTENSIONS = ['.pdf']

    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            return self._process_invoice_upload(request, *args, **kwargs)
        except PermissionDenied as e:
            messages.error(request, 'مجوز صدور فاکتور رسمی را ندارید لطفا اطلاعات خود را ویرایش منید')
            return redirect('store:update')
        except SuspiciousOperation as e:
            print(e)

            messages.error(request, 'فایل آپلود شده معتبر نیست')
            return redirect(request.META.get('HTTP_REFERER', reverse('dashboard:orders')))
        except Exception as e:
            messages.error(request, 'خطایی در آپلود فاکتور رخ داد')
            return redirect(request.META.get('HTTP_REFERER', reverse('dashboard:orders')))

    def _validate_store_requirements(self, store):
        """Validate store meets all requirements for issuing official invoices"""
        requirements = {
            'have_official_invoice': False,
            'economic_number': None,
            'registration_number': None,
            'official_invoice_phone_number': None
        }

        for field, invalid_value in requirements.items():
            if getattr(store, field) == invalid_value:
                raise PermissionDenied(
                    f"Store missing requirement: {field}"
                )

    def _validate_uploaded_file(self, uploaded_file):
        """Perform comprehensive validation of the uploaded file"""
        if not isinstance(uploaded_file, UploadedFile):
            raise SuspiciousOperation("Invalid file type")

        if uploaded_file.size > self.MAX_FILE_SIZE:
            raise SuspiciousOperation(f"File size exceeds {self.MAX_FILE_SIZE / 1024 / 1024}MB limit")

        if uploaded_file.content_type not in self.ALLOWED_MIME_TYPES:
            raise SuspiciousOperation("Invalid file content type")

        if not any(uploaded_file.name.lower().endswith(ext) for ext in self.ALLOWED_FILE_EXTENSIONS):
            raise SuspiciousOperation("Invalid file extension")

    def _get_validated_order(self, store, order_id):
        """Retrieve and validate the target order"""
        order = get_object_or_404(
            Order,
            pk=order_id,
            store=store,
            is_paid=True,
            canceled=False,
            is_active=True,
            official_invoice=True
        )
        return order

    def _process_invoice_upload(self, request, *args, **kwargs):
        """Main processing logic with transaction safety"""
        order_id = kwargs.get('pk')
        store = request.user.store

        # Validate store requirements
        self._validate_store_requirements(store)

        # Validate order exists and meets criteria
        order = self._get_validated_order(store, order_id)

        # Validate file upload
        if 'invoice_pdf' not in request.FILES:
            raise SuspiciousOperation("No file uploaded")

        pdf_file = request.FILES['invoice_pdf']
        self._validate_uploaded_file(pdf_file)

        # Process in atomic transaction
        with transaction.atomic():
            order.official_invoice_conformed_given_to_user = True
            order.official_invoice_pdf = pdf_file
            order.save()

        messages.success(request, 'فاکتور رسمی با موفقیت برای کاربر ارسال شد')
        return redirect(request.META.get('HTTP_REFERER'))


# store users list
class StoreUserListView(StoreAdminUserStaff, ListView):
    """
    for listing the users of store
    """
    template_name = 'store/users/list-users.html'
    context_object_name = 'users'

    def get_queryset(self):
        query = get_object_or_404(Store,
          pk=self.request.user.store.id,
          ).users.all()


        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StoreUsersStaffFilteringForm()
        return context


class StoreAddUsersView(StoreAdminUserStaff, FormView):
    """
    for adding users to store staff
    """
    form_class = AddStoreUserStaffForm
    template_name = 'store/users/add-users.html'
    success_url = reverse_lazy('store:user-list')

    def form_valid(self, form):
        store = self.request.user.store

        # new user data
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        phone_number = form.cleaned_data['PhoneNumber']
        password = form.cleaned_data['password']
        is_store_admin = form.cleaned_data['is_store_admin']

        if not password:
            messages.error(
                self.request,
                'رمز الزامی می باشد'
            )
            return super().form_valid(form)

        user_exit_check = get_user_model().objects.filter(
            Q(PhoneNumber=phone_number) | Q(email=email),
        ).all()

        if not user_exit_check.exists() and user_exit_check.count() == 0:

            get_user_model().objects.create_staff_user(
                PhoneNumber=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                store=store,
                is_store_admin=is_store_admin
            )

            messages.success(self.request,
                             'کاربر شما ساخته شد و برای فعال شدن کابر لطفا با ان شماه و رمز وارد سایت شده و پیامک ارسالی را وارد کنید تا حساب تایید بشود')
        else:
            messages.error(self.request,
                           'این شماره یا ایمیل قبلا وارد شده است')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,
                       form.errors)
        return super().form_invalid(form)


class StoreUpdateUsersView(StoreAdminUserStaff, UpdateView):
    """
    for updating users
    """
    form_class = AddStoreUserStaffForm
    template_name = 'store/users/add-users.html'
    success_url = reverse_lazy('store:user-list')
    model = User
    context_object_name = 'item'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'], store=self.request.user.store)

    def form_valid(self, form):
        # get store obj
        store = self.request.user.store

        # get form instance
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        phone_number = form.cleaned_data['PhoneNumber']
        password = form.cleaned_data['password']
        is_store_admin = form.cleaned_data['is_store_admin']

        user = get_object_or_404(User, pk=self.kwargs['pk'], store=store)

        if user.PhoneNumber == phone_number and user.email == email:
            if user.first_name != first_name or user.last_name != last_name or user.is_store_admin != is_store_admin:
                user.first_name = first_name
                user.last_name = last_name
                user.is_store_admin = is_store_admin
                user.save()
                messages.success(self.request,
                                 'اطلاعات شما بروز رسانی شد'
                                 )

        elif user.PhoneNumber != phone_number:
            user_exit = get_user_model().objects.filter(
                PhoneNumber=phone_number,
            )
            if not user_exit.exists() and user_exit.count() == 0:
                user.PhoneNumber = phone_number
                user.is_verified = False
                user.save()
                messages.success(self.request,
                                 'شماره کاربر مورد نظر تغییر یافت لطفا برای ورود به سایت به قسمت تایید حساب کاربری وارد شوید و حساب خود را تایید کنید'
                                 )
            else:
                messages.error(self.request, 'شماره ارسالی در سایت موجود می باشد'
                               )

        elif user.email != email:
            user_exit = get_user_model().objects.filter(
                email=email,
            )
            if not user_exit.exists() and user_exit.count() == 0:
                user.email = email
                user.save()
                messages.success(self.request, 'ایمیل مورد کاربر مورد نظر تغییر یافت'
                                 )
            else:
                messages.error(self.request, 'ایمیل ارسال در سایت موجود می باشد'
                               )

        if not user.check_password(password) and password:
            user.set_password(password)
            user.save()
            messages.success(self.request, 'رمز عبور کابر مورد نظر تغییر یافت'
                             )

        return redirect('store:user-list')

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class StoreUserActiveOrDeativate(StoreAdminUserStaff, RedirectView):
    """
        for active or deativate users
    """

    def get_redirect_url(self, *args, **kwargs):
        item = get_object_or_404(User, pk=self.kwargs['pk'], store=self.request.user.store)
        if item.is_active and not item.is_store_admin:
            item.is_active = False
            messages.success(self.request,
                             'کاربر مورد نظر غیر فعال شد و دیگر توانای ورود به سایت را ندارد')

        elif not item.is_active and not item.is_store_admin:
            item.is_active = True
            messages.success(self.request,
                             'کاربر مورد نظر  فعال شد')

        if item.is_store_admin:
            item.is_active = True
            messages.error(self.request, 'شما نمی توانید ادمینای فروشگاه را غیر فعال کنید')

        item.save()
        return self.request.META.get('HTTP_REFERER', '/')


class StoreRemoveUser(StoreAdminUserStaff, View):
    """
    for remove users
    """

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['pk'], store=self.request.user.store)
        messages.warning(request,
                         'شما نمی توانید ادمین فروشگاه رو حذف کنید و توجه کنید با حذف کاربر تمام فعالیت ان حذف می شود و بهتر است انرا غیر فعال کنید')
        return render(request, 'store/users/delete-user.html', {'item': user})

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['pk'], store=self.request.user.store)

        phone_number = request.POST['conform']
        if phone_number.isdigit():
            phone_number = str(phone_number)
            obj = str(user.PhoneNumber).replace(' ', '')
            if obj == phone_number:
                if not user.is_store_admin:
                    user.delete()
                    messages.warning(self.request,
                                     'کابر شما حذف شد')
                else:
                    messages.warning(request,
                                     'شما نمی توانید ادمین فروشگاه رو حذف کنید')

            else:
                messages.warning(request,
                                 'در وارد کردن اطلاعات دقت فرمایید')
        else:
            messages.error(request, 'لطفا فقط شماره رو وارد کنید')

        return redirect('store:user-list')


class StoreUserShowActivities(StoreAdminUserStaff, ListView):
    """
    نمایش فعالیت‌های کاربر با استفاده از ListView
    """
    template_name = 'store/users/user_activities.html'
    context_object_name = 'activities'
    paginate_by = 25  # نمایش 25 فعالیت در هر صفحه

    def get_queryset(self):
        user = get_object_or_404(
            self.request.user.store.users,
            pk=self.kwargs['pk']
        )

        return LogEntry.objects.filter(
            actor=user  # در django-auditlog از فیلد actor استفاده می‌شود
        ).order_by('-timestamp')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن کاربر به context
        context['user'] = get_object_or_404(
            self.request.user.store.users,
            pk=self.kwargs['pk']
        )
        return context

# store apps

class StoreAppsView(UserStoreStaffMixin, View):
    """
    for store apps add and remove
    """

    def get(self, request, *args, **kwargs):
        store = request.user.store
        obj = StoreApps.objects.filter(store=store)

        if request.method == 'GET':
            data = dict(request.GET.copy())
            if 'is_active' in data:
                is_active = data['is_active']
                if 'on' in is_active:
                    obj = obj.filter(is_active=True)

            if 'not_active' in data:
                is_active = data['not_active']
                if 'on' in is_active:
                    obj = obj.filter(is_active=False)

            if 'search' in data:
                search = data['search'][0]
                if  search != '' and search is not None:
                    obj = obj.filter(name__icontains=search)

        return render(request, 'store/apps/store-apps.html', {'items': obj.all(),
                                                              'form': AddStoreAppForm()})

    def post(self, request, *args, **kwargs):
        store = request.user.store

        form = AddStoreAppForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.store = store
            form.save()
            messages.success(
                self.request,
                'فایل شما ذخیره شد'
            )
        else:
            messages.error(self.request,
                           form.errors)
        return redirect('store:app-list')


class RemoveAppsOrActiveOrDeactivateAppsView(UserStoreStaffMixin, View):
    """
    for remove apps in post method and active or deativate in get method
    """

    def get(self, request, *args, **kwargs):
        store = request.user.store
        pk = self.kwargs['pk']
        obj = get_object_or_404(StoreApps, pk=pk, store=store)

        if obj.is_active:
            obj.is_active = False
            obj.save()
            messages.success(
                self.request,
                'فایل شما غیر فعال شد و کابران نمی توانند ان را دانلود و مشاهده کنند'
            )
        else:
            obj.is_active = True
            obj.save()
            messages.success(
                self.request,
                'فایل شما فعال شد و  کاربران می توانند انرا مشاهده کنند و ان را دانلود کنند'
            )
        return redirect('store:app-list')

    def post(self, request, *args, **kwargs):
        store = request.user.store
        pk = self.kwargs['pk']
        obj = get_object_or_404(StoreApps, pk=pk, store=store, )

        obj.delete()
        messages.info(self.request,
                      'فایل شما حذف شد')

        return redirect('store:app-list')


# store blog

class StoreAddBlog(UserStoreStaffMixin, FormView):
    """
    for add blog as store
    """
    template_name = 'store/blog/add.html'
    form_class = AddStoreBlogForm
    success_url = reverse_lazy('store:blog-list')

    def form_valid(self, form):
        form.instance.store = self.request.user.store
        form.instance.user = self.request.user
        form.instance.is_active = False
        form.save()
        messages.success(self.request,
                         'پست شما با موفقیت ایجاد شد لطفا برای انتشار ان پست را فعال کنید')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_form'] = AddStoreBlogCategoryForm()
        return context


class StoreBlogListView(UserStoreStaffMixin, ListView):
    """
    for list all store
    """
    model = Blog
    template_name = 'store/blog/list.html'
    context_object_name = 'blogs'
    paginate_by = 25

    def get_queryset(self):
        query = super().get_queryset().filter(store=self.request.user.store).prefetch_related('views')

        form = StoreBlogFilteringForm(self.request.GET)

        if not form.is_valid():
            return query

        data = form.cleaned_data

        if user_number := data.get('user_number'):
            query = query.filter(user__PhoneNumber=user_number)
        if start_date := data.get('start_date'):
            query = query.filter(updated_at__gte=start_date, is_active=True)
        if end_date := data.get('end_date'):
            query = query.filter(updated_at__lte=end_date, is_active=True)
        if category := data.get('category'):
            query = query.filter(category=category)
        if is_active := data.get('is_active'):
            if is_active == '11':
                query = query.filter(is_active=True)
            elif is_active == '12':
                query = query.filter(is_active=False)

        if ordering := data.get('ordering'):
            if ordering == '11':  # جدید ترین
                query = query.order_by('-id')
            elif ordering == '12':  # قدیمی ترین
                query = query.order_by('id')
            elif ordering == '21':  # بیشترین بازدید
                query = query.annotate(view_count=Count('views')).order_by('-view_count')
            elif ordering == '22':  # کمترین بازید
                query = query.annotate(view_count=Count('views')).order_by('view_count')

        if title := data.get('title'):
            query = query.filter(
                Q(title__icontains=title) |
                Q(content__icontains=title)
            )

        return query

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data['form'] = StoreBlogFilteringForm()

        return data


class StoreBlogUpdateView(UserStoreStaffMixin, UpdateView):
    """
    for update blog posts
    """
    template_name = 'store/blog/add.html'
    form_class = AddStoreBlogForm
    success_url = reverse_lazy('store:blog-list')
    model = Blog

    def form_valid(self, form):
        form.instance.store = self.request.user.store
        form.instance.user = self.request.user
        form.instance.is_active = False
        form.save()
        messages.success(self.request,
                         'پست شما با موفقیت بروزرسانی شد لطفا برای انتشار ان پست را فعال کنید')
        return super().form_valid(form)


class StoreBlogDeleteView(StoreAdminUserStaff, View):
    """
    for delete blog posts
    """

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        post = get_object_or_404(Blog, pk=pk, store=self.request.user.store)
        messages.warning(request, 'با حذف این پست تمامی اطلاعات به صورت کامل حذف می شوند بهتر است انرا غیر فعال کنید')
        return render(request, 'store/blog/delete.html', {'post': post})

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        post = get_object_or_404(Blog, pk=pk, store=self.request.user.store)

        post_title: str = request.POST.get('conform')

        if not post_title.isspace():
            if post_title == post.title:
                post.delete()
                messages.info(request, 'پست شما با موفقیت حذف شد')

            else:
                messages.error(request, 'در وارد کردن اطلاعات خواسته شده دقت کنید')
        else:
            messages.error(request, 'در وارد کردن اطلاعات خواسته شده دقت کنید')

        return redirect('store:blog-list')


class StoreActiveOrDeactivate(UserStoreStaffMixin, RedirectView):
    """
    for active or deactivate posts
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs['pk']

        post = get_object_or_404(Blog, pk=pk, store=self.request.user.store)

        if post.is_active:
            post.is_active = False
            post.updated_at = now()
            post.save()

            messages.warning(self.request,
                             'پست شما غیر فعال شد  و برای کابران غیر قابل مشاهده میباشد')
        else:
            post.is_active = True
            post.updated_at = now()
            post.save()

            messages.success(self.request,
                             'پست شما فعال شد  و انتشار یافت و برای کابران قابل مشاهده میباشد')

        return reverse('store:blog-list')


class StoreBlogAddCategories(UserStoreStaffMixin, FormView):
    """
    for add blog categories
    """
    template_name = 'store/blog/category/add.html'
    form_class = AddStoreBlogCategoryForm
    success_url = reverse_lazy('store:blog-list-category')

    def form_valid(self, form):
        form.instance.is_active = True
        form.save()
        messages.success(self.request,
                         'دسته با موفقیت ساخته شد')
        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form):
        messages.error(self.request,
                       form.errors)
        return redirect(self.request.META.get('HTTP_REFERER'))


class StoreBlogListCategories(UserStoreStaffMixin, ListView):
    """
    for list all blog categories
    """
    model = BlogCategory
    template_name = 'store/blog/category/list.html'
    context_object_name = 'categories'
    paginate_by = 25

    from django.db.models import Count, Q

    def get_queryset(self):
        # دریافت کوئری‌ست پایه با prefetch_related برای بهینه‌سازی
        query = super().get_queryset().prefetch_related('blogs')

        # دریافت پارامترهای فیلتر از request
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        views = self.request.GET.get('views')
        posts = self.request.GET.get('posts')

        # فیلتر بر اساس جستجو (نام یا توضیحات)
        if search:
            query = query.filter(
                name__icontains=search
            )

        # فیلتر بر اساس وضعیت فعال/غیرفعال
        if status == 'active':
            query = query.filter(is_active=True)
        elif status == 'inactive':
            query = query.filter(is_active=False)

        # فیلتر بر اساس تعداد پست‌ها
        if posts:
            # ابتدا تعداد پست‌ها را annotate کنیم
            query = query.annotate(posts_count=Count('blogs'))

            if posts == 'most_posts':
                query = query.order_by('-posts_count')
            elif posts == 'least_posts':
                query = query.order_by('posts_count')
            elif posts.isdigit():
                # فیلتر بر اساس تعداد دقیق پست‌ها
                query = query.filter(posts_count=int(posts))

        return query.distinct()
