import logging
from datetime import datetime, date, timedelta

from core.models import TrackCreation
from django.db import models

from external.apis.energy_charts import EnergyChartsApi

logger = logging.getLogger(__name__)


class SpotPrice(TrackCreation):
    class Meta:
        abstract = True

    class ElectricityUnit(models.TextChoices):
        KILOWATT_HOUR = "kWh"
        MEGAWATT_HOUR = "MWh"

    class CurrencyUnit(models.TextChoices):
        EURO = "EURO"
        CENT = "CENT"

    price = models.DecimalField(max_digits=10, decimal_places=2)
    at = models.DateTimeField()
    electricity_unit = models.CharField(max_length=10, choices=ElectricityUnit.choices)
    currency_unit = models.CharField(max_length=10, choices=CurrencyUnit.choices)


class SpotPriceHourly(SpotPrice):
    class Meta:
        db_table = "external_spot_prices_hourly"

    @classmethod
    def import_prices(cls, start: date, end: date):
        # already imported
        if cls.objects.filter(at__range=[start, end]).exists():
            logger.info("Spot prices already imported")
            return

        logger.info(f"Importing spot prices from {start} to {end}")

        energy_charts_api = EnergyChartsApi()
        data = energy_charts_api.get_spot_prices(start, end)

        objs = [cls(
            price=price,
            at=datetime.fromtimestamp(timestamp),
            electricity_unit=cls.ElectricityUnit.MEGAWATT_HOUR,
            currency_unit=cls.CurrencyUnit.EURO,
        ) for timestamp, price in zip(data["unix_seconds"], data["price"]
                                      )]
        cls.objects.bulk_create(objs)


class SpotPriceAverageLastYear(SpotPrice):
    class Meta:
        db_table = "external_spot_prices_average_last_year"

    at = models.DateField()

    @classmethod
    def compute_and_store_average_last_year_from_today(cls):
        if cls.objects.filter(at=date.today()).exists():
            logger.info("Average already computed")
            return

        start = date.today() - timedelta(days=1)
        end = start - timedelta(days=365)

        if not SpotPriceHourly.objects.filter(at__range=[end, start]).exists():
            raise ValueError("SpotPriceHourly data is missing")

        logger.info(f"Computing average spot price from last year (using data from {start} to {end})")

        average = SpotPriceHourly.objects.filter(at__range=[end, start]).aggregate(models.Avg("price"))["price__avg"]

        cls.objects.create(
            price=average,
            at=start,
            electricity_unit=cls.ElectricityUnit.MEGAWATT_HOUR,
            currency_unit=cls.CurrencyUnit.EURO,
        )

