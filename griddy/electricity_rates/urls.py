from django.urls import path

from electricity_rates.views import ZipCodeView

app_name = "electricity_rates"

urlpatterns = [
    path("", ZipCodeView.as_view(), name="calculator"),
]