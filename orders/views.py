from django.shortcuts import reverse, Http404, get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView, RedirectView, View
from user.mixins.logins import CustomLoginRequiredMixin as LoginRequiredMixin
from django.utils import timezone
from django.conf import settings
from django.contrib import messages

import json, uuid, requests

from product.models import Product
from sitesetting.models import SiteSetting
from .models import Order, OrderDetail, Discount

from config.settings import MERCHANT_ID

from stores.models import Store

from dashboard.models import UserAddress
from utils.tipax_price_calc import calculate_price


# Create your views here.

class AddOrder(LoginRequiredMixin, RedirectView):
    """
    for add product to order db
    """

    def get_redirect_url(self, *args, **kwargs):
        num: str = self.request.GET.get('count') or '1'

        # add some filters for count that get it from url
        if not num.isdigit() and num:
            return Http404()
        else:
            # todo fix this section
            if int(num) < 0:
                return Http404()

        request = self.request
        product_id = kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)

        order = Order.objects.get_or_create(user=request.user,
                                            store=product.store,
                                            is_active=True, canceled=False, is_paid=False
                                            )[0]

        detail = OrderDetail.objects.get_or_create(order=order,
                                                   product=product)

        if int(num) > product.count:
            messages.error(request, 'تعداد درخواستی شما از موجودی کلا بیشتر می باشد')
            return request.META.get('HTTP_REFERER', '/')

        if not detail[1]:

            if int(num) > 0:
                detail[0].count = int(num)
            else:
                detail[0].delete()
                messages.info(request, 'محصول با موقیت از سبد خرید شما حذف شد')

                return request.META.get('HTTP_REFERER', '/')

        else:

            detail[0].count = int(num)

        detail[0].get_item_price()
        detail[0].save()

        order.calculate_total_price()
        order.save()

        messages.success(request, 'محصول با موفقیت به سبد خرید شما اضافه شد')

        return request.META.get('HTTP_REFERER', '/')


class CancelingOrder(LoginRequiredMixin, RedirectView):
    """
    for cansel product in order
    """

    def get_redirect_url(self, *args, **kwargs):
        order_id = kwargs.get('pk')

        order = get_object_or_404(Order, pk=order_id, is_active=True, canceled=False, is_paid=False,
                                  user=self.request.user)
        order.canceled = True
        order.is_active = False
        order.second_date = timezone.now()
        order.save()
        messages.info(self.request, 'سبد خرید شما با موفقیت کنسل شد')

        return reverse('dashboard:orders', )


class RemoveItemFromOrder(LoginRequiredMixin, RedirectView):
    """
    for remove product in order detail
    """

    def get_redirect_url(self, *args, **kwargs):
        doid = kwargs.get('pk')  # get the detail of order id for verify and delete it
        obj = get_object_or_404(OrderDetail, pk=doid, order__user=self.request.user, order__is_active=True,
                                order__canceled=False, order__is_paid=False)

        obj.order.calculate_total_price()
        obj.order.save()
        oid = obj.order.id
        obj.delete()
        messages.info(self.request, 'ایتم مورد نظر با موفقیت حذف شد از سبد خرید شما')

        return self.request.META.get('HTTP_REFERER', '/')


class RemoveProductFromOrder(LoginRequiredMixin, RedirectView):
    """
    for remove product in order detail with product
    """

    def get_redirect_url(self, *args, **kwargs):
        doid = kwargs.get('pk')  # get the product id for verify and delete the detail order of  it
        obj = get_object_or_404(Product, pk=doid)

        order = OrderDetail.objects.filter(order__user=self.request.user, product=obj,
                                           order__store=obj.store, order__is_active=True,
                                           order__canceled=False, order__is_paid=False
                                           )

        if order.exists() and order.count() == 1:
            order = order.first()
            order.delete()
        else:
            return Http404()

        messages.info(self.request, 'ایتم مورد نظر با موفقیت حذف شد از سبد خرید شما')
        return self.request.META.get('HTTP_REFERER', '/')


class AddAddressToOrder(LoginRequiredMixin, View):
    """
    for add address to order detail
    """

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')  # order id
        user = request.user
        store = kwargs.get('store_id')
        address = request.POST.get('address')

        store = get_object_or_404(Store, pk=store, is_active=True, is_verified=True)
        address = get_object_or_404(UserAddress, pk=address, is_active=True, user=user)

        order = get_object_or_404(Order, pk=pk, is_active=True, canceled=False, is_paid=False, store=store, user=user)
        order.address = address
        order.save()

        messages.success(
            request,
            'ادرس شما با موقعیت ثبت شد'
        )

        return redirect(reverse('dashboard:order_detail', kwargs={'pk': pk}))


