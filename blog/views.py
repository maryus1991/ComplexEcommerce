from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from .models import Blog, BlogView, BlogCategory, BlogTag
from ipware import get_client_ip

class ListArticlesView(ListView):
    """
    for listing articles
    """
    template_name = 'blog/articles.html'
    model = Blog
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        """
        Returns active records annotated with their blog view counts
        """
        item = super().get_queryset(
        ).filter(is_active=True
        ).annotate(view_count=Count('views')).order_by('view_count').all()
        print(item)
        return item


class DetailArticleView(DetailView):
    """
    for detail article
    """
    template_name = 'blog/article-details.html'
    model = Blog
    context_object_name = 'post'

    def get_object(self):
        pk = self.kwargs['pk']
        obj = self.get_queryset().filter(
            pk=pk, is_active=True
        ).prefetch_related('tags'
        ).first()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            ip, is_rout = get_client_ip(self.request)
            view = BlogView.objects.get_or_create(ip=ip, blog_id=pk)

            if not view[1]:
                view[0].count += 1
                view[0].save()

        except Exception as e:
            pass


        last_posts = Blog.objects.filter(is_active=True).all().order_by('-id')[:4]
        categories = BlogCategory.objects.filter(is_active=True
        ).annotate(post_count=Count('blogs')
        ).all().order_by('-post_count')[:4]

        context['last_posts'] = last_posts
        context['categories'] = categories
        return context
