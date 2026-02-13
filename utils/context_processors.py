import time
from django.contrib.auth.context_processors import PermWrapper
from user.models import User

def ckeditor_config(request):
    return {"ckeditor_config": "mobile" if request.user_agent.is_mobile else "default"}


def timestamp(request):
    return {"ts": int(time.time())}


def auth(request):
    """
    Return context variables required by apps that use Django's authentication
    system.

    If there is no 'user' attribute in the request, use AnonymousUser (from
    django.contrib.auth).
    """
    if hasattr(request, "user"):
        user = request.user.select_related('colleague_with_store', 'store')
    else:
        from django.contrib.auth.models import AnonymousUser

        user = AnonymousUser()


    return {
        "user": user,
        "perms": PermWrapper(user),
    }