class ChangeInvoiceToOfficial(LoginRequiredMixin, RedirectView):
    """
    for change invoice to official
    """

    def get_redirect_url(self, *args, **kwargs):
        store_id = kwargs.get('store_id')
        order_id = kwargs.get('pk')
        user = self.request.user
        messages.error(self.request,
                         'برای  فاکتور رسمی در انتخاب ادرس دقت فرمایید')
        if not user.legal_person:
            messages.warning(self.request,
                             'برای دریافت فاکتور رسمی لطفا اطلاعات حقوقی خود را وارد کنید')
            return reverse('dashboard:account')

        order_obj = get_object_or_404(Order,
                                      pk=order_id, is_active=True,
                                      canceled=False, is_paid=False,
                                      user=user, store_id=store_id)

        if order_obj.official_invoice:
            order_obj.official_invoice = False
            order_obj.save()

            messages.warning(
                self.request,
                'دریافت فاکتور رسمی برای شما غیر فعال شد '
            )

        else:
            site = SiteSetting.objects.first()
            if site.active_receive_official_invoice:
                order_obj.official_invoice = True
                order_obj.save()

                messages.success(
                    self.request,
                    'دریافت فاکتور رسمی برای شما فعال شد برای دریافت ان بعد از پرداخت به صفحه سفارشات در داشبور مراجعه کنید '
                )

        return self.request.META.get('HTTP_REFERER', '/')


class OrderSetDiscount(LoginRequiredMixin, RedirectView):
    """
    for order set discount
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get('pk')
        store_id = kwargs.get('store_id')
        user = self.request.user

        obj = get_object_or_404(Order, pk=pk,
                                is_active=True,
                                canceled=False,
                                is_paid=False,
                                user=user,
                                store_id=store_id)

        discount_name = self.request.POST.get('discount_name')

        if obj.use_discount_code:
            messages.error(
                self.request, 'شما قبلا از کد تخفیف استفاده کرده بودید '
            )
            return reverse('orders:payment-conform', kwargs={'pk': pk})

        if discount_name != ' ':
            if discount_name.isalnum():
                discount_obj = Discount.objects.filter(name=discount_name, is_active=True)
                if discount_obj.exists():
                    if discount_obj.count() == 1:
                        if discount_obj.first().count > 0:
                            discount_obj = discount_obj.first()
                            if discount_obj.end_date_discount >= timezone.now():

                                if discount_obj.user is not None:

                                    if not discount_obj.user.filter(id=user.id).exists():
                                        messages.error(
                                            self.request,
                                            'این کد تخفیف متعلق به شما نیست'
                                        )
                                        return reverse('orders:payment-conform', kwargs={'pk': pk})

                                if discount_obj.store is not None:
                                    if not discount_obj.store.filter(id=store_id).exists():
                                        messages.error(
                                            self.request,
                                            'امکان استفاده از این کد تخفیف در این فروشگاه نمی باشد'
                                        )
                                        return reverse('orders:payment-conform', kwargs={'pk': pk})

                                if discount_obj.product is not None:
                                    # Get product IDs from discount and order
                                    discount_product_ids = set(discount_obj.product.values_list('id', flat=True))
                                    order_product_ids = set(obj.details.values_list('product_id', flat=True))

                                    # Find products in order that aren't in discount
                                    non_discounted_products = order_product_ids - discount_product_ids

                                    if non_discounted_products:
                                        # Get product names in a single query
                                        product_names = Product.objects.filter(
                                            id__in=non_discounted_products
                                        ).values_list('name', flat=True)

                                        messages.error(
                                            self.request,
                                            f'تخفیف برای محصولات زیر اعمال نمی‌شود: {", ".join(product_names)}'
                                        )
                                        return reverse('orders:payment-conform', kwargs={'pk': pk})

                                order_total_price = obj.calculate_total_price()
                                discount_price = 0

                                if discount_obj.percentage_discount:
                                    discount_price = (order_total_price * (discount_obj.percent / 100))

                                elif not discount_obj.percentage_discount:

                                    discount_price = discount_obj.price

                                obj.discount = discount_obj
                                obj.discount_code_price = discount_price
                                obj.use_discount_code = True
                                obj.save()

                                messages.success(
                                    self.request, f'مبلق {discount_price} از خرید شما کم شد'
                                )
                            else:
                                messages.error(
                                    self.request,
                                    'مهلت استفاده شده از این کد تخفیف با پایان رسیده'
                                )

                        else:
                            messages.error(
                                self.request,
                                'تعداد استفاده شده از این کد تخفیف با پایان رسیده'
                            )
                    else:
                        messages.error(
                            self.request,
                            'کد تخفیف شما وجود ندارد'
                        )
                else:
                    messages.error(
                        self.request,
                        'کد تخفیف شما وجود ندارد'
                    )

            else:
                messages.error(
                    self.request,
                    'نام کد تخفیف باید شامل اعداد و حروف باشد'
                )
        else:
            messages.error(
                self.request,
                'لطفا اطلاعات لازم رو به درستی بفرستید'
            )

        return reverse('orders:payment-conform', kwargs={'pk': pk})


class OrderRemoveDiscount(LoginRequiredMixin, RedirectView):
    """
    for remove the discount from orders
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get('pk')
        store_id = kwargs.get('store_id')
        user = self.request.user

        obj = get_object_or_404(Order,
                                pk=pk,
                                is_active=True,
                                canceled=False,
                                is_paid=False,
                                user=user,
                                store_id=store_id)

        obj.use_discount_code = False
        obj.discount_code_price = 0
        obj.discount = None
        obj.save()

        messages.success(
            self.request,
            'کد تخفیف از سفارش شما خذف شد'
        )

        return reverse('orders:payment-conform', kwargs={'pk': pk})


