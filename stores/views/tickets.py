from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
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
    get_list_or_404,
)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.timezone import now
from phonenumbers.phonenumber import PhoneNumber
from django.db import transaction
from django.core.exceptions import (
    PermissionDenied,
    SuspiciousOperation,
    ValidationError,
)
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import UploadedFile
from orders.models import Order
from stores.models import Store, StoreApps
from dashboard.models import Ticket, TicketConversation
from django.utils.dateparse import parse_date
from stores.forms import (
    AddProductForm,
    AddBrandForm,
    AddCategoryForm,
    AddStoreForm,
    StoreSendTicketForm,
    AddStoreUserStaffForm,
    AddStoreAppForm,
    AddStoreBlogForm,
    AddStoreBlogCategoryForm,
    ProductSearchForm,
    BrandAndCategorySearchForm,
    TicketFilterForm,
    OrderFilteringForm,
    StoreBlogFilteringForm,
    StoreUsersStaffFilteringForm,
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
from blog.models import Blog, BlogCategory
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from user.mixins.logins import UserStoreStaffMixin, AdminUserMixin, StoreAdminUserStaff
from dashboard.forms import TicketConversationForm
import jdatetime

from stores.validators import is_valid_message
from utils.tipax_price_calc import validate_city
from utils.send_otp import send_message
from sitesetting.models import SiteSetting

User = get_user_model()


# close tickets


class StoreCloseTicketViewSenderSide(UserStoreStaffMixin, RedirectView):
    """
    for close ticket
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        obj = get_object_or_404(Ticket, pk=pk, user=self.request.user)
        if obj.user == self.request.user:
            obj.close_ticket = True
            obj.close_at = now()
            obj.save()
        messages.info(self.request, "تیکت شما بسته شد")
        return self.request.META.get("HTTP_REFERER", "/")


class StoreCloseTicketViewReceiverSide(UserStoreStaffMixin, RedirectView):
    """
    for close ticket
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        obj = get_object_or_404(Ticket, pk=pk)
        if obj.store is None and self.request.user.is_superuser:
            obj.close_ticket = True
            obj.close_at = now()
            obj.save()

        if obj.store == self.request.user.store:
            obj.close_ticket = True
            obj.close_at = now()
            obj.save()

        messages.info(self.request, "تیکت شما بسته شد")

        return self.request.META.get("HTTP_REFERER", "/")


# send tickets

class StoreDeleteMessage(UserStoreStaffMixin, RedirectView):
    """for delete message in ticket"""

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        print(pk)
        obj = get_object_or_404(TicketConversation, pk=pk)

        if not obj.ticket.close_ticket:
            if obj.ticket.user == self.request.user and not obj.admin_message:
                obj.delete()
                messages.info(
                    self.request,
                    'پیام حذف شد'
                )
            elif obj.ticket.store == self.request.user.store and obj.admin_message:
                obj.delete()
                messages.info(
                    self.request,
                    'پیام حذف شد'
                )
        else:
            messages.error(
                self.request,
                'این تیکت بسته شده است'
            )

        return self.request.META.get("HTTP_REFERER", "/")


class StoreSendTicketView(UserStoreStaffMixin, CreateView):
    """
    for send ticket as store for other stores or admin
    """

    template_name = "store/tickets/send_ticket.html"
    form_class = StoreSendTicketForm
    model = Ticket
    success_url = reverse_lazy("store:send-ticket")

    def form_valid(self, form):
        store = form.cleaned_data["store"]
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message_message"]

        ticket = Ticket.objects.create(
            store=store, subject=subject, user=self.request.user
        )
        TicketConversation.objects.create(
            ticket=ticket,
            message=message,
            is_read_by_client=True,
            date_read_by_client=now(),
        )

        messages.success(self.request, "تیکت شما با موفقیت ارسال شد")

        return redirect("store:list-sended-ticket")


class StoreSendTicketsListView(UserStoreStaffMixin, ListView):
    """
    for list the sended tickets
    """

    model = Ticket
    template_name = "store/tickets/sended_tickets_list.html"
    context_object_name = "tickets"
    paginate_by = 25

    def get_queryset(self):
        query = (
            super().get_queryset().filter(user=self.request.user).order_by("-closed_at")
        )

        form = TicketFilterForm(self.request.GET)

        if not form.is_valid():
            return query.all()

        cleaned_data = form.cleaned_data

        if subject := cleaned_data.get("subject"):
            query = query.filter(Q(subject=subject) | Q(message__message=subject))

        if store_name := cleaned_data.get("store_name"):
            query = query.filter(
                Q(store__name=store_name) |
                Q(user__store__name=store_name, user__store__isnull=False)
            )

        if user_name := cleaned_data.get("user_name"):
            query = query.filter(
                Q(store__name=user_name) |
                Q(user__store__name=user_name, user__store__isnull=False)
            )

        if user_number := cleaned_data.get("user_number"):
            query = query.filter(
                Q(store__phone=user_number) |
                Q(store__phone2=user_number) |
                Q(user__PhoneNumber=user_number) |
                Q(user__store__isnull=False, store__phone2=user_number) |
                Q(user__store__isnull=False, store__phone=user_number)
            )

        if start_date := cleaned_data.get("start_date"):
            parts = str(start_date).split("-")

            if len(parts) != 3:
                messages.error(
                    self.request,
                    "لطفاً تاریخ را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(year, month, day).strftime("%Y-%m-%d")
            )

            query = query.filter(
                date__gte=jalali_date,
            )

        if end_date := cleaned_data.get("end_date"):
            parts = str(end_date).split("-")

            if len(parts) != 3:
                messages.error(
                    self.request,
                    "لطفاً تاریخ را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(year, month, day).strftime("%Y-%m-%d")
            )

            query = query.filter(
                date__lte=jalali_date,
            )

        if ticket_status := cleaned_data.get("ticket_status"):
            if ticket_status == "11":  # 'بسته'
                query = query.filter(close_ticket=True)
            elif ticket_status == "12":  # 'باز'
                query = query.filter(close_ticket=False)
            elif ticket_status == "21":  # خوانده نشده
                query = query.filter(message__is_read_by_client=False)
            elif ticket_status == "22":  # خوانده شده
                query = query.filter(message__is_read_by_client=True)

        if tsrir := cleaned_data.get("ticket_status_read_in_responder"):
            if tsrir == "11":  # خوانده شده توسط دریافت کننده
                query = query.filter(message__is_read_by_server=False)
            elif tsrir == "12":  # خوانده نشده توسط دریافت کننده
                query = query.filter(message__is_read_by_server=True)

        if ordering := cleaned_data.get("ordering"):
            if ordering == "11":  # جدیدترین
                query = query.order_by("-id")
            elif ordering == "12":  # قدیمی ترین
                query = query.order_by("id")

        return query.distinct().all()

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = TicketFilterForm()
        return context


class StoreConversationsView(UserStoreStaffMixin, View):
    """
    for ticket conversations for sender
    """

    template_name = "store/tickets/conversations.html"

    def get(self, request, *args, **kwargs):
        form = TicketConversationForm()
        obj = get_object_or_404(Ticket, id=self.kwargs["pk"], user=self.request.user)

        for message in obj.message.filter(is_read_by_client=False).all():
            message.is_read_by_client = True
            message.save()

        return render(request, self.template_name, {"form": form, "obj": obj})

    def post(self, request, *args, **kwargs):

        obj = get_object_or_404(
            Ticket, id=self.kwargs["pk"], user=self.request.user, close_ticket=False
        )

        if "message" not in request.POST or not request.POST["message"].strip():
            messages.error(request, "لطفا پیام معتبر وارد کنید")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        message = request.POST["message"].strip()

        if not is_valid_message(message):
            messages.error(
                request,
                "پیام شما حاوی کاراکترهای غیرمجاز است. فقط از حروف، اعداد و علائم نگارشی متداول استفاده کنید.",
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))

        TicketConversation.objects.create(
            ticket=obj,
            is_read_by_client=True,
            date_read_by_client=now(),
            message=message,
        )

        messages.success(request, "پیام شما با موفقیت ارسال شد")
        return redirect(self.request.META.get("HTTP_REFERER", "/"))


