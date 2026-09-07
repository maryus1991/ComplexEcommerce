from django.views.generic import RedirectView, ListView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy

from sitesetting.models import Slider
from admin_panel.forms import SliderModelForm

from user.mixins.logins import AdminUserMixin


class SliderListView(AdminUserMixin, ListView):
    model = Slider
    context_object_name = "sliders"
    paginate_by = 10
    template_name = "admin_panel/sliders/list.html"




class SliderCreateView(AdminUserMixin, CreateView):
    """
    for creating a slider
    """

    model = Slider
    form_class = SliderModelForm
    template_name = "admin_panel/sliders/form.html"
    success_url = reverse_lazy("admin_panel:sliders-list")



    def form_valid(self, form):
        messages.success(self.request, "اسلایدر شما با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


class SliderUpdateView(AdminUserMixin, UpdateView):
    """
    for updating a slider
    """

    model = Slider
    form_class = SliderModelForm
    template_name = "admin_panel/sliders/form.html"
    success_url = reverse_lazy("admin_panel:sliders-list")
    context_object_name = "slider"

    def form_valid(self, form):
        messages.success(self.request, "اسلایدر شما با موفقت ساخته شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,form.errors.as_text())
        return super().form_invalid(form)


class SliderActiveAndDeactivateView(AdminUserMixin, RedirectView):
    """
    for active or deactivate slider
    """

    def get_redirect_url(self, *args, **kwargs):
        slider_id = kwargs.get("pk")
        slider_object = get_object_or_404(Slider, pk=slider_id)
        if slider_object.is_active:
            slider_object.is_active = False
            slider_object.save()
            messages.success(self.request, "اسلایدر مورد نظر غیر فعال شد")
        else:
            slider_object.is_active = True
            slider_object.save()
            messages.success(self.request, "اسلایدر مورد نظر فعال شد")

        return reverse_lazy("admin_panel:sliders-list")


class SliderDeleteView(AdminUserMixin, RedirectView):
    """
    for delete slider
    """

    def get_redirect_url(self, *args, **kwargs):
        slider_id = kwargs.get("pk")
        slider_object = get_object_or_404(Slider, pk=slider_id)
        slider_object.delete()
        messages.info(self.request, "اسلایدر مورد نظر حذف شد")

        return reverse_lazy("admin_panel:sliders-list")
