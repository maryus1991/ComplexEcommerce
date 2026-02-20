from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    ListView,
    UpdateView,
    RedirectView,
    View,
)
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    reverse,
    redirect,
)
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import (
    PermissionDenied,
    SuspiciousOperation,
)
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import UploadedFile
from orders.models import Order, StoreSoldOrders, SpecificsOrders, ReturnsOrders
from product.models import Product
from stores.models import Store
from django.utils.dateparse import parse_date
from stores.forms import OrderFilteringForm
from django.db.models import Value
from django.db.models.functions import Concat
from user.mixins.logins import UserStoreStaffMixin
import jdatetime
from utils.send_otp import send_message
from sitesetting.models import SiteSetting
from admin_panel.forms import SpecificsOrdersModelForm
from django.utils.timezone import now


# orders
class ReturnOrderList(UserStoreStaffMixin, ListView):
    """return order list"""
    model = ReturnsOrders
    template_name = 'store/orders/returns/list.html'
    context_object_name = 'items'

    def get_queryset(self):

        queryset = super().get_queryset().filter(order__store=self.request.user.store).prefetch_related('order', 'user').order_by('-id')

        if number:= self.request.GET.get('number'):
            number = str(number)
            queryset = queryset.filter(user__PhoneNumber=number)

        return queryset.order_by('accept_by_store')


class ReturnOrderDetail(UserStoreStaffMixin, DetailView):
    """return order detail"""
    model = ReturnsOrders
    template_name = 'store/orders/returns/details.html'
    context_object_name = 'item'

    def get_object(self, queryset=None):
        return get_object_or_404(ReturnsOrders, pk=self.kwargs['pk'], order__store=self.request.user.store)


class ReturnOrderAcceptByStore(UserStoreStaffMixin, RedirectView):
    """return order accept by store"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(ReturnsOrders, pk=self.kwargs['pk'], order__store=self.request.user.store)

        if obj.date_close_request is not None:
            messages.warning(
                self.request, 'توان تغییر در سفارش بسته شده وجود ندارد'
            )
            return reverse('store:return-order-list')

        if obj.accept_by_store:
            obj.accept_by_store = False
            obj.save()

            messages.error(
                self.request, 'سفارش توسط فروشگاه لغو شد'
            )

        else:
            obj.accept_by_store = True
            obj.save()

            messages.success(
                self.request, 'سفارش توسط فروشگاه تایید شد'
            )

        return reverse('store:return-order-list')


class ReturnOrderSendToAdmin(UserStoreStaffMixin, RedirectView):
    """return order accept by store"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(ReturnsOrders, pk=self.kwargs['pk'], order__store=self.request.user.store)

        if obj.date_close_request is not None:
            messages.warning(
                self.request, 'توان تغییر در سفارش بسته شده وجود ندارد'
            )
            return reverse('store:return-order-list')

        order = StoreSoldOrders.objects.filter(order=obj.order, store=self.request.user.store).first()
        if order.is_returned_by_admin:
            messages.error(
                self.request,
                'این سفارش توسط ادمین تصفیه شده و برای مرجوعی باید توسط فروشگاه انجام بشه'
            )
            return reverse('store:return-order-list')

        if obj.send_request_to_return_this_order_by_admin:
            obj.send_request_to_return_this_order_by_admin = False
            obj.save()

            messages.error(
                self.request, "مرجوعی توسط فروشگاه انجام میشود"
            )

        else:
            obj.send_request_to_return_this_order_by_admin = True
            obj.save()

            messages.success(
                self.request, 'مرجوعی توسط ادمین انجام میشود از طریق زرین پال'
            )

        return reverse('store:return-order-list')


class ReturnOrderClose(UserStoreStaffMixin, RedirectView):
    """return order accept by store"""

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(ReturnsOrders, pk=self.kwargs['pk'], order__store=self.request.user.store)

        if obj.date_close_request is not None:
            messages.warning(
                self.request, 'توان تغییر در سفارش بسته شده وجود ندارد'
            )
            return reverse('store:return-order-list')

        obj.accept_by_store = True
        obj.date_close_request = now()
        obj.save()

        for item in obj.order.details.all():
            product = item.product
            count = item.count

            product.count += count
            product.save()

        return reverse('store:return-order-list')


