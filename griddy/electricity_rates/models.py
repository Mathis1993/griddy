import logging

from core.models import TrackCreationAndUpdates
from django.db import models
from external.models import SpotPriceAverageLastYear

logger = logging.getLogger(__name__)


class BasicInput(TrackCreationAndUpdates):
    class Meta:
        db_table = "electricity_rates_basic_inputs"

    zip_code = models.ForeignKey("ZipCode", on_delete=models.RESTRICT, related_name="basic_inputs")
    network_operator = models.ForeignKey(
        "NetworkOperator", on_delete=models.RESTRICT, related_name="basic_inputs"
    )
    kilowatt_hour_rate_static = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=None
    )
    basic_fee_monthly_static = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=None
    )
    kilowatt_hours_last_year_static = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=None
    )
    electric_car = models.ForeignKey(
        "electric_cars.Car",
        on_delete=models.RESTRICT,
        related_name="basic_inputs",
        null=True,
        blank=True,
        default=None,
    )


class Result(TrackCreationAndUpdates):
    class Meta:
        db_table = "electricity_rates_results"

    basic_input = models.ForeignKey(BasicInput, on_delete=models.CASCADE, related_name="results")
    electricity_costs_last_year_static = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True, default=None
    )
    electricity_costs_last_year_dynamic = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True, default=None
    )

    def potential_savings(self):
        savings = round(
            float(self.electricity_costs_last_year_static)
            - float(self.electricity_costs_last_year_dynamic),
            2,
        )
        return savings, savings > 0


class ZipCode(TrackCreationAndUpdates):
    class Meta:
        db_table = "electricity_rates_zip_codes"

    zip_code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.zip_code

    def one_to_one_network_operator(self) -> bool:
        return self.network_operators.count() == 1


class NetworkOperator(TrackCreationAndUpdates):
    class Meta:
        db_table = "electricity_rates_network_operators"

    name = models.CharField(max_length=255, unique=True)
    zip_code = models.ForeignKey(
        ZipCode, on_delete=models.RESTRICT, related_name="network_operators"
    )

    def __str__(self):
        return self.name
