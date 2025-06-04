from django.shortcuts import reverse, Http404, get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView, RedirectView, View
from user.mixins.logins import CustomLoginRequiredMixin as LoginRequiredMixin
from django.utils import timezone
from django.conf import settings
from django.contrib import messages

import requests, json, uuid

from product.models import Product
from sitesetting.models import SiteSetting
from .models import Order, OrderDetail

from config.settings import MERCHANT_ID

from stores.models import Store

from dashboard.models import UserAddress

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
        pk = kwargs.get('pk') # order id
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


class ConformPayment(LoginRequiredMixin, View):
    """
    for conform payment and then redirect it for payment page
    """
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order = get_object_or_404(Order, pk=pk, user=request.user, is_active=True, canceled=False, is_paid=False)
        tax = SiteSetting.objects.first().tax
        context = {
            'order': order,
            'tax': tax,
        }
        return render(request, 'order/payment.html', context)

    def post(self, request, *args, **kwargs):
        # todo fix this section

        addr = request.POST.get('address')
        addr = get_object_or_404(UserAddress, pk=addr, user=request.user)

        pk = kwargs.get('pk')
        order = get_object_or_404(Order, pk=pk, user=request.user, is_active=True, canceled=False, is_paid=False)
        tax = SiteSetting.objects.first().tax / 100

        if not order.details.exists():
            messages.error(request, 'سبد خرید شما خالی هست')
            return redirect('orders:payment-conform', pk=pk)

        merchant_id = MERCHANT_ID

        result = order.calculate_total_price()

        if result < 100000:
            messages.warning(
                request,
                'قیمت سفارش شما نباید کمتر از100,000 تومان باشد'
            )
            return redirect('orders:payment-conform', pk=pk)


        callback_url = str(request.get_host()) + str(reverse('orders:payment-result', kwargs={'pk': pk}))


        data = {
            'merchant_id' : merchant_id,
            'amount': int(result + (result * tax) + order.post_price) * 10,
            'callback_url': callback_url,
            'description' : 'توضیحات مربوط به تراکنش',
            'metadata' : {'mobile': str(request.user.PhoneNumber), 'order_id': str(order.id)},
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