from django.utils.timezone import now, timedelta
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import (
    ListView,
    UpdateView,
    FormView,
    View,
)
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import get_user_model
from product.models import Product, UserFavorite
from orders.models import Order, OrderDetail, ReturnsOrders
from user.mixins.logins import CustomLoginRequiredMixin as LoginRequiredMixin
from user.forms import ActiveAccountForm as ChangeNumberForm
from user.forms import ChangePasswordForm, EditUserInformationForm
from .forms import CreateUserAddress as CreateUserAddressForm
from .forms import (
    UserTicketsClientForm,
    TicketConversationForm,
    UserTicketsClientFormMobile,
    TicketConversationMobileForm,
    CreateRequestReturnOrder,
    UserColleagueForm
)
from user.forms import LegalPersonForm
from .models import UserAddress, Ticket, TicketConversation
from sitesetting.models import SiteSetting
from utils.find_city import search_city
from django.utils.timezone import datetime
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from guarantee.models import ActiveProductGuarantee
from django.db.models import Q, Count, Sum, Prefetch
from django.db.models.functions import Coalesce

User = get_user_model()


@method_decorator(never_cache, name='dispatch')
class ActiveProductGuaranteeListView(LoginRequiredMixin, ListView):
    """for return order list"""

    model = ActiveProductGuarantee
    template_name = "dashboard/guarantee.html"
    context_object_name = "items"

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(user=self.request.user) |
            Q(phone_number=self.request.user.PhoneNumber)
        ).select_related(
            "guarantee",
            "guarantee__company",
            "guarantee__product",
            "guarantee__product__store",
        ).order_by("-id")


# Create your views here.

@method_decorator(never_cache, name='dispatch')
class UserColleague(LoginRequiredMixin, TemplateView):
    """for manage Colleague requests of users"""

    def get(self, request):
        return render(request, 'dashboard/colleague.html', {
            'form': UserColleagueForm(initial={
                'colleague_id': request.user.colleague_id or request.POST.get('colleague_id'),
                'store_address': request.user.store_address or request.POST.get('store_address'),
                'colleague_with_store': request.POST.get('colleague_with_store') or  request.user.colleague_with_store.all() ,
            })
        })
    
    
    def post(self, request):
        form = UserColleagueForm(request.POST, request.FILES)
        if form.is_valid():
            
            user = request.user
            user.colleague_id = form.cleaned_data.get('colleague_id')
            user.store_address = form.cleaned_data.get('store_address')
            user.store_image = form.cleaned_data.get('store_image')
            user.colleague_with_store.set(form.cleaned_data.get('colleague_with_store')) 
            user.colleague_request = True
            user.colleague_user = False
            
            user.save()

            for name in user.colleague_with_store.all():
                messages.success(
                    request,
                    f"درخواست شما جهت همکاری با {name} ارسال شد "
                )

        else:
            messages.error(
                request,
                form.errors.as_text
            )
        
        return render(request, 'dashboard/colleague.html', {
            'form': UserColleagueForm(initial={
                'colleague_id':  request.POST.get('colleague_id'),
                'store_address':   request.POST.get('store_address'),
                'colleague_with_store':   request.user.colleague_with_store.all() ,
            })
        })
    


@method_decorator(never_cache, name='dispatch')
class UserCancelColleague(LoginRequiredMixin, RedirectView):
    """for canceling the Colleague"""

    def get_redirect_url(self, *args, **kwargs):


        self.request.user.colleague_user = False
        self.request.user.colleague_request = False
        self.request.user.colleague_with_store = None
        self.request.user.save()
        
        messages.info(
            self.request,
            'حساب کاربری شما از همکار به کاربر عادی تغییر یافت'
        )
        messages.info(
            self.request,
            'درخواست همکاری شما کنسل شد'
        )

        return reverse_lazy('dashboard:user-colleague')



