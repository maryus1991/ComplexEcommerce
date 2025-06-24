from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, RedirectView, CreateView
from django.shortcuts import get_object_or_404
from user.mixins.logins import AdminUserMixin
from admin_panel.forms import FastLinksModelForm, QuestionAndAnswerModelForm
from sitesetting.models import FastLinks, QuestionAndAnswer
from django.contrib import messages

class HomePageView(AdminUserMixin, TemplateView):
    template_name = 'admin_panel/index2.html'


class FastLinksListView(AdminUserMixin, ListView):
    """for listing FastLinks items for admin"""

    model = FastLinks
    paginate_by = 25
    context_object_name = 'items'
    template_name = 'admin_panel/fastlinks/list.html'


class FastLinksCreateView(AdminUserMixin, CreateView):
    """for create obj in FastLinks model """
    form_class = FastLinksModelForm
    model = FastLinks
    template_name = 'admin_panel/fastlinks/create.html'
    context_object_name = 'items'
    success_url = reverse_lazy('admin_panel:fast-links-list')

    def form_valid(self, form):
        messages.success(self.request, 'ایتم  مورد نظر با موفقت ساخته شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class FastLinksUpdateView(AdminUserMixin, UpdateView):
    """for update items in FastLinks"""
    form_class = FastLinksModelForm
    model = FastLinks
    template_name = 'admin_panel/fastlinks/create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('admin_panel:fast-links-list')

    def form_valid(self, form):
        messages.success(self.request, 'ایتم  مورد نظر با موفقت ساخته شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class FastLinksActiveAndDeactivate(AdminUserMixin, RedirectView):
    """for active and deactivate items in FastLinks model"""

    def get_redirect_url(self, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = get_object_or_404(FastLinks, pk=item_id)
        if item.is_active:
            item.is_active = False
            item.save()
            messages.success(self.request, 'ایتم مورد نظر با موفقیت غیر فعال شد')
        else:
            item.is_active = True
            item.save()
            messages.success(self.request, 'ایتم مورد نظر با موفقیت فعال شد')

        return reverse_lazy('admin_panel:fast-links-list')


class FastLinksDelete(AdminUserMixin, RedirectView):
    """for delete item in FastLinks model"""

    def get_redirect_url(self, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = get_object_or_404(FastLinks, pk=item_id)
        item.delete()
        messages.info(self.request, 'ایتم مورد نظر حذف شد')

        return reverse_lazy('admin_panel:fast-links-list')


class QuestionAndAnswerListView(AdminUserMixin, ListView):
    """for listing QuestionAndAnswer  items for admin"""

    model = QuestionAndAnswer
    paginate_by = 25
    context_object_name = 'items'
    template_name = 'admin_panel/Q&A/list.html'


class QuestionAndAnswerCreateView(AdminUserMixin, CreateView):
    """for create obj in QuestionAndAnswer  model """
    form_class = QuestionAndAnswerModelForm
    model = QuestionAndAnswer
    template_name = 'admin_panel/Q&A/create.html'
    context_object_name = 'items'
    success_url = reverse_lazy('admin_panel:Q&A-list')

    def form_valid(self, form):
        messages.success(self.request, 'ایتم  مورد نظر با موفقت ساخته شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class QuestionAndAnswerUpdateView(AdminUserMixin, UpdateView):
    """for update items in QuestionAndAnswer """
    form_class = QuestionAndAnswerModelForm
    model = QuestionAndAnswer
    template_name = 'admin_panel/Q&A/create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('admin_panel:Q&A-list')

    def form_valid(self, form):
        messages.success(self.request, 'ایتم  مورد نظر با موفقت ساخته شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class QuestionAndAnswerActiveAndDeactivate(AdminUserMixin, RedirectView):
    """for active and deactivate items in QuestionAndAnswer  model"""

    def get_redirect_url(self, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = get_object_or_404(QuestionAndAnswer, pk=item_id)
        if item.is_active:
            item.is_active = False
            item.save()
            messages.success(self.request, 'ایتم مورد نظر با موفقیت غیر فعال شد')
        else:
            item.is_active = True
            item.save()
            messages.success(self.request, 'ایتم مورد نظر با موفقیت فعال شد')

        return reverse_lazy('admin_panel:Q&A-list')


class QuestionAndAnswerDelete(AdminUserMixin, RedirectView):
    """for delete item in QuestionAndAnswer  model"""

    def get_redirect_url(self, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = get_object_or_404(QuestionAndAnswer, pk=item_id)
        item.delete()
        messages.info(self.request, 'ایتم مورد نظر حذف شد')

        return reverse_lazy('admin_panel:Q&A-list')
