from datetime import datetime

from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import (
    ListView,
    UpdateView,
    FormView,
    DeleteView,
    DetailView,
    View,
)
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import get_user_model

from product.models import Product, UserFavorite
from orders.models import Order, OrderDetail
from user.mixins.logins import CustomLoginRequiredMixin as LoginRequiredMixin
from user.forms import ActiveAccountForm as ChangeNumberForm
from user.forms import ChangePasswordForm, EditUserInformationForm
from .forms import CreateUserAddress as CreateUserAddressForm
from .forms import (
    UserTicketsClientForm,
    TicketConversationForm,
    UserTicketsClientFormMobile,
    TicketConversationMobileForm,
)

from user.forms import LegalPersonForm

from .models import UserAddress, Ticket, TicketConversation
from sitesetting.models import SiteSetting

from utils.tipax_price_calc import validate_city

User = get_user_model()


# Create your views here.


class UserSettingDashboard(LoginRequiredMixin, TemplateView):
    """
    for Show user settings
    """

    template_name = "dashboard/dashboard-account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_number_form"] = ChangeNumberForm(
            initial={"phone_number": self.request.user.PhoneNumber}
        )
        context["change_password_form"] = ChangePasswordForm()
        context["edit_user_information_form"] = EditUserInformationForm(
            initial={
                "email": self.request.user.email,
                "first_name": self.request.user.first_name,
                "last_name": self.request.user.last_name,
            }
        )

        context["legal_person"] = LegalPersonForm(
            initial={
                "legal_person_economic_number": self.request.user.legal_person_economic_number,
                "legal_person_registration_number": self.request.user.legal_person_registration_number,
                "legal_person_phone": self.request.user.legal_person_phone,
            }
        )

        return context


class Dashboard(LoginRequiredMixin, TemplateView):
    """
    Create user dashboard
    """

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        details = OrderDetail.objects.filter(order__user=self.request.user)

        context["all_order_price"] = sum(
            details.filter(order__canceled=False).values_list("price", flat=True)
        )
        context["all_order_count"] = details.count()
        context["last_detail_product"] = details.order_by("-id")[0:3]

        context["canceled"] = details.filter(order__canceled=True).count()
        context["paid"] = details.filter(order__is_paid=True).count()
        context["continue"] = details.filter(
            order__is_paid=False, order__canceled=False
        ).count()

        tickets = Ticket.objects.filter(user=self.request.user)

        context["all_ticket"] = tickets.count()
        context["close_ticket"] = tickets.filter(close_ticket=True).count()

        return context


# order section in dashboard


class OrdersHistoryDashboard(LoginRequiredMixin, ListView):
    """
    for Show user orders history
    """

    context_object_name = "orders"
    model = Order
    template_name = "dashboard/orders/list.html"

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
        ).order_by("-id")


class OrdersDetailHistoryDashboard(LoginRequiredMixin, ListView):
    """
    for Show user orders history
    """

    context_object_name = "details"
    model = Order
    template_name = "dashboard/orders/details.html"

    def get_queryset(self):
        obj = get_object_or_404(
            self.model, user=self.request.user, id=self.kwargs.get("pk")
        )
        return obj.details.all()


class GenerateOrderInvoice(LoginRequiredMixin, View):
    """
    for Show user order invoice
    """

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get("pk")
        obj = get_object_or_404(
            Order, is_paid=True, is_active=True, canceled=False, id=order_id
        )

        if (obj.user != self.request.user):
            return HttpResponseForbidden()

        if obj.address is None:
            messages.warning(request, "برای دریافت فاکتور لطفا ادرس انتخاب کنید")
            return redirect(reverse("dashboard:order_detail", kwargs={"pk": order_id}))


        site = SiteSetting.objects.filter(is_active=True).first()


        # Handle official invoice case
        if obj.official_invoice :

            if not site.active_receive_official_invoice:
                messages.warning(request, 'صدور فاکتور رسمی تا اطلاع ثانویه از سمت ادمین سایت غیر فعال شده است')
                return redirect(reverse("dashboard:order_detail", kwargs={"pk": order_id}))
            
            if not obj.store.have_official_invoice:
                messages.warning(request, 'صدور فاکتور رسمی تا اطلاع ثانویه از سمت فروشگاه غیر فعال شده است')
                return redirect(reverse("dashboard:order_detail", kwargs={"pk": order_id}))

            # Check if user is a legal person
            if not request.user.legal_person:
                messages.warning(
                    request,
                    "برای دریافت فاکتور رسمی لطفا اطلاعات خواسته شده را وارد کنید",
                )
                return redirect("dashboard:account")

            # Check if invoice is ready
            if not obj.official_invoice_conformed_given_to_user:
                messages.warning(
                    request,
                    "پی دی اف  فاکتور رسمی شما هنوز آماده نشده است به محض آماده شدن از طریق پیامک به شما اعلام خواهد شد",
                )
                return redirect(
                    reverse("dashboard:order_detail", kwargs={"pk": order_id})
                )

            # Safely open and return the file
            try:
                file = open(
                    obj.official_invoice_pdf.path, "rb"
                )  # Using .path for FileField
                response = FileResponse(file)
                response["Content-Type"] = "application/pdf"
                response["Content-Disposition"] = (
                    f'attachment; filename="invoice_{order_id}.pdf"'
                )
                return response
            except FileNotFoundError:
                messages.error(request, "فایل فاکتور یافت نشد")
                return redirect(
                    reverse("dashboard:order_detail", kwargs={"pk": order_id})
                )
            except Exception as e:
                messages.error(request, f"خطا در دریافت فایل: {str(e)}")
                return redirect(
                    reverse("dashboard:order_detail", kwargs={"pk": order_id})
                )

        # Regular invoice case (render template)

        context = {"order": obj, "site": site}
        return render(request, "utils/invoice_pdf.html", context)


