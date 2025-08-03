from django.urls import reverse_lazy
from django.views.generic import RedirectView, CreateView, ListView, View
from django.shortcuts import get_object_or_404, reverse, redirect, Http404, render
from django.contrib import messages
from django.utils.timezone import now
from dashboard.models import Ticket, TicketConversation
from user.mixins.logins import AdminUserMixin
from utils.send_otp import send_message
from sitesetting.models import SiteSetting
from stores.forms import StoreSendTicketForm
from stores.forms import TicketFilterForm
from django.utils.dateparse import parse_date
import jdatetime
from django.db.models import Q



class SendTicketCreateView(AdminUserMixin, CreateView):
    """
    for listing sent ticket
    """

    form_class = StoreSendTicketForm
    template_name = "admin_panel/tickets/create.html"
    success_url = reverse_lazy("admin_panel:ticket-send-list")

    def form_valid(self, form):
        subject = form.cleaned_data.get("subject")
        store = form.cleaned_data.get("store")
        message_message = form.cleaned_data.get("message_message")
        print(self.request.user)
        ticket = Ticket.objects.create(
            subject=subject, store=store, user=self.request.user
        )
        print(ticket)
        TicketConversation.objects.create(
            ticket=ticket,
            message=message_message,
            is_read_by_client=True,
            date_read_by_client=now(),
        )

        messages.success(self.request, "تیکیت شما ارسال شد")

        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.warning(self.request, form.errors.as_text())
        return super().form_invalid(form)


class TicketConversationDetailView(AdminUserMixin, View):
    """
    for ticket conversation detail
    """

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        item = Ticket.objects.filter(pk=pk).prefetch_related("message").first()

        if item is None:
            raise Http404()

        if item.user == request.user:

            for message in item.message.filter(is_read_by_client=False).all():
                message.is_read_by_client = True
                message.date_read_by_client = now()
                message.save()

        else:

            if SiteSetting.objects.first().send_message_response_to_ticket:
                send_message.delay(
                    str(item.user.PhoneNumber).replace(" ", ""),
                    'ticketNotify',
                    str(item.user.PhoneNumber).replace(" ", ""),

                )

            for message in item.message.filter(is_read_by_server=False).all():
                message.is_read_by_server = True
                message.date_read_by_admin = now()
                message.save()

        return render(request, "admin_panel/tickets/conversations.html", {"obj": item})

    def post(self, request, *args, **kwargs):  #

        pk = self.kwargs.get("pk")
        item = Ticket.objects.filter(pk=pk).prefetch_related("message").first()

        if item is None:
            raise Http404()

        new_message = request.POST.get("message")

        if (
            new_message and
                new_message != "" and
                new_message != " " and
                new_message is not None and
                not new_message.isspace()
        ):
            if item.user != request.user:
                TicketConversation.objects.create(
                    ticket=item,
                    admin_message=True,
                    message=new_message,
                    is_read_by_server=True,
                    date_read_by_admin=now(),
                )
            else:
                TicketConversation.objects.create(
                    ticket=item,
                    message=new_message,
                    is_read_by_client=True,
                    date_read_by_client=now(),
                )

            messages.success(self.request, "پیام شما ارسال شد")
        else:
            messages.error(request, "پیام خالی ارسال نکنید")

        return redirect(request.META.get("HTTP_REFERER"))


# send tickets list
class TicketSendListView(ListView):
    """
    for listing received ticket
    """

    model = Ticket
    paginate_by = 25
    context_object_name = "tickets"
    template_name = "admin_panel/tickets/send/list.html"

    def get_queryset(self):
        query = (
            super().get_queryset().filter(user=self.request.user).order_by("-id").order_by("close_ticket")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TicketFilterForm()
        return context


# received tickets list
class TicketReceivedListView(AdminUserMixin, ListView):
    """
    for listing received ticket
    """

    model = Ticket
    paginate_by = 25
    context_object_name = "tickets"
    template_name = "admin_panel/tickets/received/list.html"

    def get_queryset(self):
        query = (
            super()
            .get_queryset()
            .filter(
                store__isnull=True
            ).order_by("-id").order_by("close_ticket")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TicketFilterForm()
        return context


class CloseTicketView(AdminUserMixin, RedirectView):
    """for closing ticket"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Ticket, pk=kwargs.get("pk"))

        if obj.close_ticket:
            messages.warning(self.request, "تیکیت شما شده است ")

            return self.request.META.get("HTTP_REFERER")

        obj.close_ticket = True
        obj.closed_at = now()
        obj.save()
        messages.success(self.request, " تیکت بسته شد ")

        return self.request.META.get("HTTP_REFERER")


class DeleteTicketView(AdminUserMixin, RedirectView):
    """for delete Ticket"""

    def get_redirect_url(self, *args, **kwargs):
        print(1)
        obj = get_object_or_404(Ticket, pk=kwargs.get("pk"))
        print(2)
        if obj.close_ticket:
            obj.delete()
            messages.warning(self.request, "تیکت حذف شد")
            print(4)
        else:
            print(3)
            messages.error(self.request, "برای حذف تیکت انرا بسته کنید")

        print(5)
        return reverse("admin_panel:ticket-received-list")


class DeleteMessageView(AdminUserMixin, RedirectView):
    """for delete Message"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(TicketConversation, pk=kwargs.get("pk"))
        obj.delete()
        messages.success(self.request, "پیام حذف شد")
        return self.request.META.get("HTTP_REFERER")
