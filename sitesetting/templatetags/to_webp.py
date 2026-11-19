from django import template
from PIL import Image
import io
from urllib.parse import urlparse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

register = template.Library()


@register.filter
def to_webp(image_url):
    try:
        if not image_url:
            return '/static/images/1111.jpg'

        # If already a webp, return as is
        clean_url = str(image_url).split('?')[0]
        if clean_url.lower().endswith('.webp'):
            return image_url

        # Determine relative storage path from URL
        image_path = None
        media_url = getattr(settings, 'MEDIA_URL', '')
        if media_url and image_url.startswith(media_url):
            image_path = image_url[len(media_url):].lstrip('/')
        elif image_url.startswith('http://') or image_url.startswith('https://'):
            parsed = urlparse(image_url)
            path = parsed.path.lstrip('/')
            bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
            if bucket and path.startswith(f"{bucket}/"):
                path = path[len(bucket) + 1:]
            location = getattr(settings, 'AWS_LOCATION', '')
            if location and path.startswith(f"{location}/"):
                path = path[len(location) + 1:]
            image_path = path
        else:
            image_path = str(image_url).lstrip('/')

        if not image_path or ('.' not in image_path):
            return image_url

        webp_path = image_path.rsplit('.', 1)[0] + '.webp'

        if default_storage.exists(webp_path):
            return default_storage.url(webp_path)

        if default_storage.exists(image_path):
            try:
                with default_storage.open(image_path, 'rb') as f:
                    img = Image.open(f)
                    buffer = io.BytesIO()
                    img.save(buffer, 'WEBP', quality=85)
                    buffer.seek(0)
                    default_storage.save(webp_path, ContentFile(buffer.getvalue()))
                return default_storage.url(webp_path)
            except Exception:
                return image_url

        return image_url
    except Exception:
        return '/static/images/1111.jpg'
