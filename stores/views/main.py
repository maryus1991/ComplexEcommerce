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
    context_object_name = 'store'

    def get_object(self):
        return self.request.user.store

    def get_queryset(self):
        return self.request.user.store
