from django.db import transaction
from sitesetting.models import SiteSetting
from django.contrib import messages
from orders.models import Order, OrderDetail
from product.models import Product
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject


class ProductCookieMiddleware:
    """مدیریت کوکی محصولات قبل از لاگین"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.site = None

    def get_site(self):
        if self.site is None:
            self.site = SiteSetting.objects.first()
        return self.site

    def __call__(self, request):

        product_cookie = request.COOKIES.get('added_to_order_products_before_login')
        if request.user.is_authenticated and request.user.is_verified and product_cookie  :
            self.process_pending_products(request, product_cookie)
            response = self.get_response(request)
            response.delete_cookie('added_to_order_products_before_login')
            return response

        return self.get_response(request)

    def process_pending_products(self, request, cookie_value):
        """پردازش محصولات معلق"""

        try:



            products_pks = cookie_value.split(',')
            for pk in products_pks:
                product = Product.objects.filter(pk=int(pk)).prefetch_related('store').first()
                if ( product and product.is_active and product.admin_verified and product.count > 0 and
                    not product.store.zero_the_count_of_all_product_of_store and
                    not self.get_site().zero_the_count_of_all_product and
                    self.get_site().active_zarinpal_payment and
                    product.store.is_active and product.store.is_verified ) :

                    with transaction.atomic():
                        order, _ = Order.objects.get_or_create(
                            user=request.user,
                            store=product.store,
                            is_active=True,
                            canceled=False,
                            is_paid=False,
                        )

                        order_detail, _ = OrderDetail.objects.get_or_create(
                            order=order,
                            product=product
                        )

                        product.count -= 1
                        product.save()

                    messages.success(
                        request,
                        f'محصول "{product.name}" به سبد خرید شما اضافه شد'
                    )

        except Exception as e:
            messages.error(request, f"مشکلی در افزودن محصولات شده است")
            print('added_to_order_products_before_login error', e)


class SiteMiddleware(MiddlewareMixin):
    def process_request(self, request):


        request.site = SimpleLazyObject(lambda: SiteSetting.objects.filter(is_active=True).first())
