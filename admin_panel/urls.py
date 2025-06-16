from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='main'),

    # site setting
    path('update-site-setting/', views.UpdateSiteSettingView.as_view(), name='update-site-setting'),

    # banners

    # sliders

]