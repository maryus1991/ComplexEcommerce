from django.http import FileResponse, HttpResponseServerError
from django.views.generic import View
from django.core.management import call_command
from django.utils.timezone import datetime
import os
from pathlib import Path
from django.conf import settings
from user.mixins.logins import AdminUserMixin


class OneClickBackup(AdminUserMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            # Create a safe backup filename
            backup_name = f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.psql"
            # Use proper path join
            backup_path = Path(settings.DBBACKUP_STORAGE_OPTIONS['location']) / backup_name
            # Create backup
            call_command('dbbackup', output_filename=str(backup_name))
            # Verify file exists
            if not backup_path.exists():
                raise FileNotFoundError("Backup file was not created")
            # Return the file for download
            return FileResponse(
                open(backup_path, 'rb'),
                as_attachment=True,
                filename=backup_name
            )

        except Exception as e:
            return HttpResponseServerError(f"Backup failed: {str(e)}")