@method_decorator(never_cache, name='dispatch')
class UserSettingDashboard(LoginRequiredMixin, TemplateView):
    """
    for Show user settings
    """

    template_name = "dashboard/dashboard-account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_number_form"] = ChangeNumberForm(
            initial={"phone_number": str(self.request.user.PhoneNumber).replace(" ", '')}
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

@method_decorator(never_cache, name='dispatch')
class Dashboard(LoginRequiredMixin, TemplateView):
    """
    Create user dashboard
    """

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        details = OrderDetail.objects.filter(order__user=self.request.user)
        detail_stats = details.aggregate(
            all_order_price=Coalesce(Sum("price", filter=Q(order__canceled=False)), 0),
            all_order_count=Count("id"),
            canceled=Count("id", filter=Q(order__canceled=True)),
            paid=Count("id", filter=Q(order__is_paid=True)),
            continue_count=Count("id", filter=Q(order__is_paid=False, order__canceled=False)),
        )

        context["all_order_price"] = detail_stats["all_order_price"]
        context["all_order_count"] = detail_stats["all_order_count"]
        context["last_detail_product"] = details.select_related("product", "order").order_by("-id")[0:3]

        context["canceled"] = detail_stats["canceled"]
        context["paid"] = detail_stats["paid"]
        context["continue"] = detail_stats["continue_count"]

        ticket_stats = Ticket.objects.filter(user=self.request.user).aggregate(
            all_ticket=Count("id"),
            close_ticket=Count("id", filter=Q(close_ticket=True)),
        )

        context["all_ticket"] = ticket_stats["all_ticket"]
        context["close_ticket"] = ticket_stats["close_ticket"]

        return context


# return order
@method_decorator(never_cache, name='dispatch')
class ReturnOrderView(LoginRequiredMixin, View):
    """for send return order request"""

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order.objects.select_related("store"), user=self.request.user, pk=self.kwargs["pk"], is_paid=True)
        self.store = self.order.store

        store_date_for_accept_return_order = self.order.second_date + timedelta(
            days=self.store.time_for_return_order_days)

        if store_date_for_accept_return_order < now():
            messages.error(
                request, 'مهلت درخواست مرجوعی به پایان رسیده'
            )
            return redirect(request.META.get("HTTP_REFERER", '/'))

        if request.user.returns_orders.filter(order=self.order).exists():
            messages.error(
                request, 'درخواست مرجوعی برای این سفارش قبلا داده شده است'
            )
            return redirect(request.META.get("HTTP_REFERER", '/'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/orders/retuen-order-request.html'
        ,{'form': CreateRequestReturnOrder(initial={'cart_name':request.user.get_full_name()})})

    def post(self, request, *args, **kwargs):
        form = CreateRequestReturnOrder(request.POST)

        if form.is_valid():
            cart_name = form.cleaned_data["cart_name"]
            card_number = form.cleaned_data["card_number"]
            description = form.cleaned_data["description"]

            ReturnsOrders.objects.create(
                order=self.order,
                user=request.user,
                card_number=card_number,
                decryption=description,
                cart_name=cart_name
            )
            messages.success(
                request,'درخواست شما ارسال شد'
            )

        else:
            messages.error(
                request, form.errors.as_text()
            )
        return redirect('dashboard:orders-returns-list')

@method_decorator(never_cache, name='dispatch')
class ReturnsOrderListView(LoginRequiredMixin, ListView):
    """for return order list"""

    model = ReturnsOrders
    template_name = "dashboard/orders/returns-order-list.html"
    context_object_name = "items"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .select_related("order", "order__store", "order__discount")
            .prefetch_related(
                Prefetch(
                    "order__details",
                    queryset=OrderDetail.objects.select_related("product", "order"),
                )
            )
            .order_by("-id")
        )

@method_decorator(never_cache, name='dispatch')
class ReturnsOrderDelete(LoginRequiredMixin, RedirectView):
    """for return order detail"""

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        obj = self.request.user.returns_orders.filter(pk=pk).first()

        if obj is not None:
            if not obj.accept_by_store :
                if obj.date_close_request is None:
                    obj.delete()
                    messages.info(
                        self.request,
                        'حذف شد'
                    )
                else:
                    messages.error(
                        self.request,
                        'شما نمی توانید درخواست هایی که نهایی شده را حذف کنید'
                    )

            else:
                messages.error(
                    self.request,
                    'شما نمی توانید درخواست هایی که توسط فروشگاه تایید شده را حذف کنید را حذف کنید'
                )
        else:
            messages.error(
                self.request,
                'درخواست مورر نظر پیدا نشد'
            )

        return reverse("dashboard:orders-returns-list")


# order section in dashboard

@method_decorator(never_cache, name='dispatch')
class OrdersHistoryDashboard(LoginRequiredMixin, ListView):
    """
    for Show user orders history
    """

    context_object_name = "orders"
    model = Order
    template_name = "dashboard/orders/list.html"

    def get_queryset(self):
        return (
            Order.objects.filter(
                user=self.request.user,
            )
            .select_related("store", "address", "discount")
            .prefetch_related(
                Prefetch(
                    "details",
                    queryset=OrderDetail.objects.select_related("product", "order"),
                )
            )
            .order_by("-id")
        )

