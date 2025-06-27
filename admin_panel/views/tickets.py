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


class SendTicketCreateView(AdminUserMixin, CreateView):
    """
    for listing sent ticket
    """
    form_class = StoreSendTicketForm
    template_name = 'admin_panel/tickets/create.html'
    success_url = reverse_lazy('admin_panel:ticket-send-list')

    def form_valid(self, form):
        subject = form.cleaned_data.get('subject')
        store = form.cleaned_data.get('store')
        message_message = form.cleaned_data.get('message_message')
        print(self.request.user)
        ticket = Ticket.objects.create(
            subject=subject,
            store=store,
            user=self.request.user
        )
        print(ticket)
        TicketConversation.objects.create(
            ticket=ticket,
            message=message_message,
            is_read_by_client=True,
            date_read_by_client=now(),
        )

        messages.success(self.request, 'تیکیت شما ارسال شد')

        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.warning(
            self.request,
            form.errors
        )
        return super().form_invalid(form)


class TicketConversationDetailView(AdminUserMixin, View):
    """
    for ticket conversation detail
    """

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        item = Ticket.objects.filter(pk=pk).prefetch_related('message').first()

        if item is None:
            raise Http404()

        if item.user == request.user:

            for message in item.message.filter(is_read_by_client=False).all():
                message.is_read_by_client = True
                message.date_read_by_client = now()
                message.save()

        else:

            if SiteSetting.objects.first().send_message_response_to_ticket:
                send_message(
                    str(item.user.PhoneNumber).replace(' ', ''),
                    "به تیکت شما پاسخ داده شد با مراجعه به قسمت تیکت ها در حساب کاربری خود ان را مشاهده کنید"
                )

            for message in item.message.filter(is_read_by_server=False).all():
                message.is_read_by_server = True
                message.date_read_by_admin = now()
                message.save()

        return render(request, 'admin_panel/tickets/conversations.html', {'obj': item})

    def post(self, request, *args, **kwargs):  #

        pk = self.kwargs.get('pk')
        item = Ticket.objects.filter(pk=pk).prefetch_related('message').first()

        if item is None:
            raise Http404()

        new_message = request.POST.get('message')

        if new_message and new_message != '' and new_message != ' ' and new_message is not None and not new_message.isspace():
            if item.user != request.user:
                TicketConversation.objects.create(
                    ticket=item,
                    admin_message=True,
                    message=new_message,
                    is_read_by_server=True,
                    date_read_by_admin=now()
                )
            else:
                TicketConversation.objects.create(
                    ticket=item,
                    message=new_message,
                    is_read_by_client=True,
                    date_read_by_client=now()
                )

            messages.success(
                self.request,'پیام شما ارسال شد'
            )
        else:
            messages.error(
                request,'پیام خالی ارسال نکنید'
            )

        return redirect(request.META.get('HTTP_REFERER'))


# send tickets list
class TicketSendListView(ListView):
    """
    for listing received ticket
    """
    model = Ticket
    paginate_by = 25
    context_object_name = 'tickets'
    template_name = 'admin_panel/tickets/send/list.html'

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).all().order_by('-id').order_by('close_ticket')


# received tickets list
class TicketReceivedListView(AdminUserMixin, ListView):
    """
    for listing received ticket
    """
    model = Ticket
    paginate_by = 25
    context_object_name = 'tickets'
    template_name = 'admin_panel/tickets/received/list.html'

    def get_queryset(self):
        return Ticket.objects.filter(store__isnull=True).all().order_by('-id').order_by('close_ticket')

class CloseTicketView(AdminUserMixin, RedirectView):
    """for closing ticket"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Ticket, pk=kwargs.get('pk'))

        if obj.close_ticket :
            messages.warning(
                self.request,
                f'تیکیت شما شده است '
            )

            return self.request.META.get('HTTP_REFERER')

        obj.close_ticket = True
        obj.closed_at = now()
        obj.save()
        messages.success(
            self.request,
            f' تیکت بسته شد '
        )

        return self.request.META.get('HTTP_REFERER')

class DeleteTicketView(AdminUserMixin, RedirectView):
    """for delete Ticket"""
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Ticket, pk=kwargs.get('pk'))
        if obj.close_ticket :
            obj.delete()
            messages.warning(
                self.request,
                'تیکت حذف شد'
            )
        else:
            messages.error(
                self.request,
                'برای حذف تیکت انرا بسته کنید'
            )
        return redirect('admin_panel:ticket-received-list')

class DeleteMessageView(AdminUserMixin, RedirectView):
    """for delete Message"""
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(TicketConversation, pk=kwargs.get('pk'))
        obj.delete()
        messages.success(
            self.request,
            'پیام حذف شد'
        )
        return self.request.META.get('HTTP_REFERER')
