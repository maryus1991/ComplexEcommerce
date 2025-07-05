from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView, View, ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic.edit import FormView
from django.utils.text import slugify
import os
from wsgiref.util import FileWrapper
from mimetypes import guess_type
from django.db.models import Q
from django.shortcuts import Http404
from orders.models import OrderDetail
from .forms import ContactForm
from .models import (
    FastLinks,
    SiteSetting,
    QuestionAndAnswer,
    Newsletter,
    Slider,
    Banners,
)
from stores.models import StoreApps
from user.mixins.logins import CustomLoginRequiredMixin
from config.settings import BASE_DIR
from user.forms import ActiveAccountForm as NumberForAddToLettersForm

from product.models import Product, ProductCategory, ProductBrand
from blog.models import Blog, BlogCategory



def robots_txt(request):
    # ساختن آدرس‌های خاص برای دیس‌الو
    disallows = ["/user/", "/dashboard/", "/order/", "/ckeditor/"]

    lines = ["User-Agent: *"]

    # افزودن مسیرهای مسدودشده
    for path in disallows:
        lines.append(f"Disallow: {path}")

    # اجازه ایندکس بقیه مسیرها
    lines.append("Allow: /")

    # لینک کامل sitemap با پروتکل صحیح
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    print(sitemap_url)
    lines.append(f"Sitemap: {sitemap_url}")

    return HttpResponse("\n".join(lines), content_type="text/plain")


def dynamic_favicon(request):
    site = SiteSetting.objects.first()

    logo_path = site.logo.path

    if logo_path:
        with open(logo_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/png")
    else:
        with open(BASE_DIR / '1111.jpg' ,'rb') as f:
            return HttpResponse(f.read(), content_type="image/png")


# Create your views here.
class Main(TemplateView):
    """
    main page
    """

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.filter(is_active=True)

        context["Sliders"] = Slider.objects.filter(is_active=True)
        context["categories"] = (
            ProductCategory.objects.filter(is_active=True)
            .order_by("-sort_number")
            .all()[0:5]
        )
        context["brands"] = (
            ProductBrand.objects.filter(is_active=True)
            .order_by("-sort_number")
            .all()[0:5]
        )
        context["categories_blog"] = (
            BlogCategory.objects.filter(is_active=True)
            .order_by("-sort_number")
            .all()[0:5]
        )
        context["products_newst"] = products.order_by("-id").all()
        context["products_most_selled"] = products.filter().all()
        context["products_most_discount"] = (
            products.filter(have_discount=True).order_by("-discount").all()
        )
        context["Banners"] = Banners.objects.filter(is_active=True)
        context["blogs"] = Blog.objects.filter(is_active=True).all()[0:4]
        context["site"] = SiteSetting.objects.filter(is_active=True).first()

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site"] = SiteSetting.objects.filter(is_active=True).first()
        return context


class ContactUs(SuccessMessageMixin, FormView):
    """
    contact us page
    """

    template_name = "site/contact-us.html"
    form_class = ContactForm
    success_message = "پیام شما با موفقبت ارسال شد"
    success_url = reverse_lazy("site:contact-us")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["site"] = SiteSetting.objects.filter(is_active=True).first()

        return context

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
        phone = self.request.POST.get("phone_number")
        Newsletter.objects.create(phone_number=phone)
        messages.success(self.request, "شماره شما با موفقیت اضافه شد")
        return self.request.META.get("HTTP_REFERER", "/")


class UsedAppView(ListView):
    """
    for listing the stores apps
    """

    model = StoreApps
    paginate_by = 20
    context_object_name = "apps"
    template_name = "site/apps.html"

    def get_queryset(self):
        query = (
            super()
            .get_queryset()
            .order_by("-id")
            .filter(
                is_active=True,
                store__is_active=True,
                store__is_verified=True,
                admin_verified=True,
            )
        )

        # Add search functionality
        search_query = self.request.GET.get("q")
        print(search_query)
        if search_query:
            query = query.filter(
                Q(name__contains=search_query) | Q(store__name__contains=search_query)
            )

            return query

        return query


class DownloadUsedAppView(CustomLoginRequiredMixin, View):
    """
    for downloading the stores apps
    """

    def get(self, request, *args, **kwargs):
        # Get the app with all necessary validations
        app = get_object_or_404(
            StoreApps,
            pk=self.kwargs.get("pk"),
            is_active=True,
            store__is_active=True,
            store__is_verified=True,
            admin_verified=True,
        )

        # Serve the file securely
        return self.serve_file(app)

    def serve_file(self, app):
        """Securely serve the file with proper headers"""
        if not app.file or not os.path.exists(app.file.path):
            raise Http404("File not available")

        file_path = app.file.path
        file_name = f"{app.name}"
        file_size = os.path.getsize(file_path)

        response = HttpResponse(
            FileWrapper(open(file_path, "rb")), content_type=guess_type(file_path)[0]
        )

        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        response["Content-Length"] = file_size
        response["X-Accel-Redirect"] = (
            f"/protected/{os.path.basename(file_path)}"  # For nginx
        )

        return response


def custom_404_page(request, exception=None):
    return render(request, "site/404.html")


def header_render_partial(request):
    if request.user.is_authenticated:
        orders = OrderDetail.objects.filter(
            order__user=request.user,
            order__is_paid=False,
            order__is_active=True,
            order__canceled=False,
        )
    else:
        orders = None

    site = SiteSetting.objects.filter(is_active=True).first()

    return render(request, "Base/Header/Header.html", {"orders": orders, "site": site})


def footer_render_partial(request):
    site = SiteSetting.objects.filter(is_active=True).first()
    links = FastLinks.objects.all().filter(is_active=True).order_by("-id")
    return render(
        request,
        "Base/Footer/Footer.html",
        {
            "site": site,
            "links1": links[0:4],
            "links2": links[4:8],
            "form": NumberForAddToLettersForm(),
        },
    )
