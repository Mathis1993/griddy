from django.urls import path
from electricity_rates.views import CalculatorView, LandingView, ResultView

app_name = "electricity_rates"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("calculator", CalculatorView.as_view(), name="calculator"),
    path("result", ResultView.as_view(), name="result"),
]