class ChooseTypeOfDelivery(LoginRequiredMixin, RedirectView):
    """
    for choose type of delivery
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get('pk')
        store_id = kwargs.get('store_id')
        user = self.request.user
        delivery_id = kwargs.get('did')

        order = get_object_or_404(Order, pk=pk,
                                  is_active=True,
                                  canceled=False,
                                  is_paid=False,
                                  user=user,
                                  store_id=store_id)



        if delivery_id == 1:  # delivery with post
            order.vip_post = True
            order.tipax_post_delivery = False
            order.in_city_delivery = False
            order.physical_delivery = False
            order.delivery_price = order.calculate_post_price()

        elif delivery_id == 2:  # delivery with tipax
            order.tipax_post_delivery = True
            order.vip_post = False
            order.in_city_delivery = False
            order.physical_delivery = False
            order.delivery_price = order.calculate_tipax_price()

        elif delivery_id == 3:  # delivery in same city
            if order.store.orgin_city_id == order.address.city_code:
                order.in_city_delivery = True
                order.tipax_post_delivery = False
                order.vip_post = False
                order.physical_delivery = False
                order.delivery_price = order.store.in_same_city_delivery_price

            else:
                messages.error(
                    self.request,
                    'شهر ادرس ارسالی با شهر فروشگاه متفاوت است'
                )
                return reverse('orders:payment-conform', kwargs={'pk': pk})


        elif delivery_id == 4:  # physical delivery

            order.physical_delivery = True
            order.in_city_delivery = False
            order.tipax_post_delivery = False
            order.vip_post = False
            order.delivery_price = 0

        else:
            messages.error(
                self.request,
                'لطفا در وارد کردن اطلاعات دقت فرمایید'
            )
            return reverse('orders:payment-conform', kwargs={'pk': pk})

        order.save()

        messages.success(
            self.request,
            ' نحوه ارسال شما با موفقیت ثبت شد'
        )

        return reverse('orders:payment-conform', kwargs={'pk': pk})


class ConformPayment(LoginRequiredMixin, View):
    """
    for conform payment and then redirect it for payment page
    """

    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk')
        self.order = get_object_or_404(Order, pk=self.pk, user=request.user)
        self.site = SiteSetting.objects.first()

        if self.order.is_paid:
            messages.warning(request, 'این سفارش پرداخت شده است')
            return redirect(reverse('dashboard:order_detail', kwargs={'pk': self.pk}))

        elif self.order.canceled:
            messages.warning(request, 'این سفارش کنسل شده است')
            return redirect(reverse('dashboard:order_detail', kwargs={'pk': self.pk}))

        if self.order.address is None:
            messages.warning(request, 'لطفا ادرس خود را ثبت کنید')
            return redirect(reverse('dashboard:order_detail', kwargs={'pk': self.pk}))

        if self.order.details.exists():
            return super().dispatch(request, *args, **kwargs)

        else:
            messages.warning(
                request, 'سبد شما خالی می باشد'
            )
            return redirect(reverse('dashboard:order_detail', kwargs={'pk': self.pk}))

    def get(self, request, *args, **kwargs):

        context = {
            'order': self.order,
            'tax': self.site.tax,
            'site': self.site,

        }
        return render(request, 'order/payment.html', context)

    def post(self, request, *args, **kwargs):
        # todo fix this section

        pk = kwargs.get('pk')
        order = get_object_or_404(Order, pk=pk, user=request.user, is_active=True, canceled=False, is_paid=False)


        if not order.details.exists():
            messages.error(request, 'سبد خرید شما خالی هست')
            return redirect('orders:payment-conform', pk=pk)

        merchant_id = MERCHANT_ID

        result = order.get_payment_price()

        if result < 100000:
            messages.warning(
                request,
                'قیمت سفارش شما نباید کمتر از100,000 تومان باشد'
            )
            return redirect('orders:payment-conform', pk=pk)

        callback_url = str(request.get_host()) + str(reverse('orders:payment-result', kwargs={'pk': pk}))

        data = {
            'merchant_id': merchant_id,
            'amount': result,
            'callback_url': callback_url,
            'description': 'توضیحات مربوط به تراکنش',
            'metadata': {'mobile': str(request.user.PhoneNumber), 'order_id': str(order.id)},
        }

        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}

        response = requests.post(
            f'https://payment.zarinpal.com/pg/v4/payment/request.json'
            , data=data, headers=headers, timeout=10)

        print(response.json())
        if response.status_code == 200:
            authority = response.json()['data']['authority']
            return redirect(f'https://payment.zarinpal.com/pg/StartPay/{authority}')

        else:
            return render(request, 'order/payment-failed.html', {'error': response.json()['errors']['message']})


class VerifyPayment(LoginRequiredMixin, View):
    pass
