from django.urls import path
from .views import (
    ListArticlesView,
    DetailArticleView
)

app_name = 'blog'

urlpatterns = [
    path('', ListArticlesView.as_view(), name='list'),
    path('<int:pk>/', DetailArticleView.as_view(), name='detail'),
]