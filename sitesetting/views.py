from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView, ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic.edit import FormView
import os
from wsgiref.util import FileWrapper
from mimetypes import guess_type

from orders.models import OrderDetail
from .forms import ContactForm
from .models import (
    FastLinks,

    QuestionAndAnswer,
    Newsletter,
    Slider,
    Banners,
    SiteLaw
)
from ipware import get_client_ip
from stores.models import StoreApps
from stores.models import UsedAppView as UsedAppViewModel
from config.settings import BASE_DIR
from user.forms import NumberForAddToLettersForm
from urllib.parse import quote
from product.models import Product, ProductCategory, ProductBrand
from blog.models import Blog, BlogCategory
import json
import requests
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.core.cache import cache
from easy_thumbnails.files import get_thumbnailer
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, Value, Count
from django.db.models.functions import Coalesce

class SiteLawListView(ListView):
    """for listing the law for users"""
    model = SiteLaw
    template_name = 'site/law.html'
    context_object_name = 'items'


def robots_txt(request):
    # ساختن آدرس‌های خاص برای دیس‌الو
    disallows = ["/dashboard/", "/order/", "/ckeditor/"]

    lines = ["User-Agent: *"]

    # افزودن مسیرهای مسدودشده
    for path in disallows:
        lines.append(f"Disallow: {path}")

    # اجازه ایندکس بقیه مسیرها
    lines.append("Allow: /")
    lines.append("Sitemap: https://amvajsarmad.com/sitemap.xml")
    lines.append("Sitemap: https://amvajsarmad.com/sitemap1.xml")
    lines.append("Sitemap: https://amvajsarmad.com/sitemap2.xml")
    lines.append("Sitemap: https://amvajsarmad.com/sitemap3.xml")

    # لینک کامل sitemap با پروتکل صحیح
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))

    lines.append(f"Sitemap: {sitemap_url}")

    return HttpResponse("\n".join(lines), content_type="text/plain")


def dynamic_favicon(request):
    try:
        site = self.request.site

        if site and site.logo:

            thumbnail_options = {
                'size': (32, 32),
                'crop': 'center',
                'quality': 90,
                'format': 'PNG',
                'optimize': True,
            }

            thumbnailer = get_thumbnailer(site.logo)
            thumb = thumbnailer.get_thumbnail(thumbnail_options)

            return HttpResponse(thumb.read(), content_type="image/png")

        else:

            default_path = BASE_DIR / '1111.jpg'
            if default_path.exists():
                with open(default_path, 'rb') as f:
                    return HttpResponse(f.read(), content_type="image/png")
            else:
                raise FileNotFoundError

    except Exception as e:

        default_path = BASE_DIR / '1111.jpg'
        if default_path.exists():
            with open(default_path, 'rb') as f:
                return HttpResponse(f.read(), content_type="image/png")
        else:

            return HttpResponse(status=404)


class Main(TemplateView):
    """
    main page
    """

    template_name = "index.html"



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ============================================================
        # Products
        # ============================================================
        products = Product.objects.select_related("parent", "store", "category", "brand").filter(
            is_active=True,
            count__gt=0,
        )

        context["products_newst"] = (
            products
            .order_by("-sort_number_newest_products")[:10]
        )

        context["products_most_selled"] = (
            products
            .order_by("-sort_number_most_sell")[:10]
        )

        context["products_most_discount"] = (
            products
            .filter(have_discount=True)
            .order_by("-sort_number_discount", "-discount")[:20]
        )

        # ============================================================
        # Categories / Brands / Blog Categories
        # ============================================================
        context["categories"] = (
            ProductCategory.objects
            .filter(is_active=True)
            .select_related("parent")
            .prefetch_related("child")
            .annotate(
                child_ids=Coalesce(
                    ArrayAgg(
                        "child__id",
                        distinct=True,
                        filter=Q(child__is_active=True),
                    ),
                    Value([]),
                )
            ).order_by("-sort_number")[:5]
        )

        context["brands"] = (
            ProductBrand.objects
            .filter(is_active=True)
            .order_by("-sort_number")[:5]
        )

        context["categories_blog"] = (
            BlogCategory.objects
            .filter(is_active=True)
            .order_by("-sort_number")[:5]
        )

        # ============================================================
        # Blogs
        # ============================================================
        context["blogs"] = (
            Blog.objects
            .filter(is_active=True)
            .order_by("-sort_number")[:4]
        )



        # ============================================================
        # Banners / Sliders
        # ============================================================
        is_mobile = self.request.user_agent.is_mobile

        context["Banners"] = (
            Banners.objects
            .filter(
                is_active=True,
                only_show_on_phone=is_mobile,
            )
        )

        context["Sliders"] = (
            Slider.objects
            .filter(
                is_active=True,
                only_show_on_phone=is_mobile,
            )
        )

        return context



class QuestionsPageView(TemplateView):
    """
    Q&A page
    """

    template_name = "site/questions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["questions"] = QuestionAndAnswer.objects.filter(is_active=True).all()
        return context


class AboutUs(TemplateView):
    """
    about us page
    """

    template_name = "site/aboute-us.html"



class ContactUs(SuccessMessageMixin, FormView):
    """
    contact us page
    """

    template_name = "site/contact-us.html"
    form_class = ContactForm
    success_message = "پیام شما با موفقبت ارسال شد"
    success_url = reverse_lazy("site:contact-us")


    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "لطفا در وارد کردن اطلاعات دقت کنید")
        return super().form_invalid(form)


