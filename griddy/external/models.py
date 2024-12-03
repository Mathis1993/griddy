import logging
from datetime import date, datetime, timedelta

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
        already_existing_in_range = cls.objects.filter(at__range=[start, end]).order_by("at")
        actual_start = (
            already_existing_in_range.last().at if already_existing_in_range.exists() else start
        )
        if start == end:
            logger.info("Spot prices already imported")
            return

        if already_existing_in_range.exists():
            logger.info(
                f"Importing spot prices from {actual_start} to {end} (already imported until {actual_start})"
            )
        else:
            logger.info(f"Importing spot prices from {actual_start} to {end}")

        energy_charts_api = EnergyChartsApi()
        data = energy_charts_api.get_spot_prices(actual_start, end)

        objs = [
            cls(
                price=price,
                at=datetime.fromtimestamp(timestamp),
                electricity_unit=cls.ElectricityUnit.MEGAWATT_HOUR,
                currency_unit=cls.CurrencyUnit.EURO,
            )
            for timestamp, price in zip(data["unix_seconds"], data["price"])
        ]
        cls.objects.bulk_create(objs)

    @classmethod
    def import_prices_last_year(cls):
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=365)
        cls.import_prices(start, end)

    @classmethod
    def get_prices_for_date(cls, date_to_get: date):
        return cls.objects.filter(at__date=date_to_get).order_by("at")


class SpotPriceAverageLastYear(SpotPrice):
    class Meta:
        db_table = "external_spot_prices_average_last_year"

    at = models.DateField()

    @classmethod
    def compute_and_store_average_last_year_from_today(cls):
        today = date.today()
        if cls.objects.filter(at=today).exists():
            logger.info("Average already computed")
            return

        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=365)

        if (
            not SpotPriceHourly.objects.filter(at=start).exists()
            or not SpotPriceHourly.objects.filter(at=end).exists()
        ):
            logger.info("Spot price data is missing, attempting to import")
            SpotPriceHourly.import_prices_last_year()

        logger.info(
            f"Computing average spot price from last year (using data from {start} to {end})"
        )

        average = SpotPriceHourly.objects.filter(at__range=[start, end]).aggregate(
            models.Avg("price")
        )["price__avg"]

        cls.objects.create(
            price=average,
            at=today,
            electricity_unit=cls.ElectricityUnit.MEGAWATT_HOUR,
            currency_unit=cls.CurrencyUnit.EURO,
        )
