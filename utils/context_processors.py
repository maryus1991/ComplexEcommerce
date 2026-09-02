import time
from sitesetting.models import SiteSetting

def ckeditor_config(request):
    return {"ckeditor_config": "mobile" if request.user_agent.is_mobile else "default"}


def timestamp(request):
    return {"ts": int(time.time())}

def get_sitesetting(request):
    return {"site": request.site}

