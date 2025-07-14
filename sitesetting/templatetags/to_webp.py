from django import template
from PIL import Image
import os
from django.conf import settings

register = template.Library()


@register.filter
def to_webp(image_url):
    try:
        if not image_url:
            print('12')
            return '/static/images/1111.jpg'
        if image_url.startswith(settings.MEDIA_URL):
            image_path = image_url[len(settings.MEDIA_URL):]
        else:
            image_path = image_url

        full_path = os.path.join(settings.MEDIA_ROOT, image_path)
        webp_path = full_path.rsplit('.', 1)[0] + '.webp'

        if not os.path.exists(webp_path):
            try:
                img = Image.open(full_path)
                img.save(webp_path, 'WEBP', quality=85)
            except Exception as e:
                return image_url

        webp_url = settings.MEDIA_URL + image_path.rsplit('.', 1)[0] + '.webp'
        return webp_url
    except Exception as e:

        return '/static/images/1111.jpg'