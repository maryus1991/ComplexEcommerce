from celery import shared_task
import os
import time


@shared_task(bind=True, ignore_result=True, queue='clean')
def clean_temp_files(self, max_age_minutes=60):
    """
    Delete files older than `max_age_minutes` in the `temp_dir`.
    """

    now = time.time()
    max_age_seconds = max_age_minutes * 60

    dirs_list = [
        'admin_panel/backups/db/',
        'admin_panel/backups/media/',
        'media/uploads/tmp/'
    ]

    for temp_dir in dirs_list:
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)

            try:
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")