# receive tickets


class StoreReceiveTicketListView(UserStoreStaffMixin, ListView):
    """
    for listing the received ticket
    """

    model = Ticket
    template_name = "store/tickets/received_tickets_list.html"
    context_object_name = "tickets"
    paginate_by = 25

    def get_queryset(self):
        query = (
            super()
            .get_queryset()
            .filter(
                store=self.request.user.store,
            )
            .order_by("-closed_at")
        )

        form = TicketFilterForm(self.request.GET)

        if not form.is_valid():
            return query.all()

        cleaned_data = form.cleaned_data

        if subject := cleaned_data.get("subject"):
            query = query.filter(
                Q(subject=subject) | Q(message__message=subject)
            ).distinct()

        if store_name := cleaned_data.get("store_name"):
            query = query.filter(
                Q(store__name=store_name) |
                Q(user__store__name=store_name, user__store__isnull=False)
            )

        if user_name := cleaned_data.get("user_name"):
            query = query.filter(
                Q(store__name=user_name) |
                Q(user__store__name=user_name, user__store__isnull=False)
            )

        if user_number := cleaned_data.get("user_number"):
            query = query.filter(
                Q(store__phone=user_number) |
                Q(store__phone2=user_number) |
                Q(user__PhoneNumber=user_number) |
                Q(user__store__isnull=False, store__phone2=user_number) |
                Q(user__store__isnull=False, store__phone=user_number)
            )

        if start_date := cleaned_data.get("start_date"):
            parts = str(start_date).split("-")

            if len(parts) != 3:
                messages.error(
                    self.request,
                    "لطفاً تاریخ  را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(year, month, day).strftime("%Y-%m-%d")
            )

            query = query.filter(
                date__gte=jalali_date,
            )

        if end_date := cleaned_data.get("end_date"):
            parts = str(end_date).split("-")

            if len(parts) != 3:
                messages.error(
                    self.request,
                    "لطفاً تاریخ  را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(year, month, day).strftime("%Y-%m-%d")
            )

            query = query.filter(
                date__lte=jalali_date,
            )

        if ticket_status := cleaned_data.get("ticket_status"):
            if ticket_status == "11":  # 'بسته'
                query = query.filter(close_ticket=True)
            elif ticket_status == "12":  # 'باز'
                query = query.filter(close_ticket=False)
            elif ticket_status == "21":  # خوانده نشده
                query = query.filter(message__is_read_by_client=False)
            elif ticket_status == "22":  # خوانده شده
                query = query.filter(message__is_read_by_client=True)

        if tsrir := cleaned_data.get("ticket_status_read_in_responder"):
            if tsrir == "11":  # خوانده شده توسط دریافت کننده
                query = query.filter(message__is_read_by_server=False)
            elif tsrir == "12":  # خوانده نشده توسط دریافت کننده
                query = query.filter(message__is_read_by_server=True)

        if ordering := cleaned_data.get("ordering"):
            if ordering == "11":  # جدیدترین
                query = query.order_by("-id")
            elif ordering == "12":  # قدیمی ترین
                query = query.order_by("id")

        return query.distinct().all()

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = TicketFilterForm()
        return context


