from django.db import models

from core.models import TrackCreationAndUpdates


class BasicInput(TrackCreationAndUpdates):
    class Meta:
        db_table = "electricity_rates_basic_inputs"

    zip_code = models.ForeignKey("ZipCode", on_delete=models.CASCADE, related_name="basic_inputs")
    kilowatt_hour_rate_static = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, default=None)
    basic_fee_monthly_static = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, default=None)
    kilowatt_hours_last_year_static = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, default=None)
    electricity_costs_last_year_static = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=None)
    electric_car = models.BooleanField(default=False)
    electric_car_kilowatt_hours = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=None)


def calculate_electricity_costs_last_year_static(self):
    if self.electricity_costs_last_year_static is not None:
        return
    if self.kilowatt_hour_rate_static is None or self.basic_fee_static is None:
        raise ValueError("Need basic fee and kilowatt hour rate")
    self.electricity_costs_last_year_static = self.kilowatt_hour_rate_static * self.kilowatt_hours_last_year_static + self.basic_fee_monthly_static * 12


class ZipCode(TrackCreationAndUpdates):
    class Meta:
        db_table = "electricity_rates_zip_codes"

    zip_code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.zip_code


class NetworkOperator(TrackCreationAndUpdates):
    class Meta:
        db_table = "electricity_rates_network_operators"

    name = models.CharField(max_length=255, unique=True)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.RESTRICT, related_name="network_operators")

    def __str__(self):
        return self.name

