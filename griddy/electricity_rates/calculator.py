import logging
from datetime import date, datetime

from electricity_rates.models import BasicInput, Result
from external.models import SpotPriceAverageLastYear

BASIC_FEE_MONTHLY_DYNAMIC_TIBBER_EURO = 6
TAX_PER_KILOWATT_HOUR_CENTS = 6.4


class Calculator:
    logger = logging.getLogger(__name__)
    tax_per_kilowatt_hour_cents = TAX_PER_KILOWATT_HOUR_CENTS

    def __init__(
        self,
        basic_input: BasicInput,
        basic_fee_monthly_dynamic: float = BASIC_FEE_MONTHLY_DYNAMIC_TIBBER_EURO,
    ):
        self.basic_fee_monthly_dynamic = basic_fee_monthly_dynamic
        self.basic_input = basic_input
        self.result = Result(basic_input=self.basic_input)

    def calculate_costs(self) -> Result:
        self.calculate_costs_static_rate()
        self.calculate_costs_dynamic_rate()
        self.result.save()
        return self.result

    def calculate_costs_static_rate(self):
        if (
            self.basic_input.kilowatt_hour_rate_static is None
            or self.basic_input.basic_fee_monthly_static is None
        ):
            raise ValueError("Need basic fee and kilowatt hour rate")
        self.result.electricity_costs_last_year_static = round(
            (
                (
                    self.basic_input.kilowatt_hour_rate_static
                    * self.basic_input.kilowatt_hours_last_year_static
                )
                / 100
            )
            + (self.basic_input.basic_fee_monthly_static * 12),
            2,
        )

    def calculate_costs_dynamic_rate(self):
        if self.result.electricity_costs_last_year_dynamic is not None:
            return

        electric_car = self.basic_input.electric_car is not None
        electric_car_kilowatt_hours = 0.0

        average_spot_price_last_year = SpotPriceAverageLastYear.objects.filter(at=date.today())
        if not average_spot_price_last_year.exists():
            self.logger.info("No average spot price for the last year, attempting to compute it")
            SpotPriceAverageLastYear.compute_and_store_average_last_year_from_today()
            average_spot_price_last_year = SpotPriceAverageLastYear.objects.filter(at=date.today())

        average_spot_price_last_year = float(average_spot_price_last_year.first().price)
        # €/MWh -> ct/kWh
        average_spot_price_last_year /= 10

        kilowatt_hours_last_year_static = self.basic_input.kilowatt_hours_last_year_static
        if electric_car:
            electric_car_kilowatt_hours = (
                self.basic_input.electric_car.calculate_charging_kilowatt_hours(
                    self.basic_input.electric_car_charging_frequency
                )
            )
            kilowatt_hours_last_year_static -= electric_car_kilowatt_hours

        kilowatt_hours = kilowatt_hours_last_year_static
        tax = self.tax_per_kilowatt_hour_cents
        grid_fee = self.basic_input.network_operator.grid_fees.filter(
            year=datetime.now().year
        ).first()

        consumption_costs = (
            kilowatt_hours
            * (
                average_spot_price_last_year
                + tax
                + float(grid_fee.grid_fee_per_kilowatt_hour_cents)
            )
        ) / 100
        basic_fees = float(
            grid_fee.basic_grid_fee_yearly_euro + 12 * self.basic_fee_monthly_dynamic
        )

        consumption_costs_car = 0.0
        if electric_car:
            electric_car_charging_costs = self.basic_input.electric_car.calculate_charging_costs(
                self.basic_input.electric_car_charging_frequency,
                self.basic_input.get_electric_car_charging_weekdays(),
            )
            consumption_costs_car = (
                electric_car_charging_costs
                + (
                    electric_car_kilowatt_hours
                    * (tax + float(grid_fee.grid_fee_per_kilowatt_hour_cents))
                )
            ) / 100

        costs_net = consumption_costs + consumption_costs_car + basic_fees
        self.result.electricity_costs_last_year_dynamic = round(1.19 * costs_net, 2)
