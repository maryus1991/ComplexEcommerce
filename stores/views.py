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
from django.shortcuts import (get_object_or_404
, reverse
, render
, redirect
, get_list_or_404
                              )
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.timezone import now
from phonenumbers.phonenumber import PhoneNumber

from orders.models import Order
from .models import Store, StoreComment, StoreTag, StoreCategory, StoreApps
from dashboard.models import Ticket, TicketConversation

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
)
from product.models import (
    Product,
    ProductTag,
    ProductFeature,
    ProductGallery,
    ProductBrand,
    ProductCategory,

)

from blog.models import (
    Blog, BlogCategory
)

from user.mixins.logins import UserStoreStaffMixin, AdminUserMixin, StoreAdminUserStaff
from dashboard.forms import TicketConversationForm

from .validators import is_valid_message

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

    template_name = 'store/product_list.html'
    ordering = '-id'
    paginate_by = 50
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(store=self.request.user.store).prefetch_related('comments')


class StoreAddProduct(UserStoreStaffMixin, FormView):
    """
    for add product
    """
    template_name = 'store/add_product.html'
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


class StoreEditProductView(UserStoreStaffMixin, UpdateView):
    """
    for edit product
    """
    form_class = AddProductForm
    model = Product
    template_name = 'store/add_product.html'
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
    template_name = 'store/list_brand.html'
    paginate_by = 50
    context_object_name = 'brands'

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).order_by('name').prefetch_related('products')


class StoreAddBrandView(UserStoreStaffMixin, CreateView):
    """
    for add brand
    """
    form_class = AddBrandForm
    model = ProductBrand
    template_name = 'store/add_brand.html'
    success_url = reverse_lazy('store:list-brands')

    def form_valid(self, form):
        messages.success(self.request,
                         'برند شما ساخته شد')
        return super().form_valid(form)


class StoreListCategoryView(UserStoreStaffMixin, ListView):
    """
    for list the categories
    """
    model = ProductCategory
    template_name = 'store/list_category.html'
    paginate_by = 25
    context_object_name = 'categories'

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).order_by('name').prefetch_related('products')


class StoreAddCategoryView(UserStoreStaffMixin, CreateView):
    """
    for add category for store
    """
    form_class = AddCategoryForm
    model = ProductCategory
    template_name = 'store/add_category.html'
    success_url = reverse_lazy('store:list-category')

    def form_valid(self, form):
        messages.success(self.request,
                         'دسته شما ساخته شد')
        return super().form_valid(form)


### admin staff
# brands
class StoreUpdateBrandView(AdminUserMixin, UpdateView): pass


class StoreActiveDeActivateBrandView(AdminUserMixin, RedirectView): pass


class StoreRemoveBrandView(AdminUserMixin, View): pass


# categories
class StoreUpdateCategoryView(AdminUserMixin, UpdateView): pass


class StoreActiveDeActivateCategoryView(AdminUserMixin, RedirectView): pass


class StoreRemoveCategoryView(AdminUserMixin, View): pass


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
        messages.success(self.request, 'اطلاعات شما با موقیت ثبت شد')
        return super().form_valid(form)


# tickets

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
        return super().get_queryset().filter(
            user=self.request.user
        ).order_by('-closed_at').all()


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
        return super().get_queryset().filter(
            store=self.request.user.store,
        ).order_by('-closed_at').all()


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
        # todo edit the section for filtering
        query = super().get_queryset().filter(store=self.request.user.store, )

        status = self.request.GET.get('s') or None  # status filtering
        price_ordered = self.request.GET.get('po') or None  # price ordering
        price_range_start, price_range_end = self.request.GET.get('prs') or None, self.request.GET.get(
            'prd') or None  # for price range filtering
        date_order = self.request.GET.get('do') or None  # for date ordering +1 and -1
        date_range_start, date_range_end = self.request.GET.get('drs') or None, self.request.GET.get(
            'dre') or None  # for date range filtering
        sending_method = self.request.GET.get('sm') or None  # for sending method filtering
        user_phone_number_search = self.request.GET.get('upn') or None  # for search with user phone nomber
        order_id_search = self.request.GET.get('oid') or None  # for search with order id
        city_search = self.request.GET.get('cs') or None  # for search with distinction city
        post_id_search = self.request.GET.get('pis') or None  # for search with post id
        cart_number_search = self.request.GET.get('cns') or None  # for search with cart number
        payment_id_search = self.request.GET.get('pis') or None  # for search with payment id
        product_name_search = self.request.GET.get('pns') or None  # for search with existing products iin orders
        search_in_text = self.request.GET.get('sit') or None  # for search in text of products and other places

        if status:
            if status.isdigit() and len(status) == 1:
                status = int(status)
                if status == 1:
                    query = query.filter(is_paid=True, sending=False, delivered_to_user=False)
                elif status == 2:
                    query = query.filter(is_paid=True, sending=True)
                elif status == 3:
                    query = query.filter(canceled=True)
                else:
                    query = query.filter(is_paid=False, sending=False, delivered_to_user=False, canceled=False, )

        if price_ordered:
            if price_ordered.isdigit() and len(price_ordered) == 2:
                if price_ordered == '+1':
                    query = query.order_by('price')
                elif price_ordered == '-1':
                    query = query.order_by('-price')

        return query.all()


class StoreOrderDetailView(UserStoreStaffMixin, DetailView):
    """
    for watch the detials of orders
    """
    model = Order
    template_name = 'store/orders/order-detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get('pk'), store=self.request.user.store)


# store users list
class StoreUserListView(StoreAdminUserStaff, ListView):
    """
    for listing the users of store
    """
    template_name = 'store/users/list-users.html'
    context_object_name = 'users'

    def get_queryset(self):
        return get_object_or_404(Store, pk=self.request.user.store.id,
                                 ).users.all()


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


# store apps

class StoreAppsView(UserStoreStaffMixin, View):
    """
    for store apps add and remove
    """

    def get(self, request, *args, **kwargs):
        store = request.user.store
        obj = StoreApps.objects.filter(store=store).all()
        return render(request, 'store/apps/store-apps.html', {'items': obj,
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


class StoreBlogListView(UserStoreStaffMixin, ListView):
    """
    for list all store
    """
    model = Blog
    template_name = 'store/blog/list.html'
    context_object_name = 'blogs'
    paginate_by = 25

    def get_queryset(self):
        return super().get_queryset().filter(store=self.request.user.store).all()


class StoreBlogUpdateView(UserStoreStaffMixin, UpdateView):
    """
    for update blog posts
    """
    template_name = 'store/blog/add.html'
    form_class = AddStoreBlogForm
    success_url = reverse_lazy('store:blog-list')
    model = Blog


class StoreBlogDeleteView(UserStoreStaffMixin, View):
    """
    for delete blog posts
    """
    pass


class StoreActiveOrDeactivate(UserStoreStaffMixin, RedirectView):
    """
    for active or deactivate posts
    """
    pass


class StoreBlogAddCategories(UserStoreStaffMixin, FormView):
    """
    for add blog categories
    """
    template_name = 'store/blog/category/add.html'
    form_class = AddStoreBlogCategoryForm
    success_url = reverse_lazy('store:blog-list-category')


class StoreBlogListCategories(UserStoreStaffMixin, ListView):
    """
    for list all blog categories
    """
    model = Blog
    template_name = 'store/blog/category/list.html'
    context_object_name = 'categories'
    paginate_by = 25
