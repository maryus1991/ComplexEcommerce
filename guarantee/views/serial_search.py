from guarantee.models import ProductGuarantee, ActiveProductGuarantee
from django.views.generic import View
from django.shortcuts import render
from django.http import Http404
from sitesetting.models import SiteSetting
from django.contrib import messages
from guarantee.forms import GuratanteeSerialNumberSearch, ActiveGuratanteeSerialNumberSearch


class GuaranteeView(View):
    """
    for guarantee serial number search
    """ 

    def dispatch(self, request, *args, **kwargs):
        self.site = SiteSetting.objects.first()
        if self.site.active_guarantee:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()
    

    def get(self, request, *args, **kwargs):
        context = {
            'form':GuratanteeSerialNumberSearch(request.POST or request.GET or None),
            'form_guarantee':ActiveGuratanteeSerialNumberSearch(request.POST or request.GET or None),
            'site': self.site
        }
        return render(request, 'site/guarantee.html', context)

    def post(self, request, *args, **kwargs):
        form = GuratanteeSerialNumberSearch(request.POST or request.GET or None)
        items = None

        if form.is_valid():
            serial_number = form.cleaned_data.get('seria_number')
            items = ProductGuarantee.objects.filter(serial_number=serial_number)

            if not items.exists():
                messages.error(request, 'گارانتی با این شماره سریال یافت نشد')



        else:
            messages.error(request, form.errors.as_text)

            
        context = {
            'items': items.first() ,
            'form':GuratanteeSerialNumberSearch(request.POST or request.GET or None),
            'form_guarantee':ActiveGuratanteeSerialNumberSearch(request.POST or request.GET or None)
            ,'site': self.site
        }
        return render(request, 'site/guarantee.html', context)
    

class GuaranteeActiveView(View):
    """for search the active guaratee"""
    def dispatch(self, request, *args, **kwargs):
        self.site = SiteSetting.objects.first()
        if self.site.active_guarantee:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()
        
    def post(self, request, *args, **kwargs):
        form = ActiveGuratanteeSerialNumberSearch(request.POST or request.GET or None)
        items = None

        if form.is_valid():
            serial_number = form.cleaned_data.get('active_seria_number')
            items = ActiveProductGuarantee.objects.filter(serial_number=serial_number)

            if not items.exists() or not items.first().is_active :
                messages.error(request, 'گارانتی با این شماره سریال یافت نشد')
                return render(request, 'site/guarantee.html')



        else:
            messages.error(request, form.errors.as_text)
            return render(request, 'site/guarantee.html')


            
        context = {
            'items': items.first().guarantee,
            'active_guarantee': items.first(),
            'form':GuratanteeSerialNumberSearch(request.POST or request.GET or None),
            'form_guarantee':ActiveGuratanteeSerialNumberSearch(request.POST or request.GET or None),
            'site': self.site
        }
        return render(request, 'site/guarantee.html', context)