# user favorite product


class FavoriteProductsDashboard(LoginRequiredMixin, ListView):
    """
    for Show user favorite products
    """

    model = UserFavorite
    template_name = "dashboard/dashboard-favorite.html"
    context_object_name = "favorite_items"
    paginate_by = 10

    def get_queryset(self):
        # for return the specific user favorite products
        return UserFavorite.objects.filter(user=self.request.user).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_favorite"] = list(
            UserFavorite.objects.filter(user=self.request.user).values_list(
                "product_id", flat=True
            )
        )
        context["user_details_orders"] = list(
            OrderDetail.objects.filter(
                order__user=self.request.user,
                order__is_active=True,
                order__canceled=False,
                order__is_paid=False,
            ).values_list("product_id", flat=True)
        )
        return context


class AddFavoriteProduct(LoginRequiredMixin, RedirectView):
    """
    for Add Favorite Product to User
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["pk"])
        if self.request.user.is_authenticated:
            UserFavorite.objects.get_or_create(user=self.request.user, product=product)
            messages.success(
                self.request, "ایتم مورد نظر به لیست ایتم های مورد علاقه اضافه شد"
            )
        return self.request.META.get("HTTP_REFERER", "/")


class RemoveFavoriteProduct(LoginRequiredMixin, RedirectView):
    """
    for Remove Favorite Product to User
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["pk"])
        if self.request.user.is_authenticated:
            # check the is user logged in and get obj
            obj = UserFavorite.objects.filter(user=self.request.user, product=product)

            # check the obj count and delete it
            if obj.count() == 1:
                obj.delete()
                messages.success(self.request, "ایتم مورد نظر حذف شد")
            else:
                return Http404()

        return self.request.META.get("HTTP_REFERER", "/")


# user address


class UserAddressDashboard(LoginRequiredMixin, ListView):
    """
    for Show user address
    """

    model = UserAddress
    template_name = "dashboard/address/dashboard-address.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user).order_by("-id").all()


