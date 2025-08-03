from django.contrib import messages
from django.views.generic import ListView, DetailView, View, RedirectView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from orders.models import Order, StoreSoldOrders, Store, ReturnsOrders, SpecificsOrders
from user.mixins.logins import AdminUserMixin
from django.db.models.aggregates import Count
from django.utils.timezone import now
from admin_panel.forms import SpecificsOrdersModelForm
from sitesetting.models import SiteSetting
from utils.send_otp import send_message
from admin_panel.forms import AdminOrderFilteringForm
from django.db.models import Value, Q
from django.db.models.functions import Concat
from django.utils.dateparse import parse_date
import jdatetime


class ChangeStatusToDeliveredToUser(AdminUserMixin, RedirectView):
    """for set sending id and change status to DeliveredToUser"""

    def get_redirect_url(self, *args, **kwargs):
        order = get_object_or_404(
            Order, pk=self.kwargs["pk"]
        )

        order.delivered_to_user = True
        send_id = self.request.GET.get("sending_id")

        order.sending_id = send_id if send_id else 'تحویل شده به کاربر'
        order.save()
        messages.success(self.request, "تغییرات ثبت شد")

        if SiteSetting.objects.first().send_message_when_set_sending_id:
            send_message.delay(
                str(order.user.PhoneNumber).replace(" ", ""),
                'deliveryID',
                order.sending_id

            )

        return self.request.META.get("HTTP_REFERER")