class StoreOrdersView(UserStoreStaffMixin, ListView):
    """
    for listing the orders
    """

    model = Order
    template_name = "store/orders/orders-list.html"
    context_object_name = "orders"
    ordering = "-id"
    paginate_by = 100

    def get_queryset(self):
        query = super().get_queryset().prefetch_related('address', 'user').filter(store=self.request.user.store).exclude(is_paid=False, canceled=False)
        query = query.exclude(canceled=True).order_by('-second_date')

        form = OrderFilteringForm(self.request.GET)

        if not form.is_valid():
            return query

        data = form.cleaned_data
        if data.get("brands"):
            query = query.filter(details__product__brand=data.get("brands"))
        if data.get("category"):
            query = query.filter(details__product__category=data.get("category"))

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
            elif data["deliver_status"] == "23":  # حضوری
                query = query.filter(freight_delivery=True)

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

        context["form"] = OrderFilteringForm()
        return context


class StoreOrderDetailView(UserStoreStaffMixin, DetailView):
    """
    for watch the detials of orders
    """

    model = Order
    template_name = "store/orders/order-detail.html"
    context_object_name = "order"

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model, pk=self.kwargs.get("pk"), store=self.request.user.store
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SpecificsOrdersModelForm(
            initial={
                'user': self.object.user,
                'store': self.request.user.store
            }
        )
        form.fields['store'].disabled = True
        form.fields['user'].disabled = True
        context["form"] = form
        return context


class AddOfficialInvoiceView(UserStoreStaffMixin, View):
    """
    Handles secure upload of official invoice PDFs for orders
    with comprehensive validation and error handling.
    """

    # Security constants
    MAX_FILE_SIZE = 50 * 1024 * 1024
    ALLOWED_MIME_TYPES = ["application/pdf"]
    ALLOWED_FILE_EXTENSIONS = [".pdf"]

    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            return self._process_invoice_upload(request, *args, **kwargs)
        except PermissionDenied as e:
            messages.error(
                request,
                "مجوز صدور فاکتور رسمی را ندارید لطفا اطلاعات خود را ویرایش منید",
            )
            return redirect("store:update")
        except SuspiciousOperation as e:
            print(e)

            messages.error(request, "فایل آپلود شده معتبر نیست")
            return redirect(
                request.META.get("HTTP_REFERER", reverse("dashboard:orders"))
            )
        except Exception as e:
            messages.error(request, "خطایی در آپلود فاکتور رخ داد")
            return redirect(
                request.META.get("HTTP_REFERER", reverse("dashboard:orders"))
            )

    def _validate_store_requirements(self, store):
        """Validate store meets all requirements for issuing official invoices"""
        requirements = {
            "have_official_invoice": False,
            "economic_number": None,
            "registration_number": None,
            "official_invoice_phone_number": None,
        }

        for field, invalid_value in requirements.items():
            if getattr(store, field) == invalid_value:
                raise PermissionDenied(f"Store missing requirement: {field}")

    def _validate_uploaded_file(self, uploaded_file):
        """Perform comprehensive validation of the uploaded file"""
        if not isinstance(uploaded_file, UploadedFile):
            raise SuspiciousOperation("Invalid file type")

        if uploaded_file.size > self.MAX_FILE_SIZE:
            raise SuspiciousOperation(
                f"File size exceeds {self.MAX_FILE_SIZE / 1024 / 1024}MB limit"
            )

        if uploaded_file.content_type not in self.ALLOWED_MIME_TYPES:
            raise SuspiciousOperation("Invalid file content type")

        if not any(
                uploaded_file.name.lower().endswith(ext)
                for ext in self.ALLOWED_FILE_EXTENSIONS
        ):
            raise SuspiciousOperation("Invalid file extension")

    def _get_validated_order(self, store, order_id):
        """Retrieve and validate the target order"""
        order = get_object_or_404(
            Order,
            pk=order_id,
            store=store,
            is_paid=True,
            canceled=False,
            is_active=True,
            official_invoice=True,
        )
        return order

    def _process_invoice_upload(self, request, *args, **kwargs):
        """Main processing logic with transaction safety"""
        order_id = kwargs.get("pk")
        store = request.user.store

        # Validate store requirements
        self._validate_store_requirements(store)

        # Validate order exists and meets criteria
        order = self._get_validated_order(store, order_id)

        # Validate file upload
        if "invoice_pdf" not in request.FILES:
            raise SuspiciousOperation("No file uploaded")

        pdf_file = request.FILES["invoice_pdf"]
        self._validate_uploaded_file(pdf_file)

        # Process in atomic transaction
        with transaction.atomic():
            order.official_invoice_conformed_given_to_user = True
            order.official_invoice_pdf = pdf_file
            order.save()

        messages.success(request, "فاکتور رسمی با موفقیت برای کاربر ارسال شد")

        if SiteSetting.objects.first().send_message_official_invoice_upload:
            send_message.delay(
                str(order.user.PhoneNumber).replace(" ", ""),
                "invoiceNotify",
                str(order.user.PhoneNumber).replace(" ", ""),

            )

        return redirect(request.META.get("HTTP_REFERER"))


