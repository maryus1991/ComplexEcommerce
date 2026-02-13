from django.views.generic import (
    RedirectView,
    CreateView,
    UpdateView,
    ListView,
    View,
    DetailView,
)
from django.shortcuts import get_object_or_404, redirect, reverse, render, Http404
from django.urls import reverse_lazy
from user.mixins.logins import AdminUserMixin
from stores.models import Store
from django.contrib import messages
from stores.forms import AddStoreForm
from admin_panel.forms import StorePermissions
from utils.find_city import search_city
from django.core.exceptions import ValidationError


class StorePermissionsUpdateView(AdminUserMixin, UpdateView):
    """
    for update a store permissions page
    """

    model = Store
    form_class = StorePermissions
    template_name = "admin_panel/store/permissions.html"
    success_url = reverse_lazy("admin_panel:store-list")
    context_object_name = "item"

    def form_valid(self, form):
        messages.success(self.request, 'تغییرات ثبت شد')
        form.save()
        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class StoreChangeSortNumber(AdminUserMixin, RedirectView):
    """for change sort number product categories"""

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        store = get_object_or_404(Store, pk=pk)
        sort_number = self.request.POST[f'{pk}']

        try:
            sort_number = int(sort_number)
            if 1000 >= sort_number  >= 0:
                store.sort_number = sort_number
                store.save()
                messages.success(
                    self.request,
                    'ثبت شد'
                )
                print(sort_number, type(sort_number))
                return reverse("admin_panel:store-list")

            else:
                messages.error(
                    self.request,
                    'عدد وارد شده باید بین 0 الی 1000 باشد'
                )
        except Exception as e:
            messages.error(
                self.request,
                'در وارد کردن عدد دقت فرمایید'
            )

        return reverse("admin_panel:store-list")


class StoreListView(AdminUserMixin, ListView):
    """
    for listing the stores
    """

    model = Store
    context_object_name = "items"
    template_name = "admin_panel/store/list.html"


class StoreColleaguesListView(AdminUserMixin, ListView):
    """
    for listing colleague_with_store
    """

    context_object_name = "items"
    template_name = "admin_panel/users/list.html"

    def get_queryset(self):
        return Store.objects.filter(pk=self.kwargs.get('pk')).first().colleague_users.all()

class StoreCreateView(AdminUserMixin, CreateView):
    """
    for creating a new store
    """

    form_class = AddStoreForm
    template_name = "admin_panel/store/create.html"
    success_url = reverse_lazy("admin_panel:store-list")

    def form_valid(self, form):
        data = form.cleaned_data

        if (
            data.get("have_in_same_city_delivery") and
                data.get("in_same_city_delivery_price") is None
        ):
            messages.error(
                self.request, "برای فعال کردن پست درون شهری باید هزینه ان وارد شود"
            )
            return redirect(self.request.META.get("HTTP_REFERER"))

        if data.get("have_official_invoice"):
            if (
                data.get("have_official_invoice") is None or
                    data.get("official_invoice_price") is None or
                    data.get("economic_number") is None or
                    data.get("registration_number") is None or
                    data.get("official_invoice_phone_number") is None
            ):
                messages.error(
                    self.request,
                    "برای فعال شدن صدور فاکتور رسمی باید همه فیلد های مربوط به فاکتور رسمی پر شود",
                )
                return redirect(self.request.META.get("HTTP_REFERER"))

        if True:
            try:

                city = form.cleaned_data["orgin_city"]
                province = form.cleaned_data.get('province')

                if province is None or city is None:
                    messages.error(
                        self.request,
                        'نام استان و شهر رو وارد کنید'
                    )
                    return redirect(self.request.META.get("HTTP_REFERER", '/'))

                validate_city_result = search_city(province, city)

                if validate_city_result[0] == 0:
                    messages.error(
                        self.request,
                        validate_city_result[1]
                    )
                    return render(self.request, self.template_name, {"form": form})

                elif validate_city_result[0] == 1:
                    obj = validate_city_result[1]
                    form.instance.orgin_city_id = obj['tipax_id']
                    form.instance.orgin_city_id_post = obj['post_id']


                    if obj['tipax_id'] is None:
                        messages.warning(
                            self.request,
                            "این ادرس برای ارسال با تیپاکس مناسب نیست"
                        )

                    if obj['post_id'] is None:
                        messages.warning(
                            self.request,
                            "این ادرس برای ارسال با پست مناسب نیست"
                        )

            except Exception as e:
                messages.error(
                    self.request,
                    'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
                )
                return redirect(self.request.META.get("HTTP_REFERER", '/'))

        messages.success(self.request, "  فروشگاه ساخته شد")
        form.instance.is_verified = False

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class StoreUpdateView(AdminUserMixin, UpdateView):
    """
    for update a store
    """

    model = Store
    form_class = AddStoreForm
    template_name = "admin_panel/store/create.html"
    success_url = reverse_lazy("admin_panel:store-list")
    context_object_name = "item"

    def form_valid(self, form):
        data = form.cleaned_data

        if (
            data.get("have_in_same_city_delivery") and
                data.get("in_same_city_delivery_price") is None
        ):
            messages.error(
                self.request, "برای فعال کردن پست درون شهری باید هزینه ان وارد شود"
            )
            return redirect(self.request.META.get("HTTP_REFERER"))

        if data.get("have_official_invoice"):
            if (
                data.get("have_official_invoice") is None or
                    data.get("official_invoice_price") is None or
                    data.get("economic_number") is None or
                    data.get("registration_number") is None or
                    data.get("official_invoice_phone_number") is None
            ):
                messages.error(
                    self.request,
                    "برای فعال شدن صدور فاکتور رسمی باید همه فیلد های مربوط به فاکتور رسمی پر شود",
                )
                return redirect(self.request.META.get("HTTP_REFERER"))

        if self.get_object().orgin_city != data.get("orgin_city") or self.get_object().province != data.get("province"):
            try:

                city = form.cleaned_data["orgin_city"]
                province = form.cleaned_data.get('province')
                validate_city_result = search_city(province, city)

                if validate_city_result[0] == 0:
                    messages.error(
                        self.request,
                        validate_city_result[1]
                    )
                    return render(self.request, self.template_name, {"form": form})

                elif validate_city_result[0] == 1:
                    obj = validate_city_result[1]
                    form.instance.orgin_city_id = obj['tipax_id']
                    form.instance.orgin_city_id_post = obj['post_id']



                    if obj['tipax_id'] is None:
                        messages.warning(
                            self.request,
                            "این ادرس برای ارسال با تیپاکس مناسب نیست"
                        )

                    if obj['post_id'] is None:
                        messages.warning(
                            self.request,
                            "این ادرس برای ارسال با پست مناسب نیست"
                        )

            except Exception as e:
                messages.error(
                    self.request,
                    'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
                )
                return redirect(self.request.META.get("HTTP_REFERER", "/"))

        messages.success(self.request, "اطلاعات شما با موقیت ثبت شد")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class StoreDetailView(AdminUserMixin, DetailView):
    """
    for store detail view
    """

    model = Store
    context_object_name = "item"
    template_name = "admin_panel/store/details.html"

    def get_object(self, queryset=None):
        user = self.model.objects.filter(pk=self.kwargs["pk"]).prefetch_related(
            "blogs", "products", "users", "orders"
        )

        if user.count() != 1:
            raise Http404()

        return user.first()


