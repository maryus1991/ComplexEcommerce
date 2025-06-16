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

