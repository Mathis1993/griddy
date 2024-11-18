from enum import Enum

from django.views.generic import TemplateView

from electricity_rates.exceptions import QueryParamException
from electricity_rates.forms import BasicInputForm


class ExpandType(Enum):
    NETWORK_OPERATOR = "network_operator"

    def get_template_name(self):
        if self.name == self.NETWORK_OPERATOR.name:
            return "expands/network_operator.html"


class CalculatorView(TemplateView):
    template_name = "calculator.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        basic_input_form = BasicInputForm()
        context["basic_input_form"] = basic_input_form
        return context


class ExpandBasicInputView(TemplateView):
    template_name = None

    def get(self, request, *args, **kwargs):
        expand_type = request.GET.get("expand_type", None)
        if not expand_type:
            raise QueryParamException("query parameter 'expand_type' missing")
        self.handle_expand_type(expand_type)
        return super().get(request, *args, **kwargs)

    def handle_expand_type(self, expand_type: str):
        try:
            expand_type = ExpandType(expand_type)
        except ValueError:
            raise QueryParamException(f"unknown 'expand_type' {expand_type}")
        self.template_name = expand_type.get_template_name()
