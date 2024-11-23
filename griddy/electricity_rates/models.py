import logging
from datetime import date

from django.db import models

from core.models import TrackCreationAndUpdates
from external.models import SpotPriceAverageLastYear

logger = logging.getLogger(__name__)


class BasicInput(TrackCreationAndUpdates):
    class Meta:
        db_table = "electricity_rates_basic_inputs"

    zip_code = models.ForeignKey("ZipCode", on_delete=models.RESTRICT, related_name="basic_inputs")
    network_operator = models.ForeignKey("NetworkOperator", on_delete=models.RESTRICT, related_name="basic_inputs")
    kilowatt_hour_rate_static = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    basic_fee_monthly_static = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    kilowatt_hours_last_year_static = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    electric_car = models.BooleanField(default=False)
    electric_car_kilowatt_hours = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, default=None)
    electricity_costs_last_year_static = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, default=None)
    electricity_costs_last_year_dynamic = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, default=None)


    def calculate_electricity_costs_last_year_static(self):
        if self.electricity_costs_last_year_static is not None:
            return
        if self.kilowatt_hour_rate_static is None or self.basic_fee_monthly_static is None:
            raise ValueError("Need basic fee and kilowatt hour rate")
        self.electricity_costs_last_year_static = ((self.kilowatt_hour_rate_static * self.kilowatt_hours_last_year_static)/100) + (self.basic_fee_monthly_static * 12)

    def calculate_electricity_costs_last_year_dynamic(self):
        if self.electricity_costs_last_year_dynamic is not None:
            return
        average_spot_price_last_year = SpotPriceAverageLastYear.objects.filter(at=date.today())
        if not average_spot_price_last_year.exists():
            logger.info("No average spot price for the last year, attempting to compute it")
            SpotPriceAverageLastYear.compute_and_store_average_last_year_from_today()
            average_spot_price_last_year = SpotPriceAverageLastYear.objects.filter(at=date.today())

        # ToDo(ME-23.11.24): What do we use as basic monthly fee?
        self.electricity_costs_last_year_dynamic = (((average_spot_price_last_year.first().price/10)/100) * self.kilowatt_hours_last_year_static) + (6 * 12)



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

