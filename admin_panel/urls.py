from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='main'),

    # site setting
    path('update-site-setting/', views.UpdateSiteSettingView.as_view(), name='update-site-setting'),

    # banners
    path('banners/', views.BannersListView.as_view(), name='banners-list'),
    path('banners/create/', views.BannersCreateView.as_view(), name='banners-create'),
    path('banners/update/<int:pk>', views.BannersUpdateView.as_view(), name='banners-update'),
    path('banners/active-deactivate/<int:pk>', views.BannersActiveAndDeactivateView.as_view(), name='banners-active-deactivate'),
    path('banners/delete/<int:pk>', views.BannersDeleteView.as_view(), name='banners-delete'),


    # sliders
    path('sliders/', views.SliderListView.as_view(), name='sliders-list'),
    path('sliders/create/', views.SliderCreateView.as_view(), name='sliders-create'),
    path('sliders/update/<int:pk>', views.SliderUpdateView.as_view(), name='sliders-update'),
    path('sliders/active-deactivate/<int:pk>', views.SliderActiveAndDeactivateView.as_view(), name='sliders-active-deactivate'),
    path('sliders/delete/<int:pk>', views.SliderDeleteView.as_view(), name='sliders-delete'),
]