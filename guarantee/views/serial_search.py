from guarantee.models import ProductGuarantee, ActiveProductGuarantee
from django.views.generic import View
from django.shortcuts import render
from django.http import Http404
from django.contrib import messages
from guarantee.forms import GuratanteeSerialNumberSearch, ActiveGuratanteeSerialNumberSearch


class GuaranteeView(View):
    """
    for guarantee serial number search
    """

    def dispatch(self, request, *args, **kwargs):
        self.site = request.site
        if self.site.active_guarantee:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()


    def get(self, request, *args, **kwargs):


        form = GuratanteeSerialNumberSearch(request.POST or request.GET or None)


        context = {
            'items': None ,
            'form': GuratanteeSerialNumberSearch(request.POST or request.GET or None),
            'form_guarantee': ActiveGuratanteeSerialNumberSearch(request.POST or request.GET or None)
            , 'site': self.site
        }

        if form.is_valid():
            serial_number = form.cleaned_data.get('seria_number')
            matched_items = list(
                ProductGuarantee.objects.filter(serial_number=serial_number)
                .select_related("product", "company")[:2]
            )

            if len(matched_items) != 1:
                messages.error(request, 'گارانتی با این شماره سریال یافت نشد')
                return render(request, 'site/guarantee.html', context)

            items = matched_items[0]
            if not items.is_active:
                messages.error(request, 'گارانتی با این شماره سریال موجود است، اما غیر فعال است. لطفاً برای فعال‌سازی با پشتیبانی تماس بگیرید.')

                return render(request, 'site/guarantee.html', context)

            context.update({
                'items': items,
            })
            messages.success(request, "گارانتی مورد نظر با موفقیت یافت شد. در صورتی که محصولی با این گارانتی در اختیار دارید، برای فعال‌سازی آن با پشتیبانی تماس بگیرید.")

        return render(request, 'site/guarantee.html', context)




class GuaranteeActiveView(View):
    """for search the active guaratee"""
    def dispatch(self, request, *args, **kwargs):


        self.site = request.site
        if self.site.active_guarantee:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()

    def get(self, request, *args, **kwargs):
        context = {
            'items': None,
            'active_guarantee': None,
            'form':GuratanteeSerialNumberSearch(request.POST or request.GET or None),
            'form_guarantee':ActiveGuratanteeSerialNumberSearch(request.POST or request.GET or None),
            'site': self.site
        }

        form = ActiveGuratanteeSerialNumberSearch(request.POST or request.GET or None)


        if form.is_valid():
            serial_number = form.cleaned_data.get('active_seria_number')
            items = (
                ActiveProductGuarantee.objects.filter(serial_number=serial_number)
                .select_related("guarantee__company", "guarantee", "guarantee__product", "user")
                .first()
            )

            if items is None:
                messages.error(request, 'گارانتی با این شماره سریال فعال نشده است')
                return render(request, 'site/guarantee.html', context)
            if not  items.is_active  :
                messages.error(request, 'گارانتی با این شماره سریال موجود است، اما هنوز فعال نشده. لطفاً برای فعال‌سازی با پشتیبانی تماس بگیرید.')
                return render(request, 'site/guarantee.html', context)

            context.update(
                {
                    'items': items.guarantee,
                    'active_guarantee': items ,
                    'phone_number': items.phone_number if items.phone_number else items.user.PhoneNumber ,
                }
            )

        return render(request, 'site/guarantee.html', context)