from django.http import FileResponse, HttpResponseServerError
from django.views.generic import View
from django.core.management import call_command
from django.utils.timezone import datetime
import os
from pathlib import Path
from django.contrib import messages
from django.shortcuts import render, redirect
from user.mixins.logins import AdminUserMixin
# from dbbackup.management.commands.dbrestore import Command as RestoreCommand
# from dbbackup.management.commands.listbackups import Command as ListBackupsCommand
from config import settings
from django.core.cache import cache
from io import StringIO
from contextlib import redirect_stdout
import sys

class OneClickBackup(AdminUserMixin, View):
    """for download the db backups with one click"""
    pass
    # def get(self, request, *args, **kwargs):
    #     try:
    #         # Create a safe backup filename
    #         backup_name = f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.psql"
    #         # Use proper path join
    #         backup_path = (
    #             Path(settings.DBBACKUP_STORAGE_OPTIONS["location"]) / backup_name
    #         )
    #         # Create backup
    #         call_command("dbbackup", output_filename=str(backup_name))
    #         # Verify file exists
    #         if not backup_path.exists():
    #             raise FileNotFoundError("Backup file was not created")
    #         # Return the file for download
    #         return FileResponse(
    #             open(backup_path, "rb"), as_attachment=True, filename=backup_name
    #         )
    #
    #     except Exception as e:
    #         return HttpResponseServerError(f"Backup failed: {str(e)}")


class BackupRestoreInOneClickView(AdminUserMixin, View):
    """for restore the db backup with one click"""
    pass
    # def get_backup_list(self):
    #     """تابع بهبود یافته برای دریافت لیست بکاپ‌ها با بررسی دسترسی"""
    #     backup_dir = os.path.join(settings.BASE_DIR, 'admin_panel/backups/')
    #
    #     # اگر پوشه وجود ندارد، ایجادش کن
    #     os.makedirs(backup_dir, exist_ok=True)
    #
    #     backups = []
    #     try:
    #         for filename in os.listdir(backup_dir):
    #             if filename.lower().endswith(('.psql')):
    #                 filepath = os.path.join(backup_dir, filename)
    #                 file_info = {
    #                     'name': filename,
    #                     'path': filepath,
    #                     'size': f"{os.path.getsize(filepath) / (1024 * 1024):.2f} MB",
    #                     'date': os.path.getmtime(filepath),
    #                     'readable': os.access(filepath, os.R_OK)
    #                 }
    #                 backups.append(file_info)
    #
    #
    #         backups.sort(key=lambda x: x['date'], reverse=True)
    #         return backups
    #
    #     except Exception as e:
    #         raise Exception(f"خطا در خواندن پوشه بکاپ: {str(e)}")
    #
    # def get(self, request):
    #     try:
    #         backups = self.get_backup_list()
    #
    #     except Exception as e:
    #         messages.error(request, f'خطا در دریافت لیست بکاپ‌ها: {str(e)}')
    #         backups = []
    #
    #     context = {
    #         'backups': backups,
    #         'backup_dir': os.path.join(settings.BASE_DIR, 'admin_panel/backups/'),
    #     }
    #     return render(request, 'admin_panel/site_setting/backup_download.html', context)
    #
    # def post(self, request):
    #     # عملیات ریستور
    #     if 'restore' in request.POST:
    #         backup_name = request.POST.get('backup_name')
    #         if not backup_name:
    #             messages.error(request, 'نام فایل بکاپ مشخص نشده است')
    #             return redirect('admin_panel:backup')
    #
    #         backup_path = os.path.join(settings.DBBACKUP_STORAGE_OPTIONS['location'], backup_name)
    #
    #         # بررسی وجود فایل بکاپ
    #         if not os.path.exists(backup_path):
    #             messages.error(request, 'فایل بکاپ یافت نشد')
    #             return redirect('admin_panel:backup')
    #
    #         # بررسی صحت فایل بکاپ
    #         try:
    #             file_size = os.path.getsize(backup_path)
    #             if file_size == 0:
    #                 messages.error(request, 'فایل بکاپ خالی است')
    #                 return redirect('admin_panel:backup')
    #         except OSError:
    #             messages.error(request, 'خطا در بررسی فایل بکاپ')
    #             return redirect('admin_panel:backup')
    #
    #         try:
    #             restore_command = RestoreCommand()
    #             restore_command.quiet = True
    #             restore_command.decrypt = True
    #             restore_command.uncompress = True
    #             restore_command.interactive = False
    #
    #             output = StringIO()
    #             with redirect_stdout(output):
    #                 restore_command.handle(
    #                     database='default',
    #                     backup_name=backup_name,
    #                     interactive=False,
    #                     decrypt=True,
    #                     uncompress=True
    #                 )
    #
    #             messages.success(request, 'بازیابی اطلاعات با موفقیت انجام شد!')
    #             cache.clear()
    #
    #         except Exception as e:
    #             error_msg = f'خطا در بازیابی اطلاعات: {str(e)}'
    #             # اگر خطای خاص NoneType بود
    #             if 'NoneType' in str(e):
    #                 error_msg += ' - فایل بکاپ معتبر نیست یا آسیب دیده است'
    #             messages.error(request, error_msg)
    #
    #     # عملیات آپلود بکاپ جدید
    #     elif 'upload' in request.FILES:
    #         uploaded_file = request.FILES['upload']
    #         if not uploaded_file.name.endswith(('.psql')):
    #             messages.error(request, 'فرمت فایل نامعتبر است')
    #             return redirect('admin_panel:backup-restore')
    #
    #         backup_path = os.path.join(settings.DBBACKUP_STORAGE_OPTIONS.get('location'), uploaded_file.name)
    #
    #         try:
    #             with open(backup_path, 'wb+') as destination:
    #                 for chunk in uploaded_file.chunks():
    #                     destination.write(chunk)
    #
    #             messages.success(request, 'فایل بکاپ با موفقیت آپلود شد!')
    #         except Exception as e:
    #             messages.error(request, f'خطا در آپلود فایل: {str(e)}')
    #
    #     return redirect('admin_panel:backup-restore')