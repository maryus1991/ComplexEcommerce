from django.db.models import Count
from django.views.generic import RedirectView, CreateView, UpdateView, ListView, View
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, redirect
from user.mixins.logins import AdminUserMixin
from django.contrib import messages
from django.core.files import File
from stores.models import StoreApps
from admin_panel.forms import UsedAppModelForm
from config import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
import os
import shutil
import tempfile


@method_decorator(csrf_exempt, name='dispatch')
class ChunkedFileUploadView(AdminUserMixin, View):
    def post(self, request):
        chunk = request.FILES.get('file')
        chunk_number = int(request.POST.get('chunkNumber'))
        total_chunks = int(request.POST.get('totalChunks'))
        filename = request.POST.get('filename')

        tmp_dir = os.path.join(tempfile.gettempdir(), 'chunked_uploads', filename)
        os.makedirs(tmp_dir, exist_ok=True)
        chunk_path = os.path.join(tmp_dir, f'chunk_{chunk_number}')

        with open(chunk_path, 'wb+') as f:
            for part in chunk.chunks():
                f.write(part)

        if chunk_number == total_chunks:
            temp_combined = os.path.join(tmp_dir, 'combined')
            with open(temp_combined, 'wb+') as final_file:
                for i in range(1, total_chunks + 1):
                    chunk_file = os.path.join(tmp_dir, f'chunk_{i}')
                    with open(chunk_file, 'rb') as part:
                        shutil.copyfileobj(part, final_file)

            temp_combined_path = f'uploads/tmp/{filename}'
            if default_storage.exists(temp_combined_path):
                default_storage.delete(temp_combined_path)

            with open(temp_combined, 'rb') as combined_f:
                default_storage.save(temp_combined_path, combined_f)

            shutil.rmtree(tmp_dir, ignore_errors=True)

        return JsonResponse({'status': 'ok'})


class AppsListView(AdminUserMixin, ListView):
    """
    for listing the banners
    """

    model = StoreApps
    context_object_name = "items"
    template_name = "admin_panel/apps/list.html"
    paginate_by = 20

    def get_queryset(self):
        obj = super().get_queryset().select_related(
            'store'
        ).annotate(views_count=Count('views')).order_by('-id')

        request = self.request

        if request.method == "GET":
            data = dict(request.GET.copy())
            if "is_active" in data:
                is_active = data["is_active"]
                if "on" in is_active:
                    obj = obj.filter(is_active=True)

            if "not_active" in data:
                is_active = data["not_active"]
                if "on" in is_active:
                    obj = obj.filter(is_active=False)

            if "admin_verified" in data:
                is_active = data["admin_verified"]
                if "on" in is_active:
                    obj = obj.filter(admin_verified=False)

            if "search" in data:
                search = data["search"][0]
                if search != "" and search is not None:
                    obj = obj.filter(name__icontains=search)

        return obj    

class AppsCreateView(AdminUserMixin, CreateView):
    """
    for creating a apps
    """
    model = StoreApps
    form_class = UsedAppModelForm
    template_name = "admin_panel/apps/create.html"
    success_url = reverse_lazy("admin_panel:apps-list")

    def form_valid(self, form):
        if form.cleaned_data.get('store') is None:
            messages.error(self.request, "قروشکاه رو انتخاب کنید")
            return redirect(self.request.META.get('HTTP_REFERER'))

        uploaded_filename = self.request.POST.get('uploaded_filename')
        if uploaded_filename:
            temp_storage_path = f'uploads/tmp/{uploaded_filename}'
            if default_storage.exists(temp_storage_path):
                with default_storage.open(temp_storage_path, 'rb') as f:
                    form.instance.file.save(uploaded_filename, f, save=False)
                default_storage.delete(temp_storage_path)

        messages.success(self.request, "برنامه مورد نظر با موفقیت افزوده شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.form.errors.as_text())
        return super().form_invalid(form)

class AppsUpdateView(AdminUserMixin, UpdateView):
    """for updating a apps"""

    model = StoreApps
    form_class = UsedAppModelForm
    template_name = "admin_panel/apps/create.html"
    success_url = reverse_lazy("admin_panel:apps-list")
    context_object_name = "item"


    def form_valid(self, form):

        if form.cleaned_data.get('store') is None:
            messages.error(self.request, "قروشکاه رو انتخاب کنید")
            return redirect(self.request.META.get('HTTP_REFERER'))

        uploaded_filename = self.request.POST.get('uploaded_filename')

        if uploaded_filename:
            temp_storage_path = f'uploads/tmp/{uploaded_filename}'
            if default_storage.exists(temp_storage_path):
                with default_storage.open(temp_storage_path, 'rb') as f:
                    form.instance.file.save(uploaded_filename, f, save=False)
                default_storage.delete(temp_storage_path)
        form.instance.is_active = True
        form.instance.admin_verified = True
        messages.success(self.request, "تغییرات با موفقیت اعمال شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)

class AppsActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """for activating and deactivating a apps"""

    def get_redirect_url(self, *args, **kwargs):
        app_id = kwargs.get("pk")
        app = get_object_or_404(StoreApps, pk=app_id)
        if app.admin_verified:
            app.admin_verified = False
            app.is_active = False
            app.save()
            messages.success(self.request, "برنامه مورد نظر با موفقیت غیر فعال شد")
        else:
            app.admin_verified = True
            app.is_active = True
            app.save()
            messages.success(self.request, "برنامه مورد نظر با موفقیت فعال شد")

        return reverse_lazy("admin_panel:apps-list")


class AppsDeleteView(AdminUserMixin, View):
    """for deleting a banner"""

    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        obj = get_object_or_404(StoreApps, pk=pk)
        messages.warning(
            self.request,
            f"بهتر است برنامه را غیر فعال کنید اما در صورت تمایل برای حذف اسم برنامه را وارد کنید و بعد از حذف  {obj.store.name} را مطلع کنید",
        )
        return render(self.request, "admin_panel/apps/delete.html", {"item": obj})

    def post(self, *args, **kwargs):
        pk = kwargs.get("pk")
        obj = get_object_or_404(StoreApps, pk=pk)
        confirm = self.request.POST.get("conform")

        if confirm == obj.name:
            obj.delete()
            messages.info(self.request, "برنامه مورد نظر حذف شد")
        else:
            messages.error(self.request, "لطفا اسم برنامه را درست وارد کنید")

        return redirect("admin_panel:apps-list")
