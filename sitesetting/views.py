from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic.edit import FormView


from orders.models import OrderDetail
from .forms import ContactForm
from .models import FastLinks, SiteSetting, QuestionAndAnswer, Newsletter

from user.forms import ActiveAccountForm as NumberForAddToLettersForm

# Create your views here.
class Main(TemplateView):
    """
    main page
    """
    template_name = 'index.html'

class QuestionsPageView(TemplateView):
    """
    Q&A page
    """
    template_name = 'site/questions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = QuestionAndAnswer.objects.all()
        return context

class AboutUs(TemplateView):
    """
     about us page
    """
    template_name = 'site/aboute-us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site'] = SiteSetting.objects.filter(is_active=True).first()
        return context

class ContactUs(SuccessMessageMixin, FormView):
    """
    contact us page
    """
    template_name = 'site/contact-us.html'
    form_class = ContactForm
    success_message = 'پیام شما با موفقبت ارسال شد'
    success_url = reverse_lazy('site:contact-us')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['site'] = SiteSetting.objects.filter(is_active=True).first()

        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'لطفا در وارد کردن اطلاعات دقت کنید')
        return super().form_invalid(form)

class AddTONewsLetters(RedirectView):
    """
    for add phone number to news letters
    """

    def get_redirect_url(self, *args, **kwargs):
        phone = self.request.POST.get('phone_number')
        Newsletter.objects.create(phone_number=phone)
        messages.success(
            self.request,
            'شماره شما با موفقیت اضافه شد'
        )
        return self.request.META.get('HTTP_REFERER', '/')

def custom_404_page(request, exception=None):
    return render(request, 'site/404.html')

def header_render_partial(request):
    if request.user.is_authenticated:
        orders = OrderDetail.objects.filter(order__user=request.user, order__is_paid=False,
                                        order__is_active=True, order__canceled=False )
    else:
        orders = None

    site = SiteSetting.objects.filter(is_active=True).first()

    return render(request, 'Base/Header/Header.html', {'orders':orders, 'site':site})

def footer_render_partial(request):
    site = SiteSetting.objects.filter(is_active=True).first()
    links = FastLinks.objects.all().order_by('-id')
    return render(request, 'Base/Footer/Footer.html',
                  {'site':site, 'links1':links[0:4], 'links2':links[4:8],
                   'form':NumberForAddToLettersForm()})