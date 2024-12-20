import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Tuple

from electricity_rates.models import BasicInput, Result
from external.models import SpotPriceAverageLastYear

BASIC_FEE_MONTHLY_DYNAMIC_TIBBER_EURO = 6
TAX_PER_KILOWATT_HOUR_CENTS = 6.4
HOUSEHOLD_CONSUMPTION_AMOUNT_WINTER_SOLAR_SYSTEM_AND_BATTERY = 0.75
HOUSEHOLD_CONSUMPTION_AMOUNT_WINTER_SOLAR_SYSTEM = 0.65


@dataclass
class Range:
    start: datetime
    end: datetime


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

    def calculate_kwh_and_charging_costs_electric_car(self) -> tuple[float, float]:
        if self.basic_input.electric_car is None:
            return 0.0, 0.0

        electric_car_kilowatt_hours = (
            self.basic_input.electric_car.calculate_charging_kilowatt_hours(
                self.basic_input.electric_car_charging_frequency
            )
        )
        # If charging with solar power, consider only the year's winter half for charging events
        if winter_half_only := self.basic_input.electric_car_charging_with_solar_power:
            electric_car_kilowatt_hours /= 2
        electric_car_charging_costs = self.basic_input.electric_car.calculate_charging_costs(
            self.basic_input.electric_car_charging_frequency,
            self.basic_input.get_electric_car_charging_weekdays(),
            winter_half_only=winter_half_only,
        )
        return electric_car_kilowatt_hours, electric_car_charging_costs

    def calculate_costs_household(self, kilowatt_hours_household: float) -> float:
        # solar system + battery -> 75% of kilowatt_hours_household in winter half
        # solar system -> 65% of kilowatt_hours_household in winter half
        # neither -> 50% of kilowatt_hours_household in winter half
        kilowatt_hours_amount_winter = 0.5
        if solar_system_exists := self.basic_input.solar_system_exists:
            kilowatt_hours_amount_winter = HOUSEHOLD_CONSUMPTION_AMOUNT_WINTER_SOLAR_SYSTEM
        if solar_system_exists and self.basic_input.battery_exists:
            kilowatt_hours_amount_winter = (
                HOUSEHOLD_CONSUMPTION_AMOUNT_WINTER_SOLAR_SYSTEM_AND_BATTERY
            )

        winter_ranges, summer_ranges = self.calculate_winter_and_summer_ranges()
        # ToDo(ME-20.12.24): Continue

        average_spot_price_last_year = SpotPriceAverageLastYear.objects.filter(at=date.today())
        if not average_spot_price_last_year.exists():
            self.logger.info("No average spot price for the last year, attempting to compute it")
            SpotPriceAverageLastYear.compute_and_store_average_last_year_from_today()
            average_spot_price_last_year = SpotPriceAverageLastYear.objects.filter(at=date.today())

        average_spot_price_last_year = float(average_spot_price_last_year.first().price)
        # €/MWh -> ct/kWh
        average_spot_price_last_year /= 10

    @staticmethod
    def calculate_winter_and_summer_ranges() -> Tuple[List[Range], List[Range]]:
        winter_ranges = []
        summer_ranges = []

        # e.g. now=15.11.24
        now = datetime.now()  # 15.11.24
        one_year_ago = now - timedelta(days=365)  # 16.11.23 (leap year 2024)
        winter_end_last_year = one_year_ago.replace(month=3, day=31)  # 31.03.23
        summer_start_last_year = one_year_ago.replace(month=4, day=1)  # 01.04.23
        summer_end_last_year = one_year_ago.replace(month=9, day=30)  # 30.09.23
        winter_start_last_year = one_year_ago.replace(month=10, day=1)  # 01.10.23
        winter_end_this_year = now.replace(month=3, day=31)  # 31.03.24
        summer_start_this_year = now.replace(month=4, day=1)  # 01.04.24
        summer_end_this_year = now.replace(month=9, day=30)  # 30.09.24
        winter_start_this_year = now.replace(month=10, day=1)  # 01.10.24

        if one_year_ago < summer_start_last_year:
            # e.g. now=01.02.24
            winter_ranges.append(
                Range(start=one_year_ago, end=winter_end_last_year)  # 01.02.23  # 31.03.23
            )
            summer_ranges.append(
                Range(
                    start=summer_start_last_year,  # 01.04.23
                    end=summer_end_last_year,  # 30.09.23
                )
            )
            winter_ranges.append(
                Range(start=winter_start_last_year, end=now)  # 01.10.23  # 01.02.24
            )

        elif summer_start_last_year <= one_year_ago < winter_start_last_year:
            # e.g. now=14.05.24
            summer_ranges.append(
                Range(
                    start=one_year_ago,  # 15.05.23
                    end=summer_end_last_year,  # 30.09.23
                )
            )
            winter_ranges.append(
                Range(
                    start=winter_start_last_year,  # 01.10.23
                    end=winter_end_this_year,  # 31.03.24
                )
            )
            summer_ranges.append(
                Range(
                    start=summer_start_this_year,  # 01.04.24
                    end=now,  # 14.05.24
                )
            )

        elif winter_start_last_year <= one_year_ago:
            # e.g. now=03.11.24
            winter_ranges.append(
                Range(start=one_year_ago, end=winter_end_this_year)  # 04.11.23  # 31.03.24
            )
            summer_ranges.append(
                Range(
                    start=summer_start_this_year,  # 01.04.24
                    end=summer_end_this_year,  # 30.09.24
                )
            )
            winter_ranges.append(
                Range(
                    start=winter_start_this_year,  # 01.10.24
                    end=now,  # 03.11.24
                )
            )

        # Sanitize ranges (could be the case that start >= end
        # when hitting border dates exactly
        # (e.g. when now=30.09.24 because of leap year)
        winter_ranges = [
            winter_range for winter_range in winter_ranges if winter_range.start < winter_range.end
        ]
        summer_ranges = [
            summer_range for summer_range in summer_ranges if summer_range.start < summer_range.end
        ]
        return winter_ranges, summer_ranges

    def calculate_costs_dynamic_rate(self):
        if self.result.electricity_costs_last_year_dynamic is not None:
            return

        electric_car_kilowatt_hours, electric_car_charging_costs = (
            self.calculate_kwh_and_charging_costs_electric_car()
        )

        kilowatt_hours_household = (
            float(self.basic_input.kilowatt_hours_last_year_static) - electric_car_kilowatt_hours
        )
        costs_household = self.calculate_costs_household(kilowatt_hours_household)

        # consumption costs
        # brutto costs

        average_spot_price_last_year = SpotPriceAverageLastYear.objects.filter(at=date.today())
        if not average_spot_price_last_year.exists():
            self.logger.info("No average spot price for the last year, attempting to compute it")
            SpotPriceAverageLastYear.compute_and_store_average_last_year_from_today()
            average_spot_price_last_year = SpotPriceAverageLastYear.objects.filter(at=date.today())

        average_spot_price_last_year = float(average_spot_price_last_year.first().price)
        # €/MWh -> ct/kWh
        average_spot_price_last_year /= 10

        electric_car = self.basic_input.electric_car is not None

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
