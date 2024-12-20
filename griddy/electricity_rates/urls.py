from django.urls import path
from electricity_rates.views import CalculatorView

app_name = "electricity_rates"

urlpatterns = [
    path("", CalculatorView.as_view(), name="calculator"),
]
