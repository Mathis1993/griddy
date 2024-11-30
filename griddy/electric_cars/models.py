from core.models import TrackCreationAndUpdates
from django.db import models


class Car(TrackCreationAndUpdates):
    class Meta:
        db_table = "electric_cars"

    name = models.CharField(max_length=255)
    battery_capacity_kwh = models.IntegerField()

    def __str__(self):
        return f"{self.name}"


def calculate_charging_costs():
    # ToDo(ME-29.11.24):
    pass
