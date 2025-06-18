from django.views.generic import ListView, RedirectView, UpdateView, View
from user.mixins.logins import AdminUserMixin
from django.shortcuts import get_object_or_404, redirect, reverse
from blog.models import Blog, BlogCategory
from admin_panel.forms import AddBlogCategoryModelForm, AddBlogModelForm


class BlogListView(AdminUserMixin, ListView):
    """
    for listing the posts
    """
    model = Blog
    template_name = 'admin_panel/blog/list.html'
    paginate_by = 25
    context_object_name = 'items'

class BlogCategoryListView(AdminUserMixin, ListView):
    """for listing the blog categories"""
    model = BlogCategory
    template_name = 'admin_panel/blog/categories/list.html'
    paginate_by = 25
    context_object_name = 'items'

