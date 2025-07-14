from django.shortcuts import reverse, Http404, get_object_or_404, render, redirect

from urllib.parse import urljoin

from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView, RedirectView, View
from user.mixins.logins import CustomLoginRequiredMixin as LoginRequiredMixin
from django.utils import timezone
from django.conf import settings
from django.contrib import messages

import json
import uuid
import requests

from product.models import Product
from sitesetting.models import SiteSetting
from .models import Order, OrderDetail, Discount, StoreSoldOrders, SpecificsOrders

from config.settings import (
    MERCHANT_ID,
    ZARINPAL_SEND_DATA_URL,
    ZARINPAL_REDIRECT_USER_TO_PAYMENT_PAGE,
    ZARINPAL_VERIFY_PAYMENT,
)

from django.utils.timezone import now

from stores.models import Store
from dashboard.models import UserAddress
from utils.tipax_price_calc import calculate_price

from utils.send_otp import send_message


def get_zarinpal_error_code_return_perian_message(code):
    import ZARINPAL_ERRORS
    return ZARINPAL_ERRORS.zarinpal_error_codes[code]


# Create your views here.
class SpecificsOrdersView(LoginRequiredMixin, View):
    """for list and payment the specifics orders"""

    def get(self, request, *args, **kwargs):
        orders = SpecificsOrders.objects.filter(user=request.user).order_by('is_paid').order_by('-id')
        context = {
            'items': orders.all(),
        }
        return render(request, 'dashboard/orders/specifics/list.html', context=context)

    def post(self, request, *args, **kwargs):

        order = get_object_or_404(SpecificsOrders, user=request.user, pk=request.POST.get('order_id'))

        base = "https://" if request.is_secure() else "http://"

        callback_url = (
                base
                + str(request.get_host())
                + reverse("orders:specifics-payment-verify", kwargs={"pk": order.id})
        )

        data = {
            "merchant_id": MERCHANT_ID,
            "amount": int(order.price * 10),
            "callback_url": callback_url,
            "description": f"""شماره فا کتور خاص : {order.id}
                {order.store.name}-{order.store.phone} فروشگاه و شماره ان :
                کاربر :{order.user.PhoneNumber}
                """,
            "metadata": {
                "mobile": str(request.user.PhoneNumber),
                "order_id": str(order.id),
            },
        }
        data = json.dumps(data)
        headers = {
            "content-type": "application/json",
            "content-length": str(len(data)),
        }

        try:
            response = requests.post(
                ZARINPAL_SEND_DATA_URL, data=data, headers=headers, timeout=20
            )
        except Exception as e:
            messages.error(
                request,
                'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
            )
            return redirect(self.request.META.get("HTTP_REFERER", "/"))

        if response.status_code == 200:
            authority = response.json()["data"]["authority"]
            order.Authority = authority
            order.save()
            return redirect(f"{ZARINPAL_REDIRECT_USER_TO_PAYMENT_PAGE}{authority}")

        else:
            error_code = response.json()["errors"]["code"]
            error_message = get_zarinpal_error_code_return_perian_message(
                str(error_code)
            )
            return render(
                request,
                "order/payment-failed.html",
                {"error": error_message, "order": order, "date": now(), 'specifics_order':True},
            )


