# from django.shortcuts import render
# from django.views.generic import (
#     ListView,
#     DetailView,
#     View,
#     RedirectView,
#     CreateView,
#     FormView,
#     UpdateView
# )
#
# from .forms import (
# SiteSettingModelForm,
# BannersModelForm,
# SliderModelForm,
# FastLinksModelForm,
# QuestionAndAnswerModelForm,
# )
#
# from sitesetting.models import (
#     SiteSetting,
#     Banners,
#     Slider,
#     FastLinks,
#     QuestionAndAnswer,
#     ContactUs
# )
# from user.mixins.logins import AdminUserMixin
#
#
# class SliderListView(AdminUserMixin, ListView):pass
# class SliderCreateView(AdminUserMixin, CreateView):pass
# class SliderUpdateView(AdminUserMixin, UpdateView):pass
# class SliderActiveAndDeactivate(AdminUserMixin, RedirectView):pass
# class SliderDeleteView(AdminUserMixin, View):pass
