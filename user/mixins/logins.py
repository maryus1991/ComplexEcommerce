from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import Http404
from sitesetting.models import SiteSetting
from django.contrib.auth import logout


class CustomLoginRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        Site = SiteSetting.objects.first()

        if not Site.is_active:

            if  request.user.is_authenticated:
                logout(request)

            messages.warning(request, "ورود به سایت غیر فعال می باشد")
            return redirect('user:login')

        if request.user.is_authenticated and Site.is_active:
            if not Site.legal_users_login and request.user.legal_person:
                logout(request)
                messages.warning(request, "ورود افراد با حساب رسمی غیر فعال است")
                return redirect('user:login')

            if not Site.store_users_staff_logins and request.user.is_staff and request.user.store is not None:
                logout(request)
                messages.warning(request, "ورود کارمندان فروشگاها غیر فعال است")
                return redirect('user:login')

            if request.user.is_verified and request.user.is_active:
                return super().dispatch(request, *args, **kwargs)

            if  request.user.is_active and not request.user.is_verified:
                messages.info(request, 'لطفا حساب خود را تایید کنید یک کد به شما ارسال شد لطفا انرا وارد کنید تا حساب شما تایید شود')
                return redirect('user:otp')

        messages.warning(request, "لطفا وارد سایت شوید")
        return redirect('user:login')


class UserStoreStaffMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):

        Site = SiteSetting.objects.first()

        if not Site.is_active:
            if request.user.is_authenticated:
                logout(request)
            messages.warning(request, "ورود به سایت غیر فعال می باشد")
            return redirect('user:login')

        if not Site.active_store_page :
            messages.warning(request, "ورود به صفحه فروشگاه غیر فعال می باشد")
            return redirect('user:login')


        if request.user.is_authenticated:
            if request.user.is_active and request.user.is_staff and request.user.is_verified:
                if request.user.store is not None:
                    if not Site.store_users_staff_logins :
                        logout(request)
                        messages.warning(request, "ورود کارمندان فروشگاه غیر فعال شده است")
                        return redirect('user:login')
                    return super().dispatch(request, *args, **kwargs)

        raise Http404()

class StoreAdminUserStaff(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        Site = SiteSetting.objects.first()

        if not Site.is_active:
            if request.user.is_authenticated:
                logout(request)
            messages.warning(request, "ورود به سایت غیر فعال می باشد")
            return redirect('user:login')

        if not Site.active_store_page :
            messages.warning(request, "ورود به صفحه فروشگاه غیر فعال می باشد")
            return redirect('user:login')


        if request.user.is_authenticated:
            if request.user.is_active and request.user.is_staff and request.user.is_verified:
                if request.user.store is not None:

                    if request.user.is_store_admin:
                        return super().dispatch(request, *args, **kwargs)

        raise Http404()

class AdminUserMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_active and request.user.is_superuser and request.user.is_verified :
                return super().dispatch(request, *args, **kwargs)

        raise Http404()