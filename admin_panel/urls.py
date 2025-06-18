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

    # fast-links
    path('fast-links/', views.FastLinksListView.as_view(), name='fast-links-list'),
    path('fast-links/create/', views.FastLinksCreateView.as_view(), name='fast-links-create'),
    path('fast-links/update/<int:pk>', views.FastLinksUpdateView.as_view(), name='fast-links-update'),
    path('fast-links/active-deactivate/<int:pk>', views.FastLinksActiveAndDeactivate.as_view(), name='fast-links-active-deactivate'),
    path('fast-links/delete/<int:pk>', views.FastLinksDelete.as_view(), name='fast-links-delete'),

    # Q&A
    path('Q&A/', views.QuestionAndAnswerListView.as_view(), name='Q&A-list'),
    path('Q&A/create/', views.QuestionAndAnswerCreateView.as_view(), name='Q&A-create'),
    path('Q&A/update/<int:pk>', views.QuestionAndAnswerUpdateView.as_view(), name='Q&A-update'),
    path('Q&A/active-deactivate/<int:pk>', views.QuestionAndAnswerActiveAndDeactivate.as_view(), name='Q&A-active-deactivate'),
    path('Q&A/delete/<int:pk>', views.QuestionAndAnswerDelete.as_view(), name='Q&A-delete'),

    # apps
    path('apps/', views.AppsListView.as_view(), name='apps-list'),
    path('apps/create/', views.AppsCreateView.as_view(), name='apps-create'),
    path('apps/update/<int:pk>', views.AppsUpdateView.as_view(), name='apps-update'),
    path('apps/active-deactivate/<int:pk>', views.AppsActiveAndDeactivateView.as_view(), name='apps-active-deactivate'),
    path('apps/delete/<int:pk>', views.AppsDeleteView.as_view(), name='apps-delete'),

    # contact page
    path('contact/', views.ContactUsListView.as_view(), name='contact-list'),
    path('contact/details/<int:pk>', views.ContactUsDetails.as_view(), name='contact-details'),
    path('contact/delete/<int:pk>', views.ContactUsDeleteView.as_view(), name='contact-delete'),

    # blog
    path('blog/', views.BlogListView.as_view(), name='blog-list'),

    # blog category
    path('blog/categories/', views.BlogCategoryListView.as_view(), name='blog-category-list'),

]