from django.urls import path

from electricity_rates.views import CalculatorView, ExpandBasicInputView

app_name = "electricity_rates"

urlpatterns = [
    path("", CalculatorView.as_view(), name="calculator"),
    path("expand_input/", ExpandBasicInputView.as_view(), name="expand_input"),
]