from .views.serial_search import GuaranteeView
from django.urls import path

app_name='guarantee'

urlpatterns = [
    path('', GuaranteeView.as_view(), name='serial-number-search')
]
