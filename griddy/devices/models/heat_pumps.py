import logging

from devices.models.base_models import SpecificDevice
from devices.models.time_control import TimeProfile
from devices.models.utils import ExecutionResult
from django.db import models
from external.apis.smartthings.api import Api as SmartthingsApi
from external.apis.smartthings.capabilities import FlowTemperatureCapability, OnOffCapability
from external.apis.smartthings.exceptions import SmartthingsApiException


class HeatPump(SpecificDevice):
    logger = logging.getLogger(__name__)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.id}"

    @classmethod
    def get_integration_name(cls) -> str:
        raise NotImplementedError("Method get_integration_name must be implemented in subclass")

    def current_flow_temperature(self, *args, **kwargs) -> int:
        raise NotImplementedError("Method current_flow_temperature must be implemented in subclass")

    def set_flow_temperature(self, temperature: int, *args, **kwargs) -> ExecutionResult:
        raise NotImplementedError("Method set_flow_temperature must be implemented in subclass")

    def turn_on(self) -> ExecutionResult:
        raise NotImplementedError("Method turn_on must be implemented in subclass")

    def turn_off(self) -> ExecutionResult:
        raise NotImplementedError("Method turn_off must be implemented in subclass")

    def synchronize_current_with_desired_state(self, time_profile: TimeProfile):
        if time_profile is None or not time_profile.active:
            self.logger.info(f"No (active) time profile provided for heat pump {self}")
            return
        time_slot = time_profile.get_current_time_slot()
        if not time_slot:
            self.logger.info(f"No time slot found for time profile {time_profile.name}")
            return
        target_value = time_slot.get_current_target_value()
        if not target_value:
            self.logger.info(f"No target value found for time slot {time_slot}")
            return
        desired_flow_temperature = target_value.flow_temperature
        current_flow_temperature = self.current_flow_temperature()
        if current_flow_temperature == desired_flow_temperature:
            self.logger.info(
                f"Current and desired flow temperature are equal "
                f"({current_flow_temperature}°C) for heat pump {self}"
            )
            return
        success = self.set_flow_temperature(desired_flow_temperature)
        # ToDo(ME-29.05.24): Write log to db?
        if not success:
            self.logger.error(
                f"Failed to set flow temperature to {desired_flow_temperature}°C "
                f"for heat pump {self}"
            )
        self.logger.info(
            f"Successfully set flow temperature to {desired_flow_temperature}°C "
            f"for heat pump {self}"
        )
        return


class DummyHeatPump(HeatPump):
    class Meta:
        db_table = "devices_dummy_heat_pumps"

    name = models.CharField(max_length=255)
    some_config_value = models.CharField(max_length=255)

    @classmethod
    def get_integration_name(cls):
        return "Dummy"

    def turn_on(self) -> ExecutionResult:
        return ExecutionResult(success=True, message="Turned on")

    def turn_off(self) -> ExecutionResult:
        return ExecutionResult(success=True, message="Turned off")

    def online(self, *args, **kwargs) -> bool:
        return True

    def current_flow_temperature(self, *args, **kwargs) -> int:
        return 50

    def set_flow_temperature(self, temperature: int, *args, **kwargs) -> ExecutionResult:
        return ExecutionResult(success=True, message=f"Set flow temperature to {temperature}°C")


class SmartthingsHeatPump(HeatPump):
    class Meta:
        db_table = "devices_smartthings_heat_pumps"

    class Module(models.TextChoices):
        WATER = "main"
        HEATING = "INDOOR"

    name = models.CharField(max_length=255)
    smartthings_device_id = models.CharField(max_length=511)
    module_name = models.CharField(max_length=255, choices=Module.choices)
    default_flow_temperature = models.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = SmartthingsApi(
            base_url=self.api_key.api_config.base_url,
            token=self.api_key.key,
        )

    @classmethod
    def get_integration_name(cls):
        return "Samsung Smartthings"

    @property
    def status(self):
        return self.api.device_status(self.smartthings_device_id)

    def online(self) -> bool:
        return self.status["components"][self.module_name]["switch"]["switch"]["value"] == "on"

    def current_flow_temperature(self) -> int:
        return int(
            self.status["components"][self.module_name]["thermostatCoolingSetpoint"][
                "coolingSetpoint"
            ]["value"]
        )

    def set_flow_temperature(self, temperature: int, *args, **kwargs) -> ExecutionResult:
        command = FlowTemperatureCapability.set_flow_temperature(
            temperature, module=self.module_name
        )
        try:
            self.api.command(self.smartthings_device_id, command)
        except SmartthingsApiException as e:
            self.logger.error(f"Failed to set flow temperature to {temperature}°C: {e}")
            return ExecutionResult(success=False, message=str(e))
        return ExecutionResult(success=True, message=f"Set flow temperature to {temperature}°C")

    def turn_on(self) -> ExecutionResult:
        command = OnOffCapability.turn_on(module=self.module_name)
        try:
            self.api.command(self.smartthings_device_id, command)
        except SmartthingsApiException as e:
            self.logger.error(f"Failed to turn on: {e}")
            return ExecutionResult(success=False, message=str(e))
        return ExecutionResult(success=True, message="Turned on")

    def turn_off(self) -> ExecutionResult:
        command = OnOffCapability.turn_off(module=self.module_name)
        try:
            self.api.command(self.smartthings_device_id, command)
        except SmartthingsApiException as e:
            self.logger.error(f"Failed to turn off: {e}")
            return ExecutionResult(success=False, message=str(e))
        return ExecutionResult(success=True, message="Turned off")
