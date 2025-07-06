from django.urls import path
from . import views

app_name = "stores"

urlpatterns = [
    path('', views.StoreMainTemplateListView.as_view(), name='main-template-list'),
    path('<int:pk>/', views.StoreMainTemplateDetailView.as_view(), name='main-template-detail'),
    path('create/', views.StoreMainTemplateCreateView.as_view(), name='main-template-create'),
]