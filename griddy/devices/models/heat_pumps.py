from core.models import TrackCreationAndUpdates
from django.db import models


class HeatPump(TrackCreationAndUpdates):
    class Meta:
        abstract = True

    api = models.ForeignKey(
        to="external.Api",
        on_delete=models.RESTRICT,
        related_name="%(app_label)s_%(class)s",
    )

    def register_actions(self):
        raise NotImplementedError("register_actions method not implemented")


class DummyHeatPump(HeatPump):
    class Meta:
        db_table = "devices_dummy_heat_pumps"

    name = models.CharField(max_length=255)
    some_config_value = models.CharField(max_length=255)
