from .views.serial_search import GuaranteeView, GuaranteeActiveView
from django.urls import path

app_name='guarantee'

urlpatterns = [
    path('', GuaranteeView.as_view(), name='serial-number-search'),
    path('active-search/', GuaranteeActiveView.as_view(), name='serial-number-search-active')
]