class StoreVerifyView(AdminUserMixin, RedirectView):
    """
    for verify store
    """

    def get_redirect_url(self, *args, **kwargs):
        store = get_object_or_404(Store, pk=self.kwargs["pk"])
        if store.is_verified:
            store.is_verified = False
            store.save()
            messages.warning(self.request, "وضعیت اطلاعات فروشگاه تایید نشد")
        else:
            store.is_verified = True
            store.save()
            messages.success(self.request, "وضعیت اطلاعات فروشگاه تایید شد")

        return reverse("admin_panel:store-list")


class StoreActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """for active and deactivate store view"""

    def get_redirect_url(self, *args, **kwargs):
        store = get_object_or_404(Store, pk=self.kwargs["pk"])
        if store.is_active:
            store.is_active = False
            store.save()
            messages.warning(self.request, "وضعیت اطلاعات فروشگاه غیر فعال شد")
        else:
            store.is_active = True
            store.save()
            messages.success(self.request, "وضعیت اطلاعات فروشگاه فعال شد")

        return reverse("admin_panel:store-list")


class StoreDeleteView(AdminUserMixin, View):
    """for delete store"""

    def get(self, request, *args, **kwargs):
        messages.error(
            request, "با حذف این فرشگاه تمام محصولات و پست و کاربران ان حذف خواهند شد "
        )
        messages.warning(
            request,
            "بهتر است که به جای حذف فروشگاه ان را غیر فعال کنید و از حذف این همه اطلاعات جلوگیری کنید",
        )
        obj = get_object_or_404(Store, pk=self.kwargs["pk"])
        obj = (
            Store.objects.filter(id=obj.id)
            .prefetch_related("products")
            .prefetch_related("users")
            .first()
        )
        return render(request, "admin_panel/store/delete.html", {"item": obj})

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(Store, pk=self.kwargs["pk"])
        obj = (
            Store.objects.filter(id=obj.id)
            .prefetch_related("products")
            .prefetch_related("users")
            .prefetch_related("blogs")
            .first()
        )

        if obj.name == request.POST.get("conform"):
            obj.delete()
            messages.warning(request, "فروشگاه مورد نظر حذف شد")
        else:
            messages.warning(request, "در وارد کردن نام فروشگاه دقت کنید")

        return redirect("admin_panel:store-list")