class AddTONewsLetters(RedirectView):
    """
    for add phone number to news letters
    """

    def get_redirect_url(self, *args, **kwargs):
        form = NumberForAddToLettersForm(self.request.POST)
        if form.is_valid():
            Newsletter.objects.get_or_create(phone_number=form.cleaned_data["phone_number"])
            messages.success(self.request, "شماره شما با موفقیت اضافه شد")
        else:
            messages.warning(self.request, 'در وارد کردن شماره دقت فرمایید')

        return self.request.META.get("HTTP_REFERER", "/")


class UsedAppDetailView(DetailView):
    """
    for listing the stores apps
    """

    model = StoreApps
    context_object_name = "item"
    template_name = "site/apps/apps-details.html"

    def get_object(self, queryset=...):
        return get_object_or_404(StoreApps, pk=self.kwargs["pk"], is_active=True, admin_verified=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        context['GOOGLE_RECAPTCHA_SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY

        return context


class UsedAppView(ListView):
    """
    for listing the stores apps
    """


    paginate_by = 24
    context_object_name = "apps"
    template_name = "site/apps/apps.html"

    def get_queryset(self):
        query = (
            StoreApps.objects.select_related("store")
            .order_by("-id")
            .filter(
                is_active=True,
                store__is_active=True,
                store__is_verified=True,
                admin_verified=True,
            )
        )


        search_query = self.request.GET.get("q")

        if search_query:
            query = query.filter(
                Q(name__contains=search_query) | Q(store__name__contains=search_query)
            )

            return query

        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        context['GOOGLE_RECAPTCHA_SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY

        return context


@method_decorator(csrf_exempt, name="dispatch")
class ValidateRecaptchaView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            token = data.get("token")
            action = data.get("action", "submit")
        except Exception:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

        if not token:
            return JsonResponse({"success": False, "error": "Missing token"}, status=400)

        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                "response": token,
                "remoteip": request.META.get("REMOTE_ADDR"),
            },
        )

        result = response.json()

        if result.get("success") and result.get("action") == action and result.get("score", 0) > 0.5:
            download_token = str(uuid.uuid4())
            cache.set(f"download_token:{download_token}", True, timeout=60)

            return JsonResponse({
                "success": True,
                "token": download_token,
                "score": result.get("score"),
                "action": result.get("action"),
            })
        else:
            return JsonResponse({
                "success": False,
                "score": result.get("score"),
                "action": result.get("action"),
                "error": result.get("error-codes"),
            }, status=403)


class DownloadUsedAppView(View):
    def dispatch(self, request, *args, **kwargs):
        self.site = self.request.site
        site = self.site
        if site and site.force_users_to_login_for_download_apps:
            if not request.user.is_authenticated or not request.user.is_verified:
                messages.warning(
                    request,
                    'ابتدا وارد حساب خود شوید'
                )
                return redirect("user:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        if self.site.active_google_reCAPTCHA:
            dl_token = request.GET.get("dl_token")
            if not dl_token or not cache.get(f"download_token:{dl_token}"):
                raise Http404('token not found')

            # حذف توکن برای جلوگیری از استفاده مجدد
            cache.delete(f"download_token:{dl_token}")

        app = get_object_or_404(
            StoreApps,
            pk=self.kwargs.get("pk"),
            is_active=True,
            store__is_active=True,
            store__is_verified=True,
            admin_verified=True,
        )

        try:
            ip, is_rout = get_client_ip(request)
            app_view_object = UsedAppViewModel.objects.get_or_create(
                user=request.user if request.user.is_authenticated else None,
                app=app,
                ip=ip,
            )
            if not app_view_object[1]:
                app_view_object[0].count += 1
                app_view_object[0].save()

            if app_view_object[0].count == 0:
                app_view_object[0].count = 1
                app_view_object[0].save()

        except Exception as e:
            pass

        return self.serve_file(app)

    def serve_file(self, app):
        if not app.file:
            raise Http404("File not available")
        return redirect(app.file.url)


def custom_404_page(request, exception=None):
    return render(request, "site/404.html")


def header_render_partial(request, title=None, microdata=None):
    if request.user.is_authenticated:
        orders = OrderDetail.objects.select_related("order", "product").filter(
            order__user=request.user,
            order__is_paid=False,
            order__is_active=True,
            order__canceled=False,
        )
        orders_stats = orders.aggregate(
            orders_count=Count("order"),

        )
    else:
        orders_stats = {
            "orders_count": 0
        }
        orders = None

    try:
        if orders:
            basket_id = orders.first().order.id
        else:
            basket_id = 0
    except Exception as e:
        basket_id = 0

    title = title if title else request.site.title
    return render(request, "Base/Header/Header.html", {
        "orders": orders,
        "basket_id": basket_id,

        "orders_count": orders_stats["orders_count"],

        'title': title,
        "RECAPTCHA_PUBLIC_KEY": settings.RECAPTCHA_PUBLIC_KEY,
        "microdata": microdata,
    })




def footer_render_partial(request):

    links = FastLinks.objects.filter(is_active=True).order_by("-sort_number")

    return render(
        request,
        "Base/Footer/Footer.html",
        {

            "links1": links[0:4],

            "form": NumberForAddToLettersForm(),
            "RECAPTCHA_PUBLIC_KEY": settings.RECAPTCHA_PUBLIC_KEY,
        },
    )
