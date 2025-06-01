from django.shortcuts import render
from django.views.generic.base import TemplateView


class ListArticlesView(TemplateView):
    """
    for listing articles
    """
    template_name = 'blog/articles.html'

class DetailArticleView(TemplateView):
    """
    for detail article
    """
    template_name = 'blog/article-details.html'