class SpecificsOrdersVerifyPayment(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        order = SpecificsOrders.objects.get(pk=kwargs.get('pk'), Authority=request.GET.get('Authority'))

        data = {
            "merchant_id": MERCHANT_ID,
            "amount": int(order.price * 10),
            "authority": order.Authority,
        }

        headers = {"content-type": "application/json", "content-length": str(len(data))}

        response = requests.post(
            ZARINPAL_VERIFY_PAYMENT, data=json.dumps(data), timeout=20, headers=headers
        )

        if response.status_code == 200:
            response = response.json()
            if 101 >= response["data"]["code"] >= 100:

                order.cart_hash = response["data"]["card_hash"]
                order.cart = response["data"]["card_pan"]
                order.payment_id = response["data"]["ref_id"]
                order.ZarinPal_fee = response["data"]["fee"]
                order.is_paid = True
                order.second_date = now()
                order.save()

                try:
                    StoreSoldOrders.objects.create(
                        specifics_order=order, price=order.price, store=order.store
                    )
                except Exception as e:
                    pass

                messages.success(request, "از خرید شما متشکریم")

                return render(
                    request,
                    "order/successful-payment.html",
                    {
                        "order": order,
                        'specifics_order': True,
                    },
                )
        else:
            error_code = response.json()["errors"]["code"]
            error_message = get_zarinpal_error_code_return_perian_message(
                str(error_code)
            )
            return render(
                request,
                "order/payment-failed.html",
                {"error": error_message, "date": now(), "order": order, 'specifics_order':True},
            )


class AddOrder(LoginRequiredMixin, RedirectView):
    """
    for add product to order db
    """

    def get_redirect_url(self, *args, **kwargs):
        num: str = self.request.GET.get("count") or "1"

        # add some filters for count that get it from url
        if num and not num.isdigit() :
            return Http404()
        else:

            if int(num) < 0:
                return Http404()

        request = self.request
        product_id = kwargs.get("pk")
        product = get_object_or_404(Product,
                                    pk=product_id,
                                    is_active=True,
                                    store__is_active=True,
                                    store__is_verified=True,
                                    admin_verified=True,
                                    brand__is_active=True,
                                    category__is_active=True,
                                    )

        order = Order.objects.get_or_create(
            user=request.user,
            store=product.store,
            is_active=True,
            canceled=False,
            is_paid=False,
        )[0]

        detail = OrderDetail.objects.get_or_create(order=order, product=product)

        if product.count <= 0:
            messages.error(request, "موجودی کالا تموم شده است")
            detail[0].delete()
            return request.META.get("HTTP_REFERER", "/")

        if int(num) > product.count:
            messages.error(request, "تعداد درخواستی شما از موجودی کلا بیشتر می باشد")
            return request.META.get("HTTP_REFERER", "/")

        if not detail[1]:
            if int(num) > 0:
                detail[0].count = int(num)
            else:
                detail[0].delete()
                messages.info(request, "محصول با موقیت از سبد خرید شما حذف شد")

                return request.META.get("HTTP_REFERER", "/")

        else:

            detail[0].count = int(num)

        detail[0].get_item_price()
        detail[0].save()

        order.calculate_total_price()
        order.save()

        messages.success(request, "محصول با موفقیت به سبد خرید شما اضافه شد")

        return request.META.get("HTTP_REFERER", "/")


class CancelingOrder(LoginRequiredMixin, RedirectView):
    """
    for cansel product in order
    """

    def get_redirect_url(self, *args, **kwargs):
        order_id = kwargs.get("pk")

        order = get_object_or_404(
            Order,
            pk=order_id,
            is_active=True,
            canceled=False,
            is_paid=False,
            user=self.request.user,
        )
        order.canceled = True
        order.is_active = False
        order.second_date = timezone.now()
        order.save()
        messages.info(self.request, "سبد خرید شما با موفقیت کنسل شد")

        return reverse(
            "dashboard:orders",
        )


class RemoveItemFromOrder(LoginRequiredMixin, RedirectView):
    """
    for remove product in order detail
    """

    def get_redirect_url(self, *args, **kwargs):
        doid = kwargs.get("pk")  # get the detail of order id for verify and delete it
        obj = get_object_or_404(
            OrderDetail,
            pk=doid,
            order__user=self.request.user,
            order__is_active=True,
            order__canceled=False,
            order__is_paid=False,
        )

        obj.order.calculate_total_price()
        obj.order.save()
        oid = obj.order.id
        obj.delete()
        messages.info(self.request, "ایتم مورد نظر با موفقیت حذف شد از سبد خرید شما")

        return self.request.META.get("HTTP_REFERER", "/")


class RemoveProductFromOrder(LoginRequiredMixin, RedirectView):
    """
    for remove product in order detail with product
    """

    def get_redirect_url(self, *args, **kwargs):
        doid = kwargs.get(
            "pk"
        )  # get the product id for verify and delete the detail order of  it
        obj = get_object_or_404(Product, pk=doid)

        order = OrderDetail.objects.filter(
            order__user=self.request.user,
            product=obj,
            order__store=obj.store,
            order__is_active=True,
            order__canceled=False,
            order__is_paid=False,
        )

        if order.exists() and order.count() == 1:
            order = order.first()
            order.delete()
        else:
            return Http404()

        messages.info(self.request, "ایتم مورد نظر با موفقیت حذف شد از سبد خرید شما")
        return self.request.META.get("HTTP_REFERER", "/")


class AddAddressToOrder(LoginRequiredMixin, View):
    """
    for add address to order detail
    """

    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")  # order id
        user = request.user
        store = kwargs.get("store_id")
        address = request.POST.get("address")

        store = get_object_or_404(Store, pk=store, is_active=True, is_verified=True)
        address = UserAddress.objects.filter(pk=address, is_active=True, user=user).first()

        if address is None:
            messages.warning(request, 'ادرس مورد نظر پیدا نشد لطفا ادرس ثبت کنید')
            return redirect("dashboard:address")

        order = get_object_or_404(
            Order,
            pk=pk,
            is_active=True,
            canceled=False,
            is_paid=False,
            store=store,
            user=user,
        )
        order.delivery_price = 0
        order.vip_post = False
        order.tipax_post_delivery = False
        order.in_city_delivery = False
        order.physical_delivery = False
        order.address = address
        order.save()

        messages.success(request, "ادرس شما با موقعیت ثبت شد")

        return redirect(reverse("dashboard:order_detail", kwargs={"pk": pk}))


class ChangeInvoiceToOfficial(LoginRequiredMixin, RedirectView):
    """
    for change invoice to official
    """

    def get_redirect_url(self, *args, **kwargs):
        store_id = kwargs.get("store_id")
        order_id = kwargs.get("pk")
        user = self.request.user
        messages.error(self.request, "برای  فاکتور رسمی در انتخاب ادرس دقت فرمایید")
        if not user.legal_person:
            messages.warning(
                self.request,
                "برای دریافت فاکتور رسمی لطفا اطلاعات حقوقی خود را وارد کنید",
            )
            return reverse("dashboard:account")

        order_obj = get_object_or_404(
            Order,
            pk=order_id,
            is_active=True,
            canceled=False,
            is_paid=False,
            user=user,
            store_id=store_id,
        )

        if order_obj.official_invoice:
            order_obj.official_invoice = False
            order_obj.save()

            messages.warning(self.request, "دریافت فاکتور رسمی برای شما غیر فعال شد ")

        else:
            site = SiteSetting.objects.first()
            if site.active_receive_official_invoice:
                order_obj.official_invoice = True
                order_obj.save()

                messages.success(
                    self.request,
                    "دریافت فاکتور رسمی برای شما فعال شد بعد از اتمام پرداخت و اماده شدن و صادر شدن و ان برای دریافت  به صفحه سفارشات در داشبور خود مراجعه کنید ",
                )

        return self.request.META.get("HTTP_REFERER", "/")


class OrderSetDiscount(LoginRequiredMixin, RedirectView):
    """
    for order set discount
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        store_id = kwargs.get("store_id")
        user = self.request.user

        obj = get_object_or_404(
            Order,
            pk=pk,
            is_active=True,
            canceled=False,
            is_paid=False,
            user=user,
            store_id=store_id,
        )

        discount_name = self.request.POST.get("discount_name")

        if obj.use_discount_code:
            messages.error(self.request, "شما قبلا از کد تخفیف استفاده کرده بودید ")
            return reverse("orders:payment-conform", kwargs={"pk": pk})

        if discount_name != " ":
            if discount_name.isalnum():
                discount_obj = Discount.objects.filter(
                    name=discount_name, is_active=True
                )
                if discount_obj.exists():
                    if discount_obj.count() == 1:
                        if discount_obj.first().count > 0:
                            discount_obj = discount_obj.first()
                            if discount_obj.end_date_discount is not None and discount_obj.end_date_discount < timezone.now():
                                messages.error(
                                    self.request,
                                    "مهلت استفاده شده از این کد تخفیف با پایان رسیده",
                                )
                                return reverse(
                                    "orders:payment-conform", kwargs={"pk": pk}
                                )

                            if discount_obj.user.exists():

                                if not discount_obj.user.filter(
                                        id=user.id
                                ).exists():
                                    messages.error(
                                        self.request,
                                        "این کد تخفیف متعلق به شما نیست",
                                    )
                                    return reverse(
                                        "orders:payment-conform", kwargs={"pk": pk}
                                    )

                            if discount_obj.store.exists():
                                if not discount_obj.store.filter(
                                        id=store_id
                                ).exists():
                                    messages.error(
                                        self.request,
                                        "امکان استفاده از این کد تخفیف در این فروشگاه نمی باشد",
                                    )
                                    return reverse(
                                        "orders:payment-conform", kwargs={"pk": pk}
                                    )

                            if discount_obj.product.exists():
                                # Get product IDs from discount and order
                                discount_product_ids = set(
                                    discount_obj.product.values_list(
                                        "id", flat=True
                                    )
                                )
                                order_product_ids = set(
                                    obj.details.values_list("product_id", flat=True)
                                )

                                # Find products in order that aren't in discount
                                non_discounted_products = (
                                        order_product_ids - discount_product_ids
                                )

                                if non_discounted_products:
                                    # Get product names in a single query
                                    product_names = Product.objects.filter(
                                        id__in=non_discounted_products
                                    ).values_list("name", flat=True)

                                    messages.error(
                                        self.request,
                                        f'تخفیف برای محصولات زیر اعمال نمی‌شود: {", ".join(product_names)}',
                                    )
                                    return reverse(
                                        "orders:payment-conform", kwargs={"pk": pk}
                                    )

                            used_order_count = Order.objects.filter(user=user,
                                                                    use_discount_code=True,
                                                                    discount=discount_obj).count()

                            if used_order_count >= discount_obj.count_of_use_per_user:
                                messages.error(
                                    self.request,
                                    'شما قبلا از این کد تخفیف استفاده کردید',
                                )
                                return reverse(
                                    "orders:payment-conform", kwargs={"pk": pk}
                                )

                            order_total_price = obj.calculate_total_price()
                            discount_price = 0

                            if discount_obj.percentage_discount:
                                discount_price = order_total_price * (
                                        discount_obj.percent / 100
                                )

                            elif not discount_obj.percentage_discount:

                                discount_price = discount_obj.price

                            if obj.calculate_total_price() < discount_obj.min_price:
                                messages.error(
                                    self.request,
                                    f' حد اقل خرید برای کد تخفیف باید  {discount_obj.min_price} تومان باشد',
                                )
                                return reverse(
                                    "orders:payment-conform", kwargs={"pk": pk}
                                )

                            obj.discount = discount_obj
                            obj.discount_code_price = discount_price
                            obj.use_discount_code = True
                            obj.save()

                            messages.success(
                                self.request,
                                f"مبلق {discount_price} از خرید شما کم شد",
                            )


                        else:
                            messages.error(
                                self.request,
                                "تعداد استفاده شده از این کد تخفیف با پایان رسیده",
                            )
                    else:
                        messages.error(self.request, "کد تخفیف شما وجود ندارد")
                else:
                    messages.error(self.request, "کد تخفیف شما وجود ندارد")

            else:
                messages.error(self.request, "نام کد تخفیف باید شامل اعداد و حروف باشد")
        else:
            messages.error(self.request, "لطفا اطلاعات لازم رو به درستی بفرستید")

        return reverse("orders:payment-conform", kwargs={"pk": pk})


class OrderRemoveDiscount(LoginRequiredMixin, RedirectView):
    """
    for remove the discount from orders
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        store_id = kwargs.get("store_id")
        user = self.request.user

        obj = get_object_or_404(
            Order,
            pk=pk,
            is_active=True,
            canceled=False,
            is_paid=False,
            user=user,
            store_id=store_id,
        )

        obj.use_discount_code = False
        obj.discount_code_price = 0
        obj.discount = None
        obj.save()

        messages.success(self.request, "کد تخفیف از سفارش شما خذف شد")

        return reverse("orders:payment-conform", kwargs={"pk": pk})


class ChooseTypeOfDelivery(LoginRequiredMixin, RedirectView):
    """
    for choose type of delivery
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")
        store_id = kwargs.get("store_id")
        user = self.request.user
        delivery_id = kwargs.get("did")
        site = SiteSetting.objects.first()

        order = get_object_or_404(
            Order,
            pk=pk,
            is_active=True,
            canceled=False,
            is_paid=False,
            user=user,
            store_id=store_id,
        )


        if not order.details.exists():
            messages.error(
                self.request,
                'سبد خرید شما خالیست'
            )
            return reverse("orders:payment-conform", kwargs={"pk": pk})

        if delivery_id == 1 and site.active_post_delivery and order.store.have_post_delivery:  # delivery with post
            price = order.calculate_post_price()

            if price and price >= 1:
                order.vip_post = True
                order.tipax_post_delivery = False
                order.in_city_delivery = False
                order.physical_delivery = False
                price = order.calculate_post_price()

                order.delivery_price = price
                order.save()

            else:
                messages.warning(
                    self.request,
                    "در ارتباط با سرور جهت محسابه قیمت به مشکل برخوردیم لطفا راه ارسال دریگری را انتخاب نمایید یا گزینه تحویل حضوری را انتخاب نمایید و به فروشگاه صاحب محصول تیکیت بفرستید",
                )
                return reverse("orders:payment-conform", kwargs={"pk": pk})

        elif delivery_id == 2 and site.active_tipax_delivery and order.store.have_tipax_delivery:  # delivery with tipax

            price = order.calculate_tipax_price()
            if price and price >= 1:
                order.tipax_post_delivery = True
                order.vip_post = False
                order.in_city_delivery = False
                order.physical_delivery = False
                order.delivery_price = price
                order.save()

            else:
                messages.warning(
                    self.request,
                    "در ارتباط با سرور جهت محسابه قیمت به مشکل برخوردیم لطفا راه ارسال دریگری را انتخاب نمایید یا گزینه تحویل حضوری را انتخاب نمایید و به فروشگاه صاحب محصول تیکیت بفرستید",
                )
                return reverse("orders:payment-conform", kwargs={"pk": pk})

        elif (
                delivery_id == 3 and site.active_in_same_city_delivery and order.store.have_in_same_city_delivery and order.store.in_same_city_delivery_price
        ):  # delivery in same city
            if order.store.orgin_city_id == order.address.city_code:
                order.in_city_delivery = True
                order.tipax_post_delivery = False
                order.vip_post = False
                order.physical_delivery = False
                order.delivery_price = order.store.in_same_city_delivery_price
                order.save()

            else:
                messages.error(
                    self.request, "شهر ادرس ارسالی با شهر فروشگاه متفاوت است"
                )
                return reverse("orders:payment-conform", kwargs={"pk": pk})

        elif delivery_id == 4 and site.active_physical_delivery and order.store.have_physical_delivery:  # physical delivery

            order.physical_delivery = True
            order.in_city_delivery = False
            order.tipax_post_delivery = False
            order.vip_post = False
            order.delivery_price = 0
            order.save()

        else:
            messages.error(self.request, "لطفا در وارد کردن اطلاعات دقت فرمایید")
            return reverse("orders:payment-conform", kwargs={"pk": pk})

        messages.success(self.request, " نحوه ارسال شما با موفقیت ثبت شد")

        return reverse("orders:payment-conform", kwargs={"pk": pk})


class ConformPayment(LoginRequiredMixin, View):
    """
    for conform payment and then redirect it for payment page
    """

    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get("pk")
        self.order = get_object_or_404(
            Order,
            pk=self.pk,
            user=request.user,
            is_paid=False,
            is_active=True,
            canceled=False,
        )
        self.site = SiteSetting.objects.first()
        self.result = self.order.get_payment_price()

        self.site = SiteSetting.objects.first()

        if self.order.is_paid:
            messages.warning(request, "این سفارش پرداخت شده است")
            return redirect(reverse("dashboard:order_detail", kwargs={"pk": self.pk}))

        elif self.order.canceled:
            messages.warning(request, "این سفارش کنسل شده است")
            return redirect(reverse("dashboard:order_detail", kwargs={"pk": self.pk}))

        if self.order.address is None:
            messages.warning(request, "لطفا ادرس خود را ثبت کنید")
            return redirect(reverse("dashboard:order_detail", kwargs={"pk": self.pk}))

        if self.order.details.exists():
            if self.order.check_count_of_products() is True:
                return super().dispatch(request, *args, **kwargs)
            else:
                messages.error(
                    request,
                    "یکی از محصولات تعداد درخواستی از موجودی ان محصول بیشتر می باشد",
                )
                return redirect(
                    reverse("dashboard:order_detail", kwargs={"pk": self.pk})
                )

        else:
            messages.warning(request, "سبد شما خالی می باشد")
            return redirect(reverse("dashboard:order_detail", kwargs={"pk": self.pk}))

    def get(self, request, *args, **kwargs):

        context = {
            "order": self.order,
            "tax": self.site.tax,
            "site": self.site,
        }
        return render(request, "order/payment.html", context)

    def post(self, request, *args, **kwargs):

        if not self.site.active_zarinpal_payment:
            messages.warning(request, "درگاه پرداخت از طرف ادمین سایت غیر فعال شده است")
            return redirect("/")

        pk = self.pk
        order = self.order

        if (
                order.vip_post or
                order.tipax_post_delivery or
                order.in_city_delivery or
                order.physical_delivery
        ):

            if order.in_city_delivery:
                if order.address.city_code != order.store.orgin_city_id:
                    messages.error(
                        request,
                        "شما نمی توانید با ادرس وارد شده تحویل با پیک شهری را انتخاب کنید لطفا راه ارسال دیگری را انتخاب کنید",
                    )
                    return redirect("dashboard:order_detail", pk=pk)

            if not order.details.exists():
                messages.error(request, "سبد خرید شما خالی هست")
                return redirect("dashboard:order_detail", pk=pk)

            result = self.result

            if result <= self.site.min_payment:
                messages.warning(
                    request,
                     ' قیمت سفارش شما نباید کمتر از {:,} تومان باشد '.format(self.site.min_payment)
                )
                return redirect('orders:payment-conform', pk=pk)

            base = "https://" if request.is_secure() else "http://"

            callback_url = (
                    base
                    + str(request.get_host())
                    + reverse("orders:payment-result", kwargs={"pk": pk})
            )

            data = {
                "merchant_id": MERCHANT_ID,
                "amount": int(result * 10),
                "callback_url": callback_url,
                "description": f"""شماره فا کتور : {self.order.id}
                    {self.order.store.name}-{self.order.store.phone} فروشگاه و شماره ان :
                    کاربر :{self.order.user.PhoneNumber}
                    """,
                "metadata": {
                    "mobile": str(request.user.PhoneNumber),
                    "order_id": str(order.id),
                },
            }
            data = json.dumps(data)
            headers = {
                "content-type": "application/json",
                "content-length": str(len(data)),
            }

            try:
                response = requests.post(
                    ZARINPAL_SEND_DATA_URL, data=data, headers=headers, timeout=20
                )
            except Exception as e:
                messages.error(
                    self.request,
                    'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
                )
                return redirect(self.request.META.get("HTTP_REFERER", "/"))

            if response.status_code == 200:
                authority = response.json()["data"]["authority"]
                order = Order.objects.get(pk=self.pk)
                order.Authority = authority
                order.save()
                return redirect(f"{ZARINPAL_REDIRECT_USER_TO_PAYMENT_PAGE}{authority}")

            else:
                error_code = response.json()["errors"]["code"]
                error_message = get_zarinpal_error_code_return_perian_message(
                    str(error_code)
                )
                return render(
                    request,
                    "order/payment-failed.html",
                    {"error": error_message, "order": self.order, "date": now()},
                )

        else:
            messages.warning(request, "لطفا نحوه ارسال  را انتخاب کنید")
            return redirect("orders:payment-conform", pk=pk)


class VerifyPayment(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get("pk")
        self.authority = request.GET.get("Authority")
        self.status = request.GET.get("Status")
        self.order = get_object_or_404(
            Order,
            pk=self.pk,
            Authority=self.authority,
            is_paid=False,
            is_active=True,
            canceled=False,
        )
        self.result = self.order.get_payment_price()

        self.site = SiteSetting.objects.first()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        data = {
            "merchant_id": MERCHANT_ID,
            "amount": int(self.result * 10),
            "authority": self.authority,
        }

        headers = {"content-type": "application/json", "content-length": str(len(data))}

        response = requests.post(
            ZARINPAL_VERIFY_PAYMENT, data=json.dumps(data), timeout=20, headers=headers
        )

        if response.status_code == 200:
            response = response.json()
            if 101 >= response["data"]["code"] >= 100:
                card_hash = response["data"]["card_hash"]
                card_pan = response["data"]["card_pan"]
                payment_id = response["data"]["ref_id"]
                fee = response["data"]["fee"]

                order = Order.objects.get(pk=self.pk, Authority=self.authority)

                order.cart_hash = card_hash
                order.cart = card_pan
                order.payment_id = payment_id
                order.ZarinPal_fee = fee
                order.is_paid = True
                order.sending = True
                order.second_date = now()

                order.mines_order_detail_count_from_products_count()
                order.save()


                obj = StoreSoldOrders.objects.get_or_create(
                    order=order, price=order.total_price, store=order.store
                )
                if not obj[1]:
                    obj.price = int(obj.price) + int(self.result)
                    obj.save()

                if self.site.send_message_successful_payment:
                    send_message.delay(
                        str(order.user.PhoneNumber).replace(" ", ""),
                        """
                        از اینکه ما رو انتخاب کردید متشکریم 
                        سفارش شما در وضعیت ارسال قرار گرفت
                        """,
                    )

                messages.success(request, "از خرید شما متشکریم")

                return render(
                    request,
                    "order/successful-payment.html",
                    {
                        "order": order,
                    },
                )
        else:
            error_code = response.json()["errors"]["code"]
            error_message = get_zarinpal_error_code_return_perian_message(
                str(error_code)
            )
            return render(
                request,
                "order/payment-failed.html",
                {"error": error_message, "date": now(), "order": self.order},
            )
