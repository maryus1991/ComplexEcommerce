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
from django.utils.html import strip_tags
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.core.cache import cache
from easy_thumbnails.files import get_thumbnailer
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, Value, Count, F, Prefetch
from django.db.models.functions import Coalesce

class SiteLawListView(ListView):
    """for listing the law for users"""
    model = SiteLaw
    template_name = 'site/law.html'
    context_object_name = 'items'


def _get_origin(request):
    scheme = "https" if request.is_secure() else request.scheme
    return f"{scheme}://{request.get_host()}"


def _abs_url(origin, url):
    if not url:
        return ""
    if str(url).startswith(("http://", "https://")):
        return str(url)
    return f"{origin}{url}"


def _clean_text(value, max_len=160):
    if not value:
        return ""
    cleaned = " ".join(strip_tags(str(value)).split())
    if len(cleaned) > max_len:
        return cleaned[: max_len - 1].rstrip() + "…"
    return cleaned


def robots_txt(request):
    origin = _get_origin(request)
    disallows = [
        "/admin/",
        "/admin-panel/",
        "/store-panel/",
        "/dashboard/",
        "/order/",
        "/cart/",
        "/checkout/",
        "/account/",
        "/user/",
        "/ckeditor/",
    ]

    lines = [
        "User-agent: *",
        "Allow: /",
        "Allow: /llms.txt",
        "Allow: /ai-catalog.json",
    ]
    for path in disallows:
        lines.append(f"Disallow: {path}")

    lines.append("")
    lines.append(f"Sitemap: {origin}{reverse('sitemap')}")
    lines.append("")
    # lines.append("# AI / Agentic Discovery")
    # lines.append(f"llms-txt: {origin}{reverse('llms-txt')}")

    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


def llms_txt(request):
    """
    Serve /llms.txt according to the llms.txt specification (text/markdown; charset=utf-8).
    """
    origin = _get_origin(request)
    site = getattr(request, "site", None)
    site_title = (getattr(site, "title", None) or "فروشگاه اینترنتی").strip()
    site_desc = _clean_text(getattr(site, "short_description", None), max_len=240) or f"فروشگاه آنلاین {site_title}"

    categories = (
        ProductCategory.objects.filter(is_active=True)
        .annotate(active_products=Count("products", filter=Q(products__is_active=True, products__admin_verified=True)))
        .order_by("-sort_number", "id")[:30]
    )
    brands = ProductBrand.objects.filter(is_active=True).order_by("-sort_number", "id")[:30]
    products = (
        Product.objects.select_related("brand", "category", "store")
        .filter(
            is_active=True,
            admin_verified=True,
            store__is_active=True,
            store__is_verified=True,
            count__gt=0,
        )
        .order_by("-sort_number", "-id")[:30]
    )
    blogs = (
        Blog.objects.select_related("category")
        .filter(is_active=True, admin_verified=True)
        .order_by("-updated_at")[:15]
    )

    lines = [
        f"# {site_title}",
        "",
        f"> {site_desc}",
        "",
        "## Main Pages",
        f"- [صفحه اصلی ({site_title})]({origin}{reverse('site:main')}): فروشگاه اصلی، پیشنهادهای ویژه و جدیدترین محصولات",
        f"- [فروشگاه و لیست محصولات]({origin}{reverse('product:list')}): مشاهده، فیلتر و جستجوی تمامی محصولات",
        f"- [مقالات و راهنماها]({origin}{reverse('blog:list')}): مقالات تخصصی، آموزش‌ها و راهنمای خرید",
        f"- [فروشگاه‌های همکار]({origin}{reverse('stores:main-template-list')}): لیست فروشندگان و فروشگاه‌های تاییدشده",
        f"- [برنامه‌های کاربردی]({origin}{reverse('site:apps-list')}): نرم‌افزارها و ابزارهای کاربردی قابل دانلود",
        f"- [استعلام گارانتی]({origin}{reverse('guarantee:serial-number-search')}): بررسی اصالت و وضعیت گارانتی محصولات",
        f"- [درباره ما]({origin}{reverse('site:about-us')}): معرفی {site_title} و اطلاعات مجموعه",
        f"- [تماس با ما]({origin}{reverse('site:contact-us')}): اطلاعات تماس، آدرس و فرم ارتباط با پشتیبانی",
        f"- [سوالات متداول]({origin}{reverse('site:Q&A')}): پاسخ به پرسش‌های پرتکرار خریداران",
        f"- [قوانین و مقررات]({origin}{reverse('site:site-law')}): شرایط استفاده و قوانین خرید",
        f"- [نقشه سایت (XML Sitemap)]({origin}{reverse('sitemap')}): فهرست کامل صفحات ایندکس‌پذیر",
        f"- [کاتالوگ ماشینی (AI Catalog JSON)]({origin}{reverse('ai-catalog-json')}): مانیفست ساختاریافته کاتالوگ فروشگاه برای ایجنت‌ها",
    ]

    if categories:
        lines.extend(["", "## Product Categories"])
        for cat in categories:
            cat_url = _abs_url(origin, cat.get_absolute_url())
            lines.append(f"- [{cat.name}]({cat_url}): دسته محصولات {cat.name} ({cat.active_products} محصول فعال)")

    if products:
        lines.extend(["", "## Featured Products"])
        for prod in products:
            prod_url = _abs_url(origin, prod.get_absolute_url())
            price = prod.calc_discount() if getattr(prod, "have_discount", False) else prod.price
            brand_name = prod.brand.name if prod.brand_id else ""
            cat_name = prod.category.name if prod.category_id else ""
            meta_parts = [p for p in [brand_name, cat_name, f"{price:,} تومان" if price else ""] if p]
            meta_str = " | ".join(meta_parts) if meta_parts else "محصول موجود در فروشگاه"
            lines.append(f"- [{prod.name}]({prod_url}): {meta_str}")

    if brands:
        lines.extend(["", "## Brands"])
        for brand in brands:
            brand_url = _abs_url(origin, brand.get_absolute_url())
            lines.append(f"- [{brand.name}]({brand_url}): محصولات برند {brand.name}")

    if blogs:
        lines.extend(["", "## Articles & Guides"])
        for post in blogs:
            post_url = _abs_url(origin, post.get_absolute_url())
            cat_label = f"دسته‌بندی {post.category.name}" if post.category_id else "مقاله تخصصی"
            lines.append(f"- [{post.title}]({post_url}): {cat_label}")

    return HttpResponse("\n".join(lines) + "\n", content_type="text/markdown; charset=utf-8")


