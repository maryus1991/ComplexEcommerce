# store apps
from django.views.generic import (
    RedirectView,
    View,
)
from django.shortcuts import (
    get_object_or_404,
    reverse,
    render,
    redirect,
    get_list_or_404,
)
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
from django.core.files import File

@method_decorator(csrf_exempt, name='dispatch')
class ChunkedFileUploadView(UserStoreStaffMixin, View):
    def post(self, request):
        chunk = request.FILES.get('file')
        chunk_number = int(request.POST.get('chunkNumber'))
        total_chunks = int(request.POST.get('totalChunks'))
        filename = request.POST.get('filename')

        tmp_dir = f'media/uploads/tmp/{filename}'
        os.makedirs(tmp_dir, exist_ok=True)
        chunk_path = os.path.join(tmp_dir, f'chunk_{chunk_number}')

        with open(chunk_path, 'wb+') as f:
            for part in chunk.chunks():
                f.write(part)

        if chunk_number == total_chunks:
            final_path = f'media/app/{filename}'
            with open(final_path, 'wb+') as final_file:
                for i in range(1, total_chunks + 1):
                    chunk_file = os.path.join(tmp_dir, f'chunk_{i}')
                    with open(chunk_file, 'rb') as part:
                        final_file.write(part.read())
            shutil.rmtree(tmp_dir)

        return JsonResponse({'status': 'ok'})

class StoreAppsView(UserStoreStaffMixin, View):
    """
    for store apps add and remove
    """

    def get(self, request, *args, **kwargs):
        store = request.user.store
        obj = StoreApps.objects.filter(store=store)

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

            if "search" in data:
                search = data["search"][0]
                if search != "" and search is not None:
                    obj = obj.filter(name__icontains=search)

        return render(
            request,
            "store/apps/store-apps.html",
            {"items": obj.all(), "form": AddStoreAppForm()},
        )

    from django.core.files import File

    def post(self, request, *args, **kwargs):
        store = request.user.store
        uploaded_filename = request.POST.get('uploaded_filename')

        # کپی گرفتن از POST و FILES
        post_data = request.POST.copy()
        files_data = request.FILES.copy()

        # اگه فایل قبلاً آپلود شده، فایل جدید رو نادیده بگیر
        if uploaded_filename:
            files_data.pop('file', None)

        # ساخت فرم بدون فایل جدید
        form = AddStoreAppForm(post_data, files_data)

        if form.is_valid():
            form.instance.store = store

            if uploaded_filename:
                full_path = os.path.join(settings.MEDIA_ROOT, 'app', uploaded_filename)
                if os.path.exists(full_path):
                    with open(full_path, 'rb') as f:
                        form.instance.file.save(uploaded_filename, File(f), save=False)

                    os.remove(full_path)  # اختیاری

            form.save()
            messages.success(request, "فایل شما با موفقیت ذخیره شد.")
        else:
            messages.error(request, form.errors)

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
