from django.views.generic import UpdateView, RedirectView
from django.urls import reverse_lazy
from sitesetting.models import SiteSetting
from admin_panel.forms import SiteSettingModelForm
from user.mixins.logins import AdminUserMixin
from django.views.generic import View, TemplateView

from django.http import JsonResponse
from django.conf import settings
import os
from ckeditor_uploader import utils
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import redirect, reverse, HttpResponse


class UpdateSiteSettingView(AdminUserMixin, UpdateView):
    """
    for updating site setting
    """

    model = SiteSetting
    template_name = "admin_panel/site_setting/site_setting.html"
    form_class = SiteSettingModelForm
    success_url = reverse_lazy("admin_panel:update-site-setting")
    context_object_name = "site"

    def get_object(self):
        site = SiteSetting.objects
        if site.exists() and site.count() == 1:
            return site.first()
        else:
            site.all().delete()
            return site.get_or_create()[0]

    def form_valid(self, form):
        messages.success(self.request, "تنظیمات سایت با موفقیت تغییر یافت")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get("HTTP_REFERER"))


class FontManagerView(AdminUserMixin, TemplateView):
    """for show fonts list"""
    template_name = 'admin_panel/site_setting/fonts/font_manager.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        storage = utils.get_storage_class()
        user_upload_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, 'fonts')

        fonts = []
        if storage.exists(user_upload_path):
            for font_file in storage.listdir(user_upload_path)[1]:
                if font_file.lower().endswith(('.ttf', '.woff', '.woff2', '.otf')):
                    font_name = os.path.splitext(font_file)
                    font_url = storage.url(os.path.join(user_upload_path, font_file))
                    fonts.append({
                        'name': f'{str(font_name[0])}{str(font_name[1])}',
                        'file': font_file,
                        'url': font_url
                    })

        context['fonts'] = fonts
        return context

def font_list_json(request):
    storage = utils.get_storage_class()
    font_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, 'fonts')

    font_names = []

    if storage.exists(font_path):
        for font_file in storage.listdir(font_path)[1]:
            if font_file.lower().endswith(('.woff', '.woff2', '.ttf', '.otf')):
                font_name = os.path.splitext(font_file)[0]
                font_names.append(font_name)

    return JsonResponse(font_names, safe=False)

def dynamic_fonts_css(request):
    storage = utils.get_storage_class()
    font_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, 'fonts')
    fonts = []

    if storage.exists(font_path):
        for font_file in storage.listdir(font_path)[1]:
            if font_file.lower().endswith(('.woff2', '.woff', '.ttf', '.otf')):
                font_name = os.path.splitext(font_file)[0]
                font_url = storage.url(os.path.join(font_path, font_file))
                fonts.append((font_name, font_url))

    css = ""
    for name, url in fonts:
        css += f"""
@font-face {{
    font-family: '{name}';
    src: url('{url}');
}}
"""
    return HttpResponse(css, content_type='text/css')


class UploadFontView(AdminUserMixin, View):
    """for upload fonts for ckeditor"""

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('font_file')
        if not uploaded_file:
            messages.error(request, 'هیچ فایلی انتخاب نشده است')
            return redirect('font-manager')

        allowed_extensions = ('.ttf', '.woff', '.woff2', '.otf')
        if not uploaded_file.name.lower().endswith(allowed_extensions):
            messages.error(request, 'فرمت فایل مجاز نیست. فقط فایل‌های فونت قابل قبول هستند')
            return redirect('font-manager')

        user_upload_path = os.path.join(settings.MEDIA_ROOT, settings.CKEDITOR_UPLOAD_PATH,
                                        'fonts')
        if not os.path.exists(user_upload_path):
            os.makedirs(user_upload_path, mode=0o755, exist_ok=True)

        try:
            # ذخیره فایل
            file_path = os.path.join(user_upload_path, uploaded_file.name)
            default_storage.save(file_path, ContentFile(uploaded_file.read()))

            messages.success(request, f'فونت "{uploaded_file.name}" با موفقیت آپلود شد')
        except Exception as e:
            messages.error(request, f'خطا در آپلود فونت: {str(e)}')

        return redirect('admin_panel:font-manager')


class DeleteFontView(AdminUserMixin, RedirectView):
    """for delete font for ckeditor"""

    def get_redirect_url(self, *args, **kwargs):
        font_name = self.kwargs['font_name']
        if not font_name:
            messages.error(self.request, 'نام فونت مشخص نشده است')
            return reverse('admin_panel:font-manager')

        try:
            # پاکسازی نام فونت
            font_name = os.path.basename(font_name)
            phone_clean = 'fonts'

            # ساخت مسیر صحیح
            user_upload_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, phone_clean)
            font_path = os.path.join(user_upload_path, font_name)

            # اطمینان از وجود مسیر در محدوده مجاز
            if not os.path.normpath(font_path).startswith(os.path.normpath(user_upload_path)):
                raise ValueError('مسیر فونت نامعتبر است')

            if default_storage.exists(font_path):
                default_storage.delete(font_path)
                messages.success(self.request, 'فونت با موفقیت حذف شد')
            else:
                messages.warning(self.request, 'فونت مورد نظر یافت نشد')

        except Exception as e:
            messages.error(self.request, f'خطا در حذف فونت: {str(e)}')

        return reverse('admin_panel:font-manager')