def ai_catalog_json(request):
    """
    Serve /ai-catalog.json according to the AI Resource Discovery (ARD) specification.
    """
    origin = _get_origin(request)
    site = getattr(request, "site", None)
    site_title = (getattr(site, "title", None) or "فروشگاه اینترنتی").strip()
    site_desc = _clean_text(getattr(site, "short_description", None), max_len=240) or f"فروشگاه آنلاین {site_title}"
    logo_url = _abs_url(origin, site.logo.url) if site and getattr(site, "logo", None) else ""

    categories = (
        ProductCategory.objects.filter(is_active=True)
        .annotate(active_products=Count("products", filter=Q(products__is_active=True, products__admin_verified=True)))
        .order_by("-sort_number", "id")[:50]
    )
    brands = ProductBrand.objects.filter(is_active=True).order_by("-sort_number", "id")[:50]
    products = (
        Product.objects.select_related("brand", "category", "store")
        .filter(
            is_active=True,
            admin_verified=True,
            store__is_active=True,
            store__is_verified=True,
        )
        .order_by("-count", "-sort_number", "-id")[:50]
    )
    blogs = (
        Blog.objects.select_related("category")
        .filter(is_active=True, admin_verified=True)
        .order_by("-updated_at")[:20]
    )

    same_as = []
    if site:
        if getattr(site, "instagram_link", None):
            same_as.append(site.instagram_link)
        if getattr(site, "telegram_link", None):
            same_as.append(site.telegram_link)

    payload = {
        "schema_version": "1.0",
        "name": site_title,
        "description": site_desc,
        "language": "fa-IR",
        "base_url": origin,
        "discovery": {
            "llms_txt": f"{origin}{reverse('llms-txt')}",
            "ai_catalog": f"{origin}{reverse('ai-catalog-json')}",
            "sitemap": f"{origin}{reverse('sitemap')}",
            "robots_txt": f"{origin}{reverse('robots-txt')}",
        },
        "organization": {
            "name": site_title,
            "url": f"{origin}/",
            "logo": logo_url,
            "email": getattr(site, "email", "") or "",
            "telephone": str(getattr(site, "phone", "") or ""),
            "address": getattr(site, "address", "") or "",
            "same_as": same_as,
        },
        "endpoints": {
            "home": f"{origin}{reverse('site:main')}",
            "products": f"{origin}{reverse('product:list')}",
            "product_search": {
                "url_template": f"{origin}{reverse('product:list')}?search={{query}}",
                "method": "GET",
                "query_parameter": "search",
            },
            "blog": f"{origin}{reverse('blog:list')}",
            "stores": f"{origin}{reverse('stores:main-template-list')}",
            "apps": f"{origin}{reverse('site:apps-list')}",
            "guarantee": f"{origin}{reverse('guarantee:serial-number-search')}",
            "about": f"{origin}{reverse('site:about-us')}",
            "contact": f"{origin}{reverse('site:contact-us')}",
            "faq": f"{origin}{reverse('site:Q&A')}",
        },
        "categories": [
            {
                "id": cat.id,
                "name": cat.name,
                "url": _abs_url(origin, cat.get_absolute_url()),
                "product_count": cat.active_products,
            }
            for cat in categories
        ],
        "brands": [
            {
                "id": brand.id,
                "name": brand.name,
                "url": _abs_url(origin, brand.get_absolute_url()),
            }
            for brand in brands
        ],
        "featured_products": [
            {
                "id": prod.id,
                "name": prod.name,
                "url": _abs_url(origin, prod.get_absolute_url()),
                "brand": prod.brand.name if prod.brand_id else None,
                "category": prod.category.name if prod.category_id else None,
                "seller": prod.store.name if prod.store_id else None,
                "price": prod.price,
                "discounted_price": prod.calc_discount() if getattr(prod, "have_discount", False) else prod.price,
                "currency": "IRT",
                "availability": "InStock" if prod.count > 0 else "OutOfStock",
                "image": _abs_url(origin, prod.picture.url) if prod.picture else None,
            }
            for prod in products
        ],
        "latest_articles": [
            {
                "id": post.id,
                "title": post.title,
                "url": _abs_url(origin, post.get_absolute_url()),
                "category": post.category.name if post.category_id else None,
                "updated_at": post.updated_at.isoformat() if post.updated_at else None,
            }
            for post in blogs
        ],
    }

    return JsonResponse(
        payload,
        content_type="application/json; charset=utf-8",
        json_dumps_params={"ensure_ascii": False, "indent": 2},
    )


