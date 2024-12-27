from django.urls import path
from electricity_rates.views import CalculatorView, ResultView

app_name = "electricity_rates"

urlpatterns = [
    path("", CalculatorView.as_view(), name="calculator"),
    path("result", ResultView.as_view(), name="result"),
]