class ChangeStatusToDeliveredToUser(UserStoreStaffMixin, RedirectView):
    """for set sending id and change status to DeliveredToUser"""

    def get_redirect_url(self, *args, **kwargs):

        order = get_object_or_404(
            Order, pk=self.kwargs["pk"], store=self.request.user.store
        )

        order.delivered_to_user = True
        order.sending = True
        send_id = self.request.GET.get("sending_id")
     
        order.sending_id = send_id if send_id else 'تحویل شده به کاربر'
        order.save()
        messages.success(self.request, "تغییرات ثبت شد")

        if SiteSetting.objects.first().send_message_when_set_sending_id:
            send_message.delay(
                str(order.user.PhoneNumber).replace(" ", ""),
                "deliveryID",
                order.sending_id

            )


        return self.request.META.get("HTTP_REFERER")


class StoreSoleOrders(UserStoreStaffMixin, ListView):
    """for listing the paid orders"""

    model = StoreSoldOrders
    template_name = "store/payment/list.html"
    context_object_name = "items"
    paginate_by = 100

    def get_queryset(self):
        return self.model.objects.filter(
            store_id=self.request.user.store.id
        ).order_by("is_returned_by_admin"
                   ).prefetch_related("order")

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()
        context["total_price"] = sum(list(queryset.filter(is_returned_by_admin=False).values_list("price", flat=True)))

        return context


class StoreSpecificsOrdersListView(UserStoreStaffMixin, ListView):
    """for listing the special orders"""

    model = SpecificsOrders
    paginate_by = 100
    template_name = "store/orders/specifics/list.html"
    context_object_name = "items"

    def get_queryset(self):
        request = self.request
        queryset = self.model.objects.filter(store_id=self.request.user.store.id).prefetch_related('user')
        if number:= request.GET.get('number'):
            number = str(number)
            queryset = queryset.filter(user__PhoneNumber=number)

        return queryset.order_by("is_paid")


class StoreSpecificsOrdersDetailsView(UserStoreStaffMixin, DetailView):
    """for listing the special orders"""
    model = SpecificsOrders
    context_object_name = "item"
    template_name = "store/orders/specifics/details.html"


class StoreSpecificsOrdersCreateView(UserStoreStaffMixin, RedirectView):
    """for listing the special orders"""

    def get_redirect_url(self, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs["pk"], store=self.request.user.store)
        name = self.request.POST.get("name")
        price = self.request.POST.get("price")
        SpecificsOrders.objects.create(
            user=order.user,
            store=self.request.user.store,
            name=name,
            price=price,
        )
        messages.success(
            self.request,
            'ساخته شد'
        )
        return reverse('store:specifics-list')


class StoreSpecificsOrdersUpdateView(UserStoreStaffMixin, UpdateView):
    """for listing the special orders"""
    model = SpecificsOrders
    context_object_name = "item"
    template_name = "store/orders/specifics/update.html"
    form_class = SpecificsOrdersModelForm
    success_url = reverse_lazy('store:specifics-list')

    def form_valid(self, form):
        obj = get_object_or_404(self.model, pk=self.kwargs["pk"], store=self.request.user.store)
        if not obj.is_paid:
            obj.name = form.cleaned_data.get('name')
            obj.price = form.cleaned_data.get('price')
            obj.save()
            messages.success(self.request, 'ادیت شد')
        else:
            messages.error(
                self.request, 'شما نمی توانید فاکتوری که پرداخت شده رو ادیت کنید'
            )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(
            self.request,
            form.errors.as_text()
        )
        return super().form_invalid(form)


class StoreSpecificsOrdersDeleteView(UserStoreStaffMixin, RedirectView):
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
        return reverse('store:specifics-list')