def dynamic_favicon(request):
    try:
        site = getattr(request, "site", None)

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
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=BlogCategory.objects.filter(is_active=True).order_by("-sort_number"),
                )
            )
            .order_by("-sort_number")[:5]
        )

        # ============================================================
        # Blogs
        # ============================================================
        context["blogs"] = (
            Blog.objects
            .filter(is_active=True)
            .select_related("store", "category")
            .annotate(views_count=Count("views"))
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
        return get_object_or_404(
            StoreApps.objects.select_related("store"),
            pk=self.kwargs["pk"],
            is_active=True,
            admin_verified=True,
        )

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
            app_view_object, created = UsedAppViewModel.objects.get_or_create(
                user=request.user if request.user.is_authenticated else None,
                app=app,
                ip=ip,
                defaults={"count": 1},
            )
            if not created:
                UsedAppViewModel.objects.filter(pk=app_view_object.pk).update(
                    count=F("count") + 1
                )

        except Exception as e:
            pass

        return self.serve_file(app)

    def serve_file(self, app):
        if not app.file:
            raise Http404("File not available")
        return redirect(app.file.url)


def custom_404_page(request, exception=None):
    return render(request, "site/404.html", status=404)


def header_render_partial(
    request,
    title=None,
    microdata=None,
    meta_description=None,
    og_type=None,
    og_image=None,
    seo_robots_override=None,
    canonical_override=None,
    extra_meta=None,
):
    if request.user.is_authenticated:
        orders = list(
            OrderDetail.objects.select_related("order", "product").filter(
                order__user=request.user,
                order__is_paid=False,
                order__is_active=True,
                order__canceled=False,
            )
        )
        orders_count = len(orders)
        basket_id = orders[0].order_id if orders else 0
    else:
        orders = None
        orders_count = 0
        basket_id = 0

    site = getattr(request, "site", None)
    origin = _get_origin(request)
    site_title = getattr(site, "title", "") if site else ""
    clean_title = " ".join(str(title or "").split()) or site_title
    clean_description = _clean_text(meta_description, max_len=160) or _clean_text(
        getattr(site, "short_description", ""), max_len=160
    )
    clean_og_type = " ".join(str(og_type or "").split()) or "website"

    raw_og_image = " ".join(str(og_image or "").split())
    if raw_og_image:
        resolved_og_image = _abs_url(origin, raw_og_image)
    elif site and getattr(site, "logo", None):
        resolved_og_image = _abs_url(origin, site.logo.url)
    else:
        resolved_og_image = ""

    clean_microdata = (microdata or "").strip()
    clean_robots = " ".join(str(seo_robots_override or "").split())
    clean_canonical = " ".join(str(canonical_override or "").split())

    return render(request, "Base/Header/Header.html", {
        "orders": orders,
        "basket_id": basket_id,
        "orders_count": orders_count,
        "title": clean_title,
        "meta_description": clean_description,
        "og_type": clean_og_type,
        "og_image": resolved_og_image,
        "seo_robots_override": clean_robots,
        "canonical_override": clean_canonical,
        "extra_meta": (extra_meta or "").strip(),
        "RECAPTCHA_PUBLIC_KEY": settings.RECAPTCHA_PUBLIC_KEY,
        "microdata": clean_microdata,
    })


def footer_render_partial(request):
    links = FastLinks.get_cached_footer_links()

    return render(
        request,
        "Base/Footer/Footer.html",
        {
            "links1": links,
            "form": NumberForAddToLettersForm(),
            "RECAPTCHA_PUBLIC_KEY": settings.RECAPTCHA_PUBLIC_KEY,
        },
    )