@method_decorator(never_cache, name='dispatch')
class OrdersDetailHistoryDashboard(LoginRequiredMixin, ListView):
    """
    for Show user orders history
    """

    context_object_name = "details"
    model = Order
    template_name = "dashboard/orders/details.html"

    def get_queryset(self):
        self._order_obj = get_object_or_404(
            self.model.objects.select_related("store", "address", "discount").prefetch_related(
                Prefetch(
                    "details",
                    queryset=OrderDetail.objects.select_related(
                        "product", "product__store", "order"
                    ),
                )
            ),
            user=self.request.user,
            id=self.kwargs.get("pk"),
        )
        details = list(self._order_obj.details.all())
        for detail in details:
            detail.order = self._order_obj
        return details

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context["order_obj"] = self._order_obj

        self.order = self._order_obj if self._order_obj.is_paid else None
        has_return = (
            self.request.user.returns_orders.filter(order=self.order).exists()
            if self.order
            else False
        )

        if self.order and not has_return:
            store_date_for_accept_return_order = self.order.second_date + timedelta(
                days=self.order.store.time_for_return_order_days)

            context['can_return'] = store_date_for_accept_return_order >= now()
        elif has_return:
            context['can_return'] = 2
        else:
            context['can_return'] = False

        return context

@method_decorator(never_cache, name='dispatch')
class GenerateOrderInvoice(LoginRequiredMixin, View):
    """
    for Show user order invoice
    """

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get("pk")
        obj = get_object_or_404(
            Order.objects.select_related("store", "user", "address", "discount").prefetch_related(
                Prefetch(
                    "details",
                    queryset=OrderDetail.objects.select_related("product", "order"),
                )
            ),
            is_paid=True,
            is_active=True,
            canceled=False,
            id=order_id,
        )

        if not request.user.is_superuser:
            if obj.store != request.user.store:
                if (obj.user != self.request.user) :
                    return HttpResponseForbidden()

        if obj.address is None:
            messages.warning(request, "برای دریافت فاکتور لطفا ادرس انتخاب کنید")
            return redirect(reverse("dashboard:order_detail", kwargs={"pk": order_id}))

        site = self.request.site

        # Handle official invoice case
        if obj.official_invoice and obj.official_invoice_conformed_given_to_user:

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

            # Safely open and return the file via Storage API
            try:
                if not obj.official_invoice_pdf:
                    raise FileNotFoundError
                file = obj.official_invoice_pdf.open("rb")
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

@method_decorator(never_cache, name='dispatch')
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
        return (
            UserFavorite.objects.filter(user=self.request.user)
            .select_related("product", "product__store", "product__category", "product__brand")
            .order_by("-id")
        )

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

@method_decorator(never_cache, name='dispatch')
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

@method_decorator(never_cache, name='dispatch')
class RemoveFavoriteProduct(LoginRequiredMixin, RedirectView):
    """
    for Remove Favorite Product to User
    """

    pattern_name = "product:detail"

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["pk"])
        if self.request.user.is_authenticated:
            # check the is user logged in and get obj
            objs = list(UserFavorite.objects.filter(user=self.request.user, product=product)[:2])

            # check the obj count and delete it
            if len(objs) == 1:
                objs[0].delete()
                messages.success(self.request, "ایتم مورد نظر حذف شد")
            else:
                return Http404()

        return self.request.META.get("HTTP_REFERER", "/")


# user address

@method_decorator(never_cache, name='dispatch')
class UserAddressDashboard(LoginRequiredMixin, ListView):
    """
    for Show user address
    """

    model = UserAddress
    template_name = "dashboard/address/dashboard-address.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user).order_by("-id").all()