class CancelingOrderByAdmin(AdminUserMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        order = get_object_or_404(
            Order, pk=self.kwargs["pk"]
        )

        if order.store_sold_orders.is_returned_by_admin:
            messages.info(
                self.request,
                'شما این سفارش را تصفیه کرید'
            )
            return self.request.META.get("HTTP_REFERER")

        order.is_paid = False
        order.canceled = True
        order.canceled_by_admin = True
        order.second_date = now()
        order.save()
        order.store_sold_orders.delete()

        messages.info(
            self.request,
            'سفارش کنسل شد'
        )

        return self.request.META.get("HTTP_REFERER")


class OrderListView(AdminUserMixin, ListView):
    """for listing the orders"""

    model = Order
    context_object_name = "items"
    template_name = "admin_panel/orders/list.html"
    ordering = "-id"
    paginate_by = 100

    def get_queryset(self):
        query = super().get_queryset().prefetch_related(
            'address', 'user', 'store'
        )

        query = query.order_by('-id')

        form = AdminOrderFilteringForm(self.request.GET)

        if not form.is_valid():
            return query

        data = form.cleaned_data
        if data.get("brands"):
            query = query.filter(details__product__brand=data.get("brands"))

        if data.get("category"):
            query = query.filter(details__product__category=data.get("category"))

        if data.get("store"):
            query = query.filter(store=data.get("store"))

        if features := data.get("product_features_search"):
            features = [
                feature.strip() for feature in features.split("-") if feature.strip()
            ]

            if features:
                q_obj = Q()
                for feature in features:
                    q_obj |= Q(details__product__features__title__icontains=feature)

                query = (
                    query.filter(q_obj)
                    .annotate(
                        features_info=Concat(
                            "details__product__features__title",
                            Value(" "),
                        )
                    )
                    .filter(features_info__icontains=features[0])  # جستجوی ترکیبی
                )

        if tags := data.get("product_tags_search"):
            tags = [tag.strip() for tag in tags.split("-") if tag.strip()]

            if tags:
                q_obj = Q()
                for tag in tags:
                    q_obj |= Q(details__product__tags__name__icontains=tag)

                query = (
                    query.filter(q_obj)
                    .annotate(
                        product_info=Concat(
                            "details__product__tags__name",
                            Value(" "),
                        )
                    )
                    .filter(product_info__icontains=tags[0])  # یا همینجا جستجو دقیق‌تر
                )

        if product_search := data.get("product_search"):
            names = [name.strip() for name in product_search.split("-") if name.strip()]

            if names:
                q_obj = Q()
                for name in names:
                    q_obj |= Q(details__product__name__icontains=name)

                query = (
                    query.filter(q_obj)
                    .annotate(
                        product_info=Concat(
                            "details__product__name",
                            Value(" "),
                        )
                    )
                    .filter(product_info__icontains=names[0])  # یا همینجا جستجو دقیق‌تر
                )

        # فیلتر بر اساس شماره کاربر
        if data.get("user_phone_number"):
            query = query.filter(user__PhoneNumber=data["user_phone_number"])

        # فیلتر بر اساس آدرس
        if data.get("address_search"):
            query = query.filter(
                Q(address__province__icontains=data.get("address_search")) |
                Q(address__city__icontains=data.get("address_search")) |
                Q(address__address__icontains=data.get("address_search")) |
                Q(address__zipcode__icontains=data.get("address_search")) |
                Q(
                    address__additional_decryption__icontains=data.get("address_search")
                )
            )

        # فیلتر بر اساس کد پیگیری ارسال
        if data.get("sending_id"):
            query = query.filter(sending_id__icontains=data["sending_id"])

        # فیلتر بر اساس شماره کارت
        if data.get("cart"):
            query = query.filter(cart__icontains=data["cart"])

        # فیلتر بر اساس کد پیگیری پرداخت
        if data.get("payment_id"):
            query = query.filter(payment_id__icontains=data["payment_id"])

        # فیلتر بر اساس کد تخفیف
        if data.get("discount"):
            query = query.filter(discount=data["discount"])

        # فیلتر بر اساس تاریخ باز شدن سفارش
        if data.get("start_date"):
            parts = str(data.get("start_date")).split("-")

            if len(parts) != 3:
                messages.error(
                    self.request,
                    "لطفاً تاریخ را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(year, month, day).strftime("%Y-%m-%d")
            )

            query = query.filter(date__gte=jalali_date)
        if data.get("end_date"):
            parts = str(data.get("end_date")).split("-")

            if len(parts) != 3:
                messages.error(
                    self.request,
                    "لطفاً تاریخ  را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(year, month, day).strftime("%Y-%m-%d")
            )

            query = query.filter(date__lte=jalali_date)

        # فیلتر بر اساس تاریخ پرداخت/کنسل
        if data.get("start_second_date"):
            parts = str(data.get("start_second_date")).split("-")

            if len(parts) != 3:
                messages.error(
                    self.request,
                    "لطفاً تاریخ   را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(year, month, day).strftime("%Y-%m-%d")
            )
            query = query.filter(second_date__gte=jalali_date)
        if data.get("end_second_date"):
            parts = str(data.get("end_second_date")).split("-")

            if len(parts) != 3:
                messages.error(
                    self.request,
                    "لطفاً تاریخ   را به صورت صحیح وارد کنید (فرمت: yyyy-mm-dd)",
                )

            year, month, day = map(int, parts)

            jalali_date = parse_date(
                jdatetime.date(year, month, day).strftime("%Y-%m-%d")
            )
            query = query.filter(second_date__lte=jalali_date)

        # فیلتر بر اساس نحوه ارسال
        if data.get("deliver_status"):
            if data["deliver_status"] == "11":  # پست
                query = query.filter(vip_post=True)
            elif data["deliver_status"] == "12":  # تیپاکس
                query = query.filter(tipax_post_delivery=True)
            elif data["deliver_status"] == "21":  # درون شهری
                query = query.filter(in_city_delivery=True)
            elif data["deliver_status"] == "22":  # حضوری
                query = query.filter(physical_delivery=True)

        # فیلتر بر اساس وضعیت پرداخت
        if data.get("payment_status"):
            if data["payment_status"] == "11":  # پرداخت شده
                query = query.filter(is_paid=True)
            elif data["payment_status"] == "12":  # درحال ارسال
                query = query.filter(
                    is_paid=True, sending=True, delivered_to_user=False
                )
            elif data["payment_status"] == "21":  # تحویل شده
                query = query.filter(
                    is_paid=True, sending=True, delivered_to_user=False
                )

        # فیلتر بر اساس وضعیت کلی
        if data.get("official_status"):
            if data["official_status"] == "11":  # کنسل شده
                query = query.filter(canceled=True)
            elif data["official_status"] == "12":  # پرداخت شده
                query = query.filter(is_paid=True)
            elif data["official_status"] == "21":  # باز
                query = query.filter(is_paid=False, canceled=False, is_active=True)

        # فیلتر بر اساس وضعیت فاکتور
        if data.get("invoice_status"):
            if data["invoice_status"] == "11":  # رسمی
                query = query.filter(official_invoice=True)
            elif data["invoice_status"] == "12":  # غیر رسمی
                query = query.filter(official_invoice=False)

        # فیلتر بر اساس وضعیت فاکتور رسمی
        if data.get("invoice_status_ready_pdf"):
            if data["invoice_status_ready_pdf"] == "11":  # تحویل داده شده
                query = query.filter(official_invoice_conformed_given_to_user=True)
            elif data["invoice_status_ready_pdf"] == "12":  # تحویل داده نشده
                query = query.filter(official_invoice_conformed_given_to_user=False)

        # فیلتر بر اساس وضعیت تخفیف
        if data.get("use_discount_code"):
            if data["use_discount_code"] == "11":  # با تخفیف
                query = query.filter(discount__isnull=False)
            elif data["use_discount_code"] == "12":  # بدون تخفیف
                query = query.filter(discount__isnull=True)

        # فیلتر بر اساس محدوده قیمت کل
        if data.get("min_total_price"):
            query = query.filter(total_price__gte=data["min_total_price"])
        if data.get("max_total_price"):
            query = query.filter(total_price__lte=data["max_total_price"])

        # فیلتر بر اساس محدوده وزن
        if data.get("min_total_weight"):
            query = query.filter(total_weight__gte=data["min_total_weight"])
        if data.get("max_total_weight"):
            query = query.filter(total_weight__lte=data["max_total_weight"])

        # فیلتر بر اساس ابعاد
        if data.get("min_total_length"):
            query = query.filter(total_length__gte=data["min_total_length"])
        if data.get("max_total_length"):
            query = query.filter(total_length__lte=data["max_total_length"])

        if data.get("min_total_width"):
            query = query.filter(total_width__gte=data["min_total_width"])
        if data.get("max_total_width"):
            query = query.filter(total_width__lte=data["max_total_width"])

        if data.get("min_total_height"):
            query = query.filter(total_height__gte=data["min_total_height"])
        if data.get("max_total_height"):
            query = query.filter(total_height__lte=data["max_total_height"])

        # فیلتر بر اساس قیمت تخفیف
        if data.get("min_discount_code_price"):
            query = query.filter(
                discount_code_price__gte=data["min_discount_code_price"]
            )
        if data.get("max_discount_code_price"):
            query = query.filter(
                discount_code_price__lte=data["max_discount_code_price"]
            )

        # فیلتر بر اساس قیمت ارسال
        if data.get("min_delivery_price"):
            query = query.filter(delivery_price__gte=data["min_delivery_price"])
        if data.get("max_delivery_price"):
            query = query.filter(delivery_price__lte=data["max_delivery_price"])

        # فیلتر بر اساس تعداد کالا
        if data.get("min_count_of_product"):
            query = query.filter(details__count__gte=data["min_count_of_product"])
        if data.get("max_count_of_product"):
            query = query.filter(details__count__lte=data["max_count_of_product"])

        return query.distinct()

    def get_context_data(self, *, object_list=..., **kwargs):

        context = super().get_context_data(**kwargs)

        context["form"] = AdminOrderFilteringForm()
        return context


class OrderSoldListView(AdminUserMixin, ListView):
    """for listing the orders"""

    model = StoreSoldOrders
    context_object_name = "items"
    template_name = "admin_panel/orders/sold-list.html"
    ordering = "-id"
    paginate_by = 100

    def get_queryset(self):
        return super().get_queryset().prefetch_related("store", 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stores'] = Store.objects.annotate(
            order_count=Count('store_sold_orders')
        ).filter(
            order_count__gte=1
        ).all()
        return context


class OrderDetailView(AdminUserMixin, DetailView):
    """for listing the orders"""

    model = Order
    context_object_name = "order"
    template_name = "admin_panel/orders/details.html"

    def get_object(self, queryset=None):
        order = (
            Order.objects.filter(pk=self.kwargs["pk"])
            .prefetch_related("address", "user", "store")
            .first()
        )
        return order


class OrderSoledChangeStatus(AdminUserMixin, RedirectView):
    """for change soled order status"""

    def get_redirect_url(self, *args, **kwargs):
        store_id = self.kwargs["pk"]
        items = StoreSoldOrders.objects.filter(store_id=store_id, is_returned_by_admin=False).all()

        for item in items:
            item.is_returned_by_admin = True
            item.paid_by_admin_date = now()
            item.save()

        messages.success(
            self.request,
            'حساب مورد نظر تصفیه شد'
        )

        return reverse("admin_panel:orders-sold-list")


class SpecificsOrdersListView(AdminUserMixin, ListView):
    """for listing the orders"""
    model = SpecificsOrders
    paginate_by = 100
    context_object_name = "items"
    template_name = "admin_panel/orders/specifics/list.html"

    def get_queryset(self):
        request = self.request
        queryset = self.model.objects.prefetch_related('user', 'store')
        if number := request.GET.get('number'):
            number = str(number)
            queryset = queryset.filter(user__PhoneNumber=number)

        if store := request.GET.get('store'):
            queryset = queryset.filter(store__name__icontains=store)

        return queryset.order_by("is_paid")


class SpecificsOrderDetailView(AdminUserMixin, DetailView):
    """for listing the orders"""
    model = SpecificsOrders
    context_object_name = "item"
    template_name = "admin_panel/orders/specifics/details.html"


class SpecificsOrderCreateView(AdminUserMixin, CreateView):
    """for create the orders"""

    form_class = SpecificsOrdersModelForm
    model = SpecificsOrders
    template_name = "admin_panel/orders/specifics/create.html"
    success_url = reverse_lazy("admin_panel:specifics-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            'ثبت شد'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            form.errors.as_text()
        )
        return super().form_valid(form)


class SpecificsOrdersUpdateView(AdminUserMixin, UpdateView):
    """for update the orders"""

    form_class = SpecificsOrdersModelForm
    model = SpecificsOrders
    template_name = "admin_panel/orders/specifics/create.html"
    success_url = reverse_lazy("admin_panel:specifics-list")
    context_object_name = "item"

    def form_valid(self, form):
        if self.object.is_paid:
            messages.error(
                self.request, 'شما نمی توانید فاکتوری که پرداخت شده رو بروزرسانی کنید'
            )
            return redirect("admin_panel:specifics-list")

        messages.success(
            self.request,
            'ثبت شد'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            form.errors.as_text()
        )
        return super().form_valid(form)


class SpecificsOrdersDeleteView(AdminUserMixin, RedirectView):
    """for delete orders"""

    def get_redirect_url(self, *args, **kwargs):

        obj = get_object_or_404(SpecificsOrders, pk=self.kwargs["pk"])
        if not obj.is_paid and obj.Authority is None:
            obj.delete()
            messages.success(
                self.request,
                'حذف شد'
            )

        else:
            messages.error(
                self.request,
                'شما نمی توانید فاکتور پرداخت شده رو پاک کنید'
            )
        return reverse('admin_panel:specifics-list')


# return order

class ReturnOrderList(AdminUserMixin, ListView):
    """return order list"""
    model = ReturnsOrders
    template_name = 'admin_panel/orders/returns/list.html'
    context_object_name = 'items'

    def get_queryset(self):

        queryset = super().get_queryset().prefetch_related('order', 'user').order_by('-id')

        if number := self.request.GET.get('number'):
            number = str(number)
            queryset = queryset.filter(user__PhoneNumber=number)

        if store := self.request.GET.get('store'):
            queryset = queryset.filter(order__store__name__icontains=store)

        return queryset.order_by('accept_by_store')


class ReturnOrderDetail(AdminUserMixin, DetailView):
    """return order detail"""
    model = ReturnsOrders
    template_name = 'admin_panel/orders/returns/details.html'
    context_object_name = 'item'

    def get_object(self, queryset=None):
        return get_object_or_404(ReturnsOrders, pk=self.kwargs['pk'])


class ReturnOrderAcceptByAdmin(AdminUserMixin, RedirectView):
    """return order accept by store"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(ReturnsOrders, pk=self.kwargs['pk'])
        if obj.send_request_to_return_this_order_by_admin:
            obj.date_close_request = now()
            obj.accept_by_admin = True
            obj.accept_by_store = True
            obj.save()
            messages.success(
                self.request,
                'تایید شد و مرجوعی توسط ادمین انجام میشه'
            )
        else:
            messages.error(
                self.request,
                'فروشگاه درخواست پرگشتی توسط ادمین را نداده است'
            )
        return reverse('admin_panel:return-order-list')
