import logging
from typing import Optional

from core.models import TrackCreationAndUpdates
from django.db import models
from netzentgelte.models import Netzentgelt


class TimeProfile(TrackCreationAndUpdates):

    class Meta:
        db_table = "devices_time_profiles"

    name = models.CharField(max_length=255)
    active = models.BooleanField(default=False)
    device = models.ForeignKey(
        to="devices.Device", on_delete=models.CASCADE, related_name="time_profiles"
    )

    def get_current_time_slot(self) -> Optional["TimeSlot"]:
        return self.time_slots.filter(
            start__lte=self.created_at.time(), end__gte=self.created_at.time()
        ).first()


class TimeSlot(TrackCreationAndUpdates):
    logger = logging.getLogger(__name__)

    class Meta:
        db_table = "devices_time_slots"

    time_profile = models.ForeignKey(
        to="devices.TimeProfile", on_delete=models.CASCADE, related_name="time_slots"
    )
    start = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        return f"{self.time_profile.name} - {self.start} - {self.end} - {self.id}"

    def get_current_target_value(self) -> Optional["TimeSlotTargetValue"]:
        target_value = self.target_values.filter(netzentgelt_magnitude=None).first()
        if target_value:
            self.logger.info(
                f"Found target value without netzentgelt magnitude for time slot {self}"
            )
            return target_value
        currently_valid_netzentgelt = Netzentgelt.get_currently_valid_netzentgelt(
            zip_code=self.time_profile.device.address.zip_code
        )
        if not currently_valid_netzentgelt:
            self.logger.info(f"No currently valid netzentgelt found for time slot {self}")
            return None
        return self.target_values.filter(
            netzentgelt_magnitude=currently_valid_netzentgelt.magnitude
        ).first()


class TimeSlotTargetValue(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_time_slot_target_values"
        unique_together = ("time_slot", "netzentgelt_magnitude")

    time_slot = models.ForeignKey(
        to="devices.TimeSlot", on_delete=models.CASCADE, related_name="target_values"
    )
    flow_temperature = models.IntegerField()
    netzentgelt_magnitude = models.ForeignKey(
        to="netzentgelte.Magnitude",
        on_delete=models.RESTRICT,
        related_name="time_slot_target_values",
        null=True,
        blank=True,
        default=None,
    )
