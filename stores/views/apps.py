# store apps
from django.db.models import Count
from django.views.generic import (
    RedirectView,
    View,CreateView, UpdateView
)
from django.shortcuts import (
    get_object_or_404,
    reverse,
    render,
    redirect,
    get_list_or_404,
)
from admin_panel.forms import UsedAppModelForm
from django.contrib import messages
from stores.models import StoreApps
from stores.forms import AddStoreAppForm
from user.mixins.logins import UserStoreStaffMixin
from stores.validators import is_valid_message
from config import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
import os
import shutil
import tempfile
from django.urls import reverse_lazy
from django.core.files import File

@method_decorator(csrf_exempt, name='dispatch')
class ChunkedFileUploadView(UserStoreStaffMixin, View):
    def post(self, request):
        if request.user.store.can_store_add_apps :
            chunk = request.FILES.get('file')
            chunk_number = int(request.POST.get('chunkNumber'))
            total_chunks = int(request.POST.get('totalChunks'))
            filename = request.POST.get('filename')

            tmp_dir = os.path.join(tempfile.gettempdir(), 'chunked_uploads_store', filename)
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
        else:
            return JsonResponse({'status': 'error'})

class StoreAppsView(UserStoreStaffMixin, View):
    """
    for store apps add and remove
    """

    def get(self, request, *args, **kwargs):
        store = request.user.store
        obj = StoreApps.objects.filter(store=store).prefetch_related(
            'views'
        ).annotate(views_count=Count('views'))

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

        return render(
            request,
            "store/apps/store-apps.html",
            {"items": obj.all(), "form": AddStoreAppForm()},
        )


    def post(self, request, *args, **kwargs):
        store = request.user.store
        uploaded_filename = request.POST.get('uploaded_filename')

        post_data = request.POST.copy()
        files_data = request.FILES.copy()

        if uploaded_filename:
            files_data.pop('file', None)

        form = AddStoreAppForm(post_data, files_data)

        if form.is_valid():
            form.instance.store = store

            if uploaded_filename:
                temp_storage_path = f'uploads/tmp/{uploaded_filename}'
                if default_storage.exists(temp_storage_path):
                    with default_storage.open(temp_storage_path, 'rb') as f:
                        form.instance.file.save(uploaded_filename, f, save=False)
                    default_storage.delete(temp_storage_path)

            if request.user.store.store.can_store_add_apps:

                if request.user.store.allowed_to_add_and_edit_apps_with_out_admin_per:
                    form.instance.is_active = True
                    form.instance.admin_verified = True
                else:
                    form.instance.is_active = False
                    form.instance.admin_verified = False

                form.save()
                messages.success(request, "فایل شما با موفقیت ذخیره شد.")
            else:
                messages.success(request, "دسترسی ندارید")

        else:
            messages.error(request, form.errors.as_text())

        return redirect("store:app-list")


class RemoveAppsOrActiveOrDeactivateAppsView(UserStoreStaffMixin, View):
    """
    for remove apps in post method and active or deativate in get method
    """

    def get(self, request, *args, **kwargs):
        store = request.user.store
        pk = self.kwargs["pk"]
        obj = get_object_or_404(StoreApps, pk=pk, store=store)

        if obj.admin_verified:
            if obj.is_active:
                obj.is_active = False
                obj.save()
                messages.success(
                    self.request,
                    "فایل شما غیر فعال شد و کابران نمی توانند ان را دانلود و مشاهده کنند",
                )
            else:
                obj.is_active = True
                obj.save()
                messages.success(
                    self.request,
                    "فایل شما فعال شد و  کاربران می توانند انرا مشاهده کنند و ان را دانلود کنند",
                )
        else:
            messages.error(
                self.request,
                "ادمین سایت این برنامه را غیر فعال کرده است برای فعال کردن ان و انتشار ان با ادمین سایت در ارتباط باشید",
            )
        return redirect("store:app-list")

    def post(self, request, *args, **kwargs):
        store = request.user.store
        pk = self.kwargs["pk"]
        obj = get_object_or_404(
            StoreApps,
            pk=pk,
            store=store,
        )
        if obj.admin_verified:
            obj.delete()
            messages.info(self.request, "فایل شما حذف شد")
        else:
            messages.error(
                self.request,
                "ادمین سایت این برنامه را غیر فعال کرده است برای فعال کردن ان و انتشار ان با ادمین سایت در ارتباط باشید",
            )
        return redirect("store:app-list")


class AppsCreateView(UserStoreStaffMixin, CreateView):
    """
    for creating a apps
    """

    form_class = UsedAppModelForm
    template_name = "store/apps/create.html"
    success_url = reverse_lazy("store:app-list")


    def form_valid(self, form):
        form.instance.store = self.request.user.store
        request = self.request

        uploaded_filename = self.request.POST.get('uploaded_filename')
        if uploaded_filename:
            temp_storage_path = f'uploads/tmp/{uploaded_filename}'
            if default_storage.exists(temp_storage_path):
                with default_storage.open(temp_storage_path, 'rb') as f:
                    form.instance.file.save(uploaded_filename, f, save=False)
                default_storage.delete(temp_storage_path)

            if request.user.store.store.can_store_add_apps:

                if request.user.store.allowed_to_add_and_edit_apps_with_out_admin_per:
                    form.instance.is_active = True
                    form.instance.admin_verified = True
                else:
                    form.instance.is_active = False
                    form.instance.admin_verified = False

                messages.success(self.request, "فایل شما با موفقیت ذخیره شد.")
            else:
                messages.success(self.request, "دسترسی ندارید")

        else:
            messages.success(self.request, "فایل اپلود شده پیدا نشد")

        return redirect("store:app-list")

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class AppsUpdateView(UserStoreStaffMixin, UpdateView):
    """for updating a apps"""

    model = StoreApps
    form_class = UsedAppModelForm
    template_name = "store/apps/create.html"
    success_url = reverse_lazy("store:app-list")
    context_object_name = "item"


    def form_valid(self, form):
        form.instance.store = self.request.user.store
        request = self.request

        uploaded_filename = self.request.POST.get('uploaded_filename')

        if uploaded_filename:
            temp_storage_path = f'uploads/tmp/{uploaded_filename}'
            if default_storage.exists(temp_storage_path):
                with default_storage.open(temp_storage_path, 'rb') as f:
                    form.instance.file.save(uploaded_filename, f, save=False)
                default_storage.delete(temp_storage_path)

            if request.user.store.can_store_add_apps:

                if request.user.store.allowed_to_add_and_edit_apps_with_out_admin_per:
                    form.instance.is_active = True
                    form.instance.admin_verified = True
                else:
                    form.instance.is_active = False
                    form.instance.admin_verified = False

                form.save()
                messages.success(self.request, "فایل شما با موفقیت ذخیره شد.")
            else:
                messages.success(self.request, "دسترسی ندارید")

        else:
            messages.warning(self.request, "فایل اپلود شده پیدا نشد")

        return redirect("store:app-list")

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)
