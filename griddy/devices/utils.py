from dataclasses import dataclass
from typing import Type

from devices.forms import DummyHeatPumpCreateForm, SmartthingsHeatPumpCreateForm
from devices.models.heat_pumps import DummyHeatPump, HeatPump, SmartthingsHeatPump
from django import forms


@dataclass
class HeatPumpIntegration:
    identifier: int
    name: str
    integration_class: Type[HeatPump]
    form_class: Type[forms.ModelForm]


HEAT_PUMP_INTEGRATIONS = [
    HeatPumpIntegration(
        identifier=0,
        name="Dummy",
        integration_class=DummyHeatPump,
        form_class=DummyHeatPumpCreateForm,
    ),
    HeatPumpIntegration(
        identifier=1,
        name="Samsung Smartthings",
        integration_class=SmartthingsHeatPump,
        form_class=SmartthingsHeatPumpCreateForm,
    ),
]


def get_heat_pump_integration(identifier: int) -> HeatPumpIntegration:
    for integration in HEAT_PUMP_INTEGRATIONS:
        if integration.identifier == identifier:
            return integration
    raise ValueError(f"Integration with identifier {identifier} not found")
