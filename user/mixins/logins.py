from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.shortcuts import Http404
from sitesetting.models import SiteSetting
from django.contrib.auth import logout


class CustomLoginRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        Site = SiteSetting.get_cached()

        if Site and not Site.is_active:

            if request.user.is_authenticated:
                logout(request)

            messages.warning(request, "ورود به سایت غیر فعال می باشد")
            return redirect("user:login")

        if request.user.is_authenticated and Site and Site.is_active:
            if Site and not Site.legal_users_login and request.user.legal_person:
                logout(request)
                messages.warning(request, "ورود افراد با حساب رسمی غیر فعال است")
                return redirect("user:login")

            if ( Site and
                    not Site.store_users_staff_logins and
                    request.user.is_staff and
                    request.user.store is not None
            ):
                logout(request)
                messages.warning(request, "ورود کارمندان فروشگاها غیر فعال است")
                return redirect("user:login")

            if request.user.is_verified and request.user.is_active:
                return super().dispatch(request, *args, **kwargs)

            if request.user.is_active and not request.user.is_verified:
                messages.info(
                    request,
                    "لطفا حساب خود را تایید کنید یک کد به شما ارسال شد لطفا انرا وارد کنید تا حساب شما تایید شود",
                )
                return redirect("user:otp")

        if Site is None:
            return super().dispatch(request, *args, **kwargs)

        messages.warning(request, "لطفا وارد سایت شوید")
        return redirect("user:login")


class UserStoreStaffMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):

        Site = SiteSetting.get_cached()

        if Site and not Site.is_active:
            if request.user.is_authenticated:
                logout(request)
            messages.warning(request, "ورود به سایت غیر فعال می باشد")
            return redirect("user:login")

        if Site and not Site.active_store_page:
            messages.warning(request, "ورود به صفحه فروشگاه غیر فعال می باشد")
            return redirect("user:login")

        if request.user.is_authenticated:
            if (
                    request.user.is_active and
                    request.user.is_staff and
                    request.user.is_verified
            ):
                if request.user.store is not None:
                    if Site and not Site.store_users_staff_logins:
                        logout(request)
                        messages.warning(
                            request, "ورود کارمندان فروشگاه غیر فعال شده است"
                        )
                        return redirect("user:login")
                    if request.user.store.is_active:
                        path = request.path
                        store = request.user.store

                        if reverse('store:add-product') == path:
                            if not store.can_stores_add_product:
                                messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                return redirect('store:home')
                        if reverse('store:add-brands') == path:
                            if not store.can_stores_add_product_brand:
                                messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                return redirect('store:home')
                        if reverse('store:add-category') == path:
                            if not store.can_stores_add_product_category:
                                messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                return redirect('store:home')
                        if reverse('store:blog-add') == path:
                            if not store.can_store_add_blog_post:
                                messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                return redirect('store:home')
                        if reverse('store:blog-add-category') == path:
                            if not store.can_store_add_blog_category:
                                messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                return redirect('store:home')
                        if reverse('store:user-add') == path :
                            if not store.can_store_add_users:
                                messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                return redirect('store:home')
                        if reverse('store:app-create') == path or reverse('store:app-upload-app') == path :
                            if not store.can_store_add_apps:
                                messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                return redirect('store:home')
                        return super().dispatch(request, *args, **kwargs)
                    else:
                        messages.warning(
                            request, 'فروشگاه شما توسط ادمین سایت فعال نمی باشد'
                        )
                        return redirect('/')

        raise Http404()


class StoreAdminUserStaff(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        Site = SiteSetting.get_cached()

        if Site and not Site.is_active:
            if request.user.is_authenticated:
                logout(request)
            messages.warning(request, "ورود به سایت غیر فعال می باشد")
            return redirect("user:login")

        if Site and not Site.active_store_page:
            messages.warning(request, "ورود به صفحه فروشگاه غیر فعال می باشد")
            return redirect("user:login")

        if request.user.is_authenticated:
            if (
                    request.user.is_active and
                    request.user.is_staff and
                    request.user.is_verified
            ):
                if request.user.store is not None:

                    if request.user.is_store_admin:
                        if request.user.store.is_active:
                            path = request.path
                            store = request.user.store

                            if reverse('store:add-product') == path:
                                if not store.can_stores_add_product:
                                    messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                    return redirect('store:home')
                            if reverse('store:add-brands') == path:
                                if not store.can_stores_add_product_brand:
                                    messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                    return redirect('store:home')
                            if reverse('store:add-category') == path:
                                if not store.can_stores_add_product_category:
                                    messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                    return redirect('store:home')
                            if reverse('store:blog-add') == path:
                                if not store.can_store_add_blog_post:
                                    messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                    return redirect('store:home')
                            if reverse('store:blog-add-category') == path:
                                if not store.can_store_add_blog_category:
                                    messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                    return redirect('store:home')
                            if reverse('store:user-add') == path:
                                if not store.can_store_add_users:
                                    messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                    return redirect('store:home')
                            if reverse('store:app-create') == path or reverse('store:app-upload-app') == path:
                                if not store.can_store_add_apps:
                                    messages.error(request, 'شما اجازه ورود به این صفحه را ندارید')
                                    return redirect('store:home')
                            return super().dispatch(request, *args, **kwargs)
                        else:
                            messages.warning(
                                request, 'فروشگاه شما توسط ادمین سایت تایید و فعال نمی باشد'
                            )
                            return redirect('/')

        raise Http404()


class AdminUserMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if (
                    request.user.is_active and
                    request.user.is_superuser and
                    request.user.is_verified
            ):
                return super().dispatch(request, *args, **kwargs)

        raise Http404()
