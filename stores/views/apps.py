# store apps
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
from stores.models import Store, StoreComment, StoreTag, StoreCategory, StoreApps
from dashboard.models import Ticket, TicketConversation
from django.utils.dateparse import parse_date
from stores.forms import (
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

from stores.validators import is_valid_message
from utils.tipax_price_calc import validate_city

User = get_user_model()


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
                if search != '' and search is not None:
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

        if obj.admin_verified:
            if obj.is_active :
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
        else:
            messages.error(self.request,
                           'ادمین سایت این برنامه را غیر فعال کرده است برای فعال کردن ان و انتشار ان با ادمین سایت در ارتباط باشید'
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
