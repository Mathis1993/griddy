from devices.models import Action
from devices.models.base_models import SpecificDevice
from django.db import models


class HeatPump(SpecificDevice):
    class Meta:
        abstract = True

    api = models.ForeignKey(
        to="external.Api",
        on_delete=models.RESTRICT,
        related_name="%(app_label)s_%(class)s",
    )


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
