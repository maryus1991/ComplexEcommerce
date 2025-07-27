from django.views.generic import (
    DetailView,
    ListView,
    View,
    UpdateView,
)
from django.shortcuts import (
    get_object_or_404,
    reverse,
    render,
    redirect,
)
from django.urls import reverse_lazy
from django.contrib import messages
from stores.models import Store
from stores.forms import (
    AddStoreForm, RegisterStoreMinimalInformationForm
)
from user.mixins.logins import StoreAdminUserStaff, CustomLoginRequiredMixin
from utils.tipax_price_calc import validate_city


class StoreMainTemplateCreateView(CustomLoginRequiredMixin, View):
    """for store create view in main template"""
    model = Store
    template_name = 'store/store/create.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.store :
                messages.warning(request, 'شما نمی توانید اینجا وارد شوید')
                return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = RegisterStoreMinimalInformationForm(
            initial={
                'phone': str(request.user.PhoneNumber).replace(' ', '')
            }
        )
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        data = RegisterStoreMinimalInformationForm(request.POST, request.FILES)

        if data.is_valid():
            name = data.cleaned_data.get('name')
            phone = data.cleaned_data.get('phone')
            logo = data.cleaned_data.get('logo')
            about_image = data.cleaned_data.get('about_image')
            province = data.cleaned_data.get('province')
            card = data.cleaned_data.get('card')
            card_shaba = data.cleaned_data.get('card_shaba')
            card_name = data.cleaned_data.get('card_name')
            economic_number = data.cleaned_data.get('economic_number')
            registration_number = data.cleaned_data.get('registration_number')
            official_invoice_phone_number = data.cleaned_data.get('official_invoice_phone_number')

            store = Store.objects.create(
                is_active=False,
                is_verified=False,
                name=name,
                phone=phone,
                logo=logo,
                about_image=about_image,
                province=province,
                card=card,
                card_shaba=card_shaba,
                card_name=card_name,
                economic_number=economic_number,
                registration_number=registration_number,
                official_invoice_phone_number=official_invoice_phone_number,
            )

            user = request.user

            user.is_staff = True
            user.store = store
            user.is_store_admin = True
            user.legal_person = True
            user.legal_person_economic_number = economic_number
            user.legal_person_registration_number = registration_number
            user.legal_person_phone = official_invoice_phone_number
            user.save()
            messages.success(request, 'فروشگاه مورد نظر ساخته شد و به ادمین جهت برسی ارسال شد در صورت تایید با شما تماس خواهند گرفت و بعد از تایید پنل فروشگاهی شما فعال خواهد شد ')
        else:
            messages.warning(request, 'اطلاعات را به درستی وارد کنید')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return redirect('/')


class StoreMainTemplateDetailView(DetailView):
    """for store detail view in main template"""
    model = Store
    template_name = 'store/store/detail.html'
    context_object_name = 'item'

    def get_object(self, queryset=...):
        return get_object_or_404(Store, pk=self.kwargs['pk'], is_active=True, is_verified=True)


class StoreMainTemplateListView(ListView):
    """for store list view in main template"""
    model = Store
    template_name = 'store/store/list.html'
    context_object_name = 'items'
    paginate_by = 21

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_verified=True).order_by('-sort_number')


class StoreUpdateInformationView(StoreAdminUserStaff, UpdateView):
    """
    for update information
    """

    template_name = "store/add_store.html"
    form_class = AddStoreForm
    model = Store
    success_url = reverse_lazy("store:update")
    context_object_name = "item"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Store, id=self.request.user.store.id, is_active=True, is_verified=True
        )

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)

    def form_valid(self, form):

        data = form.cleaned_data

        if data.get("have_official_invoice"):
            if (
                    data.get("have_official_invoice") is None or
                    data.get("official_invoice_price") is None or
                    data.get("economic_number") is None or
                    data.get("registration_number") is None or
                    data.get("official_invoice_phone_number") is None
            ):
                raise ValidationError(
                    "برای فعال شدن صدور فاکتور رسمی باید همه فیلد های مربوط به فاکتور رسمی پر شود"
                )

        if self.request.user.store.orgin_city != data.get("orgin_city"):

            try:
                validate_city_result = validate_city(data.get("orgin_city"))

                if validate_city_result is None:
                    messages.error(self.request, "مشکلی پیش امد")
                    return redirect(self.request.META.get("HTTP_REFERER", "/"))

                if len(validate_city_result) > 1:
                    messages.warning(
                        self.request,
                        f""" 
                        شهر شما یافت نشد لطفا در نوشتن ان دقت فرمایید
                        لیست شهر های پیدا شده با این اسم ارسالی شما 
                            {" , ".join([x['title'] for x in list(validate_city_result)])}""",  # noqa
                    )  # noqa
                    return redirect(self.request.META.get("HTTP_REFERER", "/"))

                if len(validate_city_result) == 1:
                    form.instance.orgin_city_id = validate_city_result[0]["id"]

            except Exception as e:
                messages.error(
                    self.request,
                    'مشکلی در ارتباط با سرور پیش امده است لطفا بعدا امتحان کنید'
                )
                return redirect(self.request.META.get("HTTP_REFERER", "/"))

        messages.success(self.request, "اطلاعات شما با موقیت ثبت شد")

        return super().form_valid(form)