@method_decorator(never_cache, name='dispatch')
class CreateUserAddress(LoginRequiredMixin, FormView):
    """
    for Create User Address
    """

    template_name = "dashboard/address/create-user-address.html"
    form_class = CreateUserAddressForm
    success_url = reverse_lazy("dashboard:address")

    def form_invalid(self, form):
        messages.error(
            self.request, form.errors.as_text(),
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user

            city = form.cleaned_data["city"]
            province = form.cleaned_data.get('province')
            validate_city_result = search_city(province,city)

            if validate_city_result[0] == 0 :
                messages.error(
                    self.request,
                    validate_city_result[1]
                    )
                return render(self.request, self.template_name, {"form": form})

            elif validate_city_result[0] == 1 :
                obj = validate_city_result[1]
                form.instance.city_code = obj['tipax_id']
                form.instance.city_code_post = obj['post_id']
                form.save()

                print(obj['tipax_id'],obj['post_id'])

                messages.success(
                    self.request,'ادرس شما اضافه شد'
                )

                if obj['tipax_id'] is None:
                    messages.warning(
                        self.request,
                        "این ادرس برای ارسال با تیپاکس مناسب نیست"
                    )

                if obj['post_id'] is None:
                    messages.warning(
                        self.request,
                        "این ادرس برای ارسال با پست مناسب نیست"
                    )

            return super().form_valid(form)
        except Exception as e:
            messages.error(
                self.request,
                'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
            )
            return redirect(reverse_lazy("dashboard:address"))

@method_decorator(never_cache, name='dispatch')
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
            form.instance.user = self.request.user

            city = form.cleaned_data["city"]
            province = form.cleaned_data.get('province')
            validate_city_result = search_city(province, city)

            if validate_city_result[0] == 0:
                messages.error(
                    self.request,
                    validate_city_result[1]
                )
                return render(self.request, self.template_name, {"form": form})

            elif validate_city_result[0] == 1:
                obj = validate_city_result[1]
                form.instance.city_code = obj['tipax_id']
                form.instance.city_code_post = obj['post_id']
                form.save()

                print(obj['tipax_id'],obj['post_id'])

                if obj['tipax_id'] is None:
                    messages.warning(
                        self.request,
                        "این ادرس برای ارسال با تیپاکس مناسب نیست"
                    )

                if obj['post_id'] is None:
                    messages.warning(
                        self.request,
                        "این ادرس برای ارسال با پست مناسب نیست"
                    )

            return super().form_valid(form)

        except Exception as e:
            messages.error(
                self.request,
                'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
            )
            return redirect(reverse_lazy("dashboard:address"))

@method_decorator(never_cache, name='dispatch')
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

@method_decorator(never_cache, name='dispatch')
class UserTicketDashboard(LoginRequiredMixin, ListView):
    """
    for Show user ticket
    """

    template_name = "dashboard/ticket/dashboard-tickets.html"
    model = Ticket
    context_object_name = "tickets"

    def get_queryset(self):
        return (
            Ticket.objects.filter(user=self.request.user)
            .select_related("store")
            .order_by("-id")
        )

@method_decorator(never_cache, name='dispatch')
class UserTicketConversation(LoginRequiredMixin, View):
    """
    for Show user ticket
    """

    template_name = "dashboard/ticket/dashboard-tickets-conversation.html"

    def get(self, request, *args, **kwargs):
        # get the ticket obj
        tickets = get_object_or_404(
            Ticket.objects.select_related("store", "user"),
            user=request.user,
            id=kwargs["pk"],
        )
        tickets_messages = tickets.message

        tickets_messages.filter(is_read_by_client=False).update(
            is_read_by_client=True,
            date_read_by_client=datetime.now(),
        )

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
            messages.error(self.request, form.errors.as_text())
        return redirect(
            reverse("dashboard:tickets-conversation", kwargs={"pk": ticket_id})
        )

@method_decorator(never_cache, name='dispatch')
class CloseTicket(LoginRequiredMixin, RedirectView):
    """
    for Close Ticket
    """

    pattern_name = "dashboard:tickets"

    def get_redirect_url(self, *args, **kwargs):
        ticket = get_object_or_404(Ticket, user=self.request.user, pk=kwargs["pk"])
        ticket_id = ticket.id
        ticket.close_ticket = True
        ticket.save(update_fields=["close_ticket"])
        messages.success(self.request, "تیکیت شما بسته شد")
        return reverse("dashboard:tickets-conversation", kwargs={"pk": ticket_id})

@method_decorator(never_cache, name='dispatch')
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
            "dashboard:tickets-conversation", kwargs={"pk": message.ticket_id}
        )
        if message.admin_message:
            messages.error(self.request, "توان حذف پیام ادمین را ندارید")
        else:
            message.delete()
            messages.success(self.request, "پیام با موفقیت حذف شد")
        return url

@method_decorator(never_cache, name='dispatch')
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