class StoreResponseToUsersTicketView(UserStoreStaffMixin, View):
    """
    for listing the received ticket
    """

    template_name = "store/tickets/conversations.html"

    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        obj = get_object_or_404(Ticket, pk=pk, store=self.request.user.store)

        for message in obj.message.filter(
            is_read_by_server=False, date_read_by_admin=None
        ).all():
            message.is_read_by_server = True
            message.date_read_by_admin = now()
            message.save()

        return render(request, self.template_name, {"obj": obj})

    def post(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        obj = get_object_or_404(
            Ticket, pk=pk, store=self.request.user.store, close_ticket=False
        )

        if "message" not in request.POST or not request.POST["message"].strip():
            messages.error(request, "لطفا پیام معتبر وارد کنید")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        message = request.POST["message"].strip()

        if not is_valid_message(message):
            messages.error(
                request,
                "پیام شما حاوی کاراکترهای غیرمجاز است. فقط از حروف، اعداد و علائم نگارشی متداول استفاده کنید.",
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))

        TicketConversation.objects.create(
            ticket=obj,
            is_read_by_server=True,
            date_read_by_admin=now(),
            message=message,
            admin_message=True,
        )

        if SiteSetting.objects.first().send_message_response_to_ticket:

            send_message.delay(
                str(obj.user.PhoneNumber).replace(" ", ""),
                "به تیکیت شما پاسخ داده شد با مراجعه به قسمت کاربری ان را مشاهده کنید",
            )

        messages.success(request, "پیام شما با موفقیت ارسال شد")

        return redirect(self.request.META.get("HTTP_REFERER", "/"))