class CreateUserAddress(LoginRequiredMixin, FormView):
    """
    for Create User Address
    """

    template_name = "dashboard/address/create-user-address.html"
    form_class = CreateUserAddressForm
    success_url = reverse_lazy("dashboard:address")

    def dispatch(self, request, *args, **kwargs):
        print(1234)
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(
            request,form.errors,
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        print(1234)
        try:
            form.instance.user = self.request.user

            city = form.cleaned_data["city"]
            validate_city_result = validate_city(city)

            if validate_city_result is None:
                messages.error(self.request, "مشکلی پیش امد")
                return redirect(self.request.META.get("HTTP_REFERER", "/"))

            if len(validate_city_result) > 1:
                messages.warning(
                    self.request,
                    f"""
                    شهر شما یافت نشد لطفا در نوشتن ان دقت فرمایید
                    لیست شهر های پیدا شده با این اسم ارسالی شما 
                        {" , ".join([x['title'] for x in list(validate_city_result)])}""",
                )
                return redirect(self.request.META.get("HTTP_REFERER", "/"))

            if len(validate_city_result) == 1:
                form.instance.city_code = validate_city_result[0]["id"]
                form.save()

            messages.success(self.request, "ادرس شما با موفقیت اضافه شد")
            return super().form_valid(form)
        except Exception as e:
            messages.error(
                self.request,
                'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
            )
            return redirect(reverse_lazy("dashboard:address"))


class UpdateUserAddress(LoginRequiredMixin, UpdateView):
    """
    for Create User Address
    """

    template_name = "dashboard/address/create-user-address.html"
    form_class = CreateUserAddressForm
    model = UserAddress

    def get_success_url(self):
        messages.success(self.request, "ادرس مورد نظر با موفقیت بروزرسانی شد")
        return reverse("dashboard:address")

    def form_valid(self, form):
        form.instance.user = self.request.user

        try:
            city = form.cleaned_data["city"]
            validate_city_result = validate_city(city)

            if validate_city_result is None:
                messages.error(self.request, "مشکلی پیش امد")
                return redirect(self.request.META.get("HTTP_REFERER", "/"))

            if len(validate_city_result) > 1:
                messages.warning(
                    self.request,
                    f"""
                    شهر شما یافت نشد لطفا در نوشتن ان دقت فرمایید
                    لیست شهر های پیدا شده با این اسم ارسالی شما 
                        {" , ".join([x['title'] for x in list(validate_city_result)])}""",
                )
                return redirect(self.request.META.get("HTTP_REFERER", "/"))

            if len(validate_city_result) == 1:
                form.instance.city_code = validate_city_result[0]["id"]

            form.save()
            messages.success(self.request, "ادرس شما با موفقیت بروز رسانی شد")
            return super().form_valid(form)

        except Exception as e:
            messages.error(
                self.request,
                'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
            )
            return redirect(reverse_lazy("dashboard:address"))


class DeleteUserAddress(LoginRequiredMixin, RedirectView):
    """
    for Delete User Address
    """

    pattern_name = "dashboard:address"

    def get_redirect_url(self, *args, **kwargs):
        address = get_object_or_404(UserAddress, pk=self.kwargs["pk"])
        address.delete()
        messages.success(self.request, "ادرس مورد نظر با موفقیت حذف شد")
        return reverse("dashboard:address")


# user ticket


class UserTicketDashboard(LoginRequiredMixin, ListView):
    """
    for Show user ticket
    """

    template_name = "dashboard/ticket/dashboard-tickets.html"
    model = Ticket
    context_object_name = "tickets"

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by("-id").all()


class UserTicketConversation(LoginRequiredMixin, View):
    """
    for Show user ticket
    """

    template_name = "dashboard/ticket/dashboard-tickets-conversation.html"

    def get(self, request, *args, **kwargs):
        # get the ticket obj
        tickets = get_object_or_404(Ticket, user=request.user, id=kwargs["pk"])
        tickets_messages = tickets.message

        for ticket in tickets_messages.filter(is_read_by_client=False):
            ticket.is_read_by_client = True
            ticket.date_read_by_client = datetime.now()
            ticket.save()

        if self.request.user_agent.is_mobile:
            form = TicketConversationMobileForm()
        else:
            form = TicketConversationForm()

        context = {
            "ticket": tickets,
            "form": form,
            "messages_tickets": tickets_messages.all(),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if self.request.user_agent.is_mobile:
            form = TicketConversationMobileForm(request.POST or None)
        else:
            form = TicketConversationForm(request.POST or None)

        ticket_id = kwargs["pk"]
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        if form.is_valid():
            content = form.cleaned_data["content"]
            if content:
                TicketConversation.objects.create(
                    message=content,
                    ticket=ticket,
                    is_read_by_client=True,
                    date_read_by_client=datetime.now(),
                )
                messages.success(request, "پیام شما ارسال شد")
            else:
                messages.error(self.request, "مشکلی پیش امده لطفا دوباره امتحان کننید")
        else:
            messages.error(self.request, form.errors)
        return redirect(
            reverse("dashboard:tickets-conversation", kwargs={"pk": ticket_id})
        )


class CloseTicket(LoginRequiredMixin, RedirectView):
    """
    for Close Ticket
    """

    pattern_name = "dashboard:tickets"

    def get_redirect_url(self, *args, **kwargs):
        ticket = get_object_or_404(Ticket, user=self.request.user, pk=kwargs["pk"])
        ticket_id = ticket.id
        ticket.close_ticket = True
        ticket.save()
        messages.success(self.request, "تیکیت شما بسته شد")
        return reverse("dashboard:tickets-conversation", kwargs={"pk": ticket_id})


class DeleteMessageTicket(LoginRequiredMixin, RedirectView):
    """
    for delete message in conversation
    """

    pattern_name = "dashboard:ticket"

    def get_redirect_url(self, *args, **kwargs):
        message = get_object_or_404(
            TicketConversation, ticket__user=self.request.user, pk=kwargs["pk"]
        )
        url = reverse(
            "dashboard:tickets-conversation", kwargs={"pk": message.ticket.id}
        )
        if message.admin_message:
            messages.error(self.request, "توان حذف پیام ادمین را ندارید")
        else:
            message.delete()
            messages.success(self.request, "پیام با موفقیت حذف شد")
        return url


class CreateUserTicket(LoginRequiredMixin, FormView):
    """
    for Show user ticket
    """

    template_name = "dashboard/ticket/dashboard-tickets-create.html"
    form_class = UserTicketsClientForm
    success_url = reverse_lazy("dashboard:tickets")

    # todo fix the checkeditor config
    def get_form_class(self):
        if self.request.user_agent.is_mobile:
            return UserTicketsClientFormMobile
        return UserTicketsClientForm

    def form_valid(self, form):
        store = form.cleaned_data["store"]
        subject = form.cleaned_data["subject"]
        content = form.cleaned_data["content"]

        ticket = Ticket.objects.create(
            subject=subject,
            store=store,
            user=self.request.user,
        )

        TicketConversation.objects.create(
            ticket=ticket,
            message=content,
            is_read_by_client=True,
            date_read_by_client=datetime.now(),
        )

        messages.success(self.request, "پیام شما ارسال شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "مشکلی پیش امده است")
        return super().form_invalid(form)
