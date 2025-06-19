from django.views.generic import RedirectView, CreateView, UpdateView, ListView, View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.urls import reverse_lazy
from user.mixins.logins import AdminUserMixin


class UserCreateView(AdminUserMixin, CreateView): pass


class UserListView(AdminUserMixin, ListView): pass


class UserUpdateView(AdminUserMixin, UpdateView): pass


class UserActiveDeactivateView(AdminUserMixin, RedirectView): pass


class UserVerifyView(AdminUserMixin, RedirectView): pass


class UserDeleteView(AdminUserMixin, View): pass
