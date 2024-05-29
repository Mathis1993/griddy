from devices.forms import AddressCreateForm
from devices.utils import HEAT_PUMP_INTEGRATIONS, get_heat_pump_integration
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from external.forms import ApiKeyCreateForm


class HeatPumpIntegrationsListView(LoginRequiredMixin, TemplateView):
    template_name = "devices/heat_pump_integrations_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["integrations"] = HEAT_PUMP_INTEGRATIONS
        return context


class HeatPumpCreateView(LoginRequiredMixin, TemplateView):
    template_name = "devices/heat_pump_create.html"

    def get_context_data(self, integration_id: int, **kwargs):
        context = super().get_context_data(**kwargs)
        integration = get_heat_pump_integration(integration_id)
        context["integration"] = integration
        context["api_key_form"] = ApiKeyCreateForm()
        context["address_form"] = AddressCreateForm()
        # ToDo(ME-12.05.24): This is not working yet
        # context["heat_pump_form"] = integration.form_class()
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "devices/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["device"] = self.request.user.devices.first()
        return context
