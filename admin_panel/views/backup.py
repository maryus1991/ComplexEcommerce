from attr.filters import exclude
from django.http import FileResponse, Http404, HttpResponseServerError, JsonResponse
from django.views.generic import View
import os
from django.core.files.storage import default_storage
from pathlib import Path
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.cache import cache
from io import StringIO
from user.mixins.logins import AdminUserMixin
import tempfile
from django.core.management import call_command
from django.utils.timezone import now, datetime
from config import settings
from django.core.files.base import ContentFile
import shutil
from contextlib import redirect_stdout
import sys
from django.utils.text import get_valid_filename


class StreamMediaZipView(View):
    def get(self, request, *args, **kwargs):
        # ساخت یه مسیر موقت برای ذخیره zip
        temp_dir = tempfile.mkdtemp()
        archive_name = 'media_' + str(now().strftime("%Y%m%d%H%M%S")) + '.zip'
        archive_path = os.path.join(temp_dir, archive_name)

        # ساخت فایل zip از پوشه MEDIA_ROOT
        shutil.make_archive(base_name=archive_path.replace('.zip', ''),
                            format='zip',
                            root_dir=settings.MEDIA_ROOT)

        # بررسی وجود فایل
        if not os.path.exists(archive_path):
            raise Http404("فایل زیپ ساخته نشد.")

        # ارسال فایل به کاربر
        response = FileResponse(open(archive_path, 'rb'), as_attachment=True, filename=archive_name)

        # پاک‌سازی بعد از ارسال (زمانی که فایل کامل ارسال شد)
        def cleanup(file_path, dir_path):
            try:
                os.remove(file_path)
                shutil.rmtree(dir_path)
            except Exception as e:
                print("خطا در پاک‌سازی:", e)

        # اضافه کردن هوک به close برای حذف فایل
        original_close = response.close

        def custom_close():
            cleanup(archive_path, temp_dir)
            original_close()

        response.close = custom_close

        return response


class OneClickBackup(AdminUserMixin, View):
    """for download the db backups with one click"""

    def get(self, request, *args, **kwargs):
        # ساخت یک فایل موقت در سیستم
        timestamp = now().strftime("%Y%m%d%H%M%S")
        filename = f"backup_{timestamp}.json"
        temp_path = os.path.join(tempfile.gettempdir(), filename)

        # اجرای دستور dumpdata و نوشتن در فایل موقت
        with open(temp_path, 'w', encoding='utf-8') as f:
            call_command(
                'dumpdata',
                exclude=['auth.permission', 'contenttypes', 'auditlog.logentry'],
                indent=2,
                stdout=f
            )

        # ساخت FileResponse برای دانلود فایل
        response = FileResponse(open(temp_path, 'rb'), as_attachment=True, filename=filename)

        # افزودن حذف فایل بعد از ارسال (با callback)
        def cleanup_file(response):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"خطا در حذف فایل موقت: {e}")

        response.close = lambda *args, **kwargs: (cleanup_file(response), FileResponse.close(response, *args, **kwargs))

        return response


