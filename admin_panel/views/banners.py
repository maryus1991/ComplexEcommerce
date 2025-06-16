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
#
# class BannersListView(AdminUserMixin, ListView):pass
# class BannersCreateView(AdminUserMixin, CreateView):pass
# class BannersUpdateView(AdminUserMixin, UpdateView):pass
# class BannersActiveAndDeactivate(AdminUserMixin, RedirectView):pass
# class BannersDeleteView(AdminUserMixin, View):pass
#
