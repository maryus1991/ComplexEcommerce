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
        return SiteSetting.get_cached()

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



            site = self.get_site()
            if not site or site.zero_the_count_of_all_product or not site.active_zarinpal_payment:
                return

            products_pks = [int(pk) for pk in cookie_value.split(',') if pk.strip()]
            products_by_id = Product.objects.select_related('store').in_bulk(products_pks)
            for pk in products_pks:
                product = products_by_id.get(pk)
                if ( product and product.is_active and product.admin_verified and product.count > 0 and
                    not product.store.zero_the_count_of_all_product_of_store and
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
                        product.save(update_fields=['count'])

                    messages.success(
                        request,
                        f'محصول "{product.name}" به سبد خرید شما اضافه شد'
                    )

        except Exception as e:
            messages.error(request, f"مشکلی در افزودن محصولات شده است")
            print('added_to_order_products_before_login error', e)


class SiteMiddleware(MiddlewareMixin):
    def process_request(self, request):


        def _get_active_site():
            site = SiteSetting.get_cached()
            return site if site and site.is_active else None

        request.site = SimpleLazyObject(_get_active_site)