class BackupRestoreInOneClickView(AdminUserMixin, View):
    """for restore the db backup with one click"""

    def get_backup_list(self):
        """تابع بهبود یافته برای دریافت لیست بکاپ‌ها با بررسی دسترسی"""
        backup_dir = os.path.join(settings.BASE_DIR, 'admin_panel/backups/db/')

        # اگر پوشه وجود ندارد، ایجادش کن
        os.makedirs(backup_dir, exist_ok=True)

        backups = []
        try:
            for filename in os.listdir(backup_dir):
                if filename.lower().endswith(('.json')):
                    filepath = os.path.join(backup_dir, filename)
                    file_info = {
                        'name': filename,
                        'path': filepath,
                        'size': f"{os.path.getsize(filepath) / (1024 * 1024):.2f} MB",
                        'date': os.path.getmtime(filepath),
                        'readable': os.access(filepath, os.R_OK)
                    }
                    backups.append(file_info)

            backups.sort(key=lambda x: x['date'], reverse=True)
            return backups

        except Exception as e:
            raise Exception(f"خطا در خواندن پوشه بکاپ: {str(e)}")

    def get(self, request):
        try:
            backups = self.get_backup_list()

        except Exception as e:
            messages.error(request, f'خطا در دریافت لیست بکاپ‌ها: {str(e)}')
            backups = []

        context = {
            'backups': backups,
            'backup_dir': os.path.join(settings.BASE_DIR, 'admin_panel/backups/db/'),
        }
        return render(request, 'admin_panel/site_setting/backup_download.html', context)

    def post(self, request):
        # عملیات ریستور
        if 'restore' in request.POST:

            backup_name = request.POST.get('backup_name')
            if not backup_name:
                messages.error(request, 'نام فایل بکاپ مشخص نشده است')
                return redirect('admin_panel:backup-restore')

            backup_path = os.path.join(settings.BASE_DIR, 'admin_panel/backups/db/', backup_name)

            # بررسی وجود فایل بکاپ
            if not os.path.exists(backup_path):
                messages.error(request, 'فایل بکاپ یافت نشد')
                return redirect('admin_panel:backup-restore')

            # بررسی صحت فایل
            try:
                file_size = os.path.getsize(backup_path)
                if file_size == 0:
                    messages.error(request, 'فایل بکاپ خالی است')
                    return redirect('admin_panel:backup-restore')
            except OSError:
                messages.error(request, 'خطا در بررسی فایل بکاپ')
                return redirect('admin_panel:backup-restore')

            try:
                call_command('loaddata', backup_path, verbosity=0)
                cache.clear()
                messages.success(request, 'بازیابی اطلاعات با موفقیت انجام شد!')
            except Exception as e:
                error_msg = f'خطا در بازیابی اطلاعات: {str(e)}'
                if 'NoneType' in str(e):
                    error_msg += ' - فایل بکاپ معتبر نیست یا آسیب دیده است'
                messages.error(request, error_msg)

            return redirect('/')

        # عملیات آپلود بکاپ جدید
        elif 'upload' in request.FILES:
            uploaded_file = request.FILES['upload']
            if not uploaded_file.name.endswith(('.json')):
                messages.error(request, 'فرمت فایل نامعتبر است')
                return redirect('admin_panel:backup-restore')

            backup_path = os.path.join(settings.BASE_DIR, 'admin_panel/backups/db/', uploaded_file.name)

            try:
                with open(backup_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                messages.success(request, 'فایل بکاپ با موفقیت آپلود شد!')
            except Exception as e:
                messages.error(request, f'خطا در آپلود فایل: {str(e)}')

        return redirect('admin_panel:backup-restore')


class MediaBackupRestoreInOneClickView(AdminUserMixin, View):
    """for restore the db backup with one click"""

    def get_backup_list(self):
        """تابع بهبود یافته برای دریافت لیست بکاپ‌ها با بررسی دسترسی"""
        backup_dir = os.path.join(settings.BASE_DIR, 'admin_panel/backups/media/')

        # اگر پوشه وجود ندارد، ایجادش کن
        os.makedirs(backup_dir, exist_ok=True)

        backups = []
        try:
            for filename in os.listdir(backup_dir):
                if filename.lower().endswith(('.zip')):
                    filepath = os.path.join(backup_dir, filename)
                    file_info = {
                        'name': filename,
                        'path': filepath,
                        'size': f"{os.path.getsize(filepath) / (1024 * 1024):.2f} MB",
                        'date': os.path.getmtime(filepath),
                        'readable': os.access(filepath, os.R_OK)
                    }
                    backups.append(file_info)

            backups.sort(key=lambda x: x['date'], reverse=True)
            return backups

        except Exception as e:
            raise Exception(f"خطا در خواندن پوشه بکاپ: {str(e)}")

    def get(self, request):
        try:
            backups = self.get_backup_list()

        except Exception as e:
            messages.error(request, f'خطا در دریافت لیست بکاپ‌ها: {str(e)}')
            backups = []

        context = {
            'backups': backups,
            'backup_dir': os.path.join(settings.BASE_DIR, 'admin_panel/backups/media'),
        }
        return render(request, 'admin_panel/site_setting/backup_media.html', context)

    def post(self, request):
        backup_name = request.POST.get('backup_name')
        if not backup_name:
            return JsonResponse({'success': False, 'error': 'نام فایل بکاپ ارسال نشده است'})

        # مسیر فایل زیپ بکاپ
        backup_path = os.path.join(settings.BASE_DIR, 'admin_panel', 'backups', 'media', backup_name)
        if not os.path.exists(backup_path):
            return JsonResponse({'success': False, 'error': 'فایل بکاپ یافت نشد'})

        media_path = settings.MEDIA_ROOT
        if not os.path.exists(media_path):
            os.makedirs(media_path)

        try:
            shutil.unpack_archive(backup_path, extract_dir=media_path)
            messages.info(request, 'فایل‌ها با موفقیت در media استخراج شدند')
            return redirect('admin_panel:backup-media-restore')
        except shutil.ReadError:
            messages.info(request, 'فرمت فایل پشتیبان پشتیبانی نمی‌شود یا خراب است')
            return redirect('admin_panel:backup-media-restore')
        except Exception as e:
            messages.info(request, f'خطا در استخراج فایل: {str(e)}')
            return redirect('admin_panel:backup-media-restore')


class UploadBackupView(AdminUserMixin, View):
    def post(self, request):
        file = request.FILES.get('upload')
        if not file:
            return JsonResponse({'success': False, 'error': 'هیچ فایلی ارسال نشده است'})

        filename = get_valid_filename(file.name)
        target_dir = os.path.join(settings.BASE_DIR, 'admin_panel', 'backups', 'media')
        os.makedirs(target_dir, exist_ok=True)

        save_path = os.path.join(target_dir, filename)

        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return JsonResponse({'success': True, 'filename': filename})
