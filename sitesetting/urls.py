from django.urls import path

from .views import (
    Main,
    QuestionsPageView,
    AboutUs,
    ContactUs,
AddTONewsLetters,
footer_render_partial,
header_render_partial
)

app_name = "site"

urlpatterns = [
    path('', Main.as_view(), name='main'),
    path('Q&A', QuestionsPageView.as_view(), name='Q&A'),
    path('about-us', AboutUs.as_view(), name='about-us'),
    path('contact-us', ContactUs.as_view(), name='contact-us'),
    path('add-to-news-letters', AddTONewsLetters.as_view(), name='add-to-news-letters'),


    path('partial/header/', header_render_partial, name='partial-header'),
    path('partial/footer/', footer_render_partial, name='partial-footer'),
]