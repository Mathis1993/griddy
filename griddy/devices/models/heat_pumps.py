from devices.models import Action
from devices.models.base_models import SpecificDevice
from django.db import models
from external.apis.smartthings.api import Api as SmartthingsApi
from external.apis.smartthings.capabilities import FlowTemperatureCapability


class HeatPump(SpecificDevice):
    class Meta:
        abstract = True


class DummyHeatPump(HeatPump):
    class Meta:
        db_table = "devices_dummy_heat_pumps"

    name = models.CharField(max_length=255)
    some_config_value = models.CharField(max_length=255)

    actions = {
        Action.ActionType.TURN_ON: "turn_on",
        Action.ActionType.TURN_OFF: "turn_off",
    }

    def turn_on(self):
        return f"Turning on {self.name}"

    def turn_off(self):
        return f"Turning off {self.name}"


class SmartthingsHeatPump(HeatPump):
    class Meta:
        db_table = "devices_smartthings_heat_pumps"

    name = models.CharField(max_length=255)
    smartthings_device_id = models.CharField(max_length=511)
    module_name_water = models.CharField(max_length=255)
    module_name_heating = models.CharField(max_length=255)
    default_flow_temperature_water = models.IntegerField()
    default_flow_temperature_heating = models.IntegerField()

    actions = {
        Action.ActionType.SET_FLOW_TEMPERATURE: "set_flow_temperature",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = SmartthingsApi(
            base_url=self.api_key.api_config.base_url,
            token=self.api_key.key,
        )

    @property
    def status(self):
        return self.api.device_status(self.smartthings_device_id)

    def online(self, module_name: str) -> bool:
        return self.status["components"][module_name]["switch"]["switch"]["value"] == "on"

    def current_flow_temperature(self, module_name: str) -> int:
        return int(
            self.status["components"][module_name]["thermostatCoolingSetpoint"]["coolingSetpoint"][
                "value"
            ]
        )

    def set_flow_temperature(self, temperature: int, module: str):
        command = FlowTemperatureCapability.set_flow_temperature(temperature, module=module)
        self.api.command(self.smartthings_device_id, command)
