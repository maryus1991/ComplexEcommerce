from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect

class CustomLoginRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_verified and request.user.is_active:
                return super().dispatch(request, *args, **kwargs)

            if  request.user.is_active and not request.user.is_verified:
                messages.info(request, 'لطفا حساب خود را تایید کنید یک کد به شما ارسال شد لطفا انرا وارد کنید تا حساب شما تایید شود')
                return redirect('user:otp')

        messages.warning(request, "لطفا وارد سایت شوید")
        return redirect('user:login')


class UserStoreStaffMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_active and request.user.is_staff and request.user.is_verified:
                if request.user.store is not None:
                    return super().dispatch(request, *args, **kwargs)

        messages.error(request, "شما دسترسی ورود با این صفحه را ندارید")
        return redirect(request.META.get('HTTP_REFERER', '/'))

class StoreAdminUserStaff(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_active and request.user.is_staff and request.user.is_verified:
                if request.user.store is not None:
                    if request.user.is_store_admin:
                        return super().dispatch(request, *args, **kwargs)

        messages.error(request, "شما دسترسی ورود با این صفحه را ندارید")
        return redirect(request.META.get('HTTP_REFERER', '/'))

class AdminUserMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_active and request.user.is_superuser and request.user.is_verified :
                return super().dispatch(request, *args, **kwargs)

        messages.error(request, "شما دسترسی ورود با این صفحه را ندارید")
        return redirect(request.META.get('HTTP_REFERER', '/'))