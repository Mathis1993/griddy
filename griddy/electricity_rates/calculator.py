import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cached_property
from typing import List, Tuple

from dateutil.utils import today
from electricity_rates.models import BasicInput, Result
from external.models import SpotPriceAverageLastYear, SpotPriceHourly

BASIC_FEE_MONTHLY_DYNAMIC_TIBBER_EURO = 6
TAX_PER_KILOWATT_HOUR_CENTS = 6.4
HOUSEHOLD_CONSUMPTION_AMOUNT_WINTER_SOLAR_SYSTEM_AND_BATTERY = 0.75
HOUSEHOLD_CONSUMPTION_AMOUNT_WINTER_SOLAR_SYSTEM = 0.65


@dataclass
class Range:
    start: datetime
    end: datetime

    @cached_property
    def days(self):
        return (self.end - self.start).days


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

    @cached_property
    def grid_fee(self):
        return self.basic_input.network_operator.grid_fees.filter(year=datetime.now().year).first()

    def calculate_costs(self) -> Result:
        self.calculate_costs_static_rate()
        self.calculate_costs_dynamic_rate()
        self.calculate_price_range()
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

        # net costs
        electric_car_kilowatt_hours, electric_car_charging_costs = (
            self.calculate_kwh_and_charging_costs_electric_car()
        )

        kilowatt_hours_household = (
            float(self.basic_input.kilowatt_hours_last_year_static) - electric_car_kilowatt_hours
        )
        costs_household = self.calculate_costs_household(kilowatt_hours_household)

        # plus tax and grid fee
        consumption_costs_household = self.add_tax_and_grid_fee_to_costs(
            kilowatt_hours_household, costs_household
        )
        consumption_costs_electric_car = self.add_tax_and_grid_fee_to_costs(
            electric_car_kilowatt_hours, electric_car_charging_costs
        )

        # basic fees
        basic_fees = self.calculate_basic_fees()

        # brutto costs
        consumption_costs = (consumption_costs_household + consumption_costs_electric_car) / 100
        total_costs = 1.19 * (consumption_costs + basic_fees)
        self.result.electricity_costs_last_year_dynamic = round(total_costs, 2)

    # ToDo(ME-23.12.24): Validate this is correct
    def calculate_price_range(self):
        """
        Calculates the min, max and mean (brutto) ct/kWh prices for the last year.
        """
        now = datetime.now()
        one_year_ago = now - timedelta(days=365)
        mean_last_year = SpotPriceHourly.calculate_price_for_time_period(
            start=one_year_ago.date(), end=now.date()
        )
        min_last_year = SpotPriceHourly.calculate_price_for_time_period(
            start=one_year_ago.date(), end=now.date(), aggregation_type="min"
        )
        max_last_year = SpotPriceHourly.calculate_price_for_time_period(
            start=one_year_ago.date(), end=now.date(), aggregation_type="max"
        )

        prices = [mean_last_year, min_last_year, max_last_year]

        # €/MWh -> ct/kWh
        prices = [price / 10 for price in prices]

        prices = [self.add_tax_and_grid_fee_to_costs(1, price) for price in prices]

        prices = [1.19 * price for price in prices]

        (
            self.result.mean_price_kilowatt_hours_last_year_dynamic,
            self.result.min_price_kilowatt_hours_last_year_dynamic,
            self.result.max_price_kilowatt_hours_last_year_dynamic,
        ) = prices

    def calculate_kwh_and_charging_costs_electric_car(self) -> tuple[float, float]:
        if self.basic_input.electric_car is None:
            return 0.0, 0.0

        # ToDo(ME-23.12.24): Return result object also containing mean ct/kWh
        #  for charging electric car and potential warnings
        electric_car_kilowatt_hours, electric_car_charging_costs = (
            self.basic_input.electric_car.calculate_charging_costs(
                self.basic_input.electric_car_charging_frequency,
                self.basic_input.get_electric_car_charging_weekdays(),
                # If charging with solar power, consider only the year's winter half
                # for charging events
                winter_half_only=self.basic_input.electric_car_charging_with_solar_power,
            )
        )
        return electric_car_kilowatt_hours, electric_car_charging_costs

    # ToDo(ME-23.12.24): Return result object also containing mean ct/kWh for household consumption
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

        kilowatt_hours_winter = kilowatt_hours_amount_winter * kilowatt_hours_household
        kilowatt_hours_summer = (1 - kilowatt_hours_amount_winter) * kilowatt_hours_household

        winter_ranges, summer_ranges = self.calculate_winter_and_summer_ranges()
        winter_days = sum([winter_range.days for winter_range in winter_ranges])
        summer_days = sum([winter_range.days for winter_range in winter_ranges])
        average_prices_winter = [
            SpotPriceHourly.calculate_price_for_time_period(
                start=winter_range.start.date(), end=winter_range.end.date()
            )
            * winter_range.days
            / winter_days
            for winter_range in winter_ranges
        ]
        average_prices_summer = [
            SpotPriceHourly.calculate_price_for_time_period(
                start=summer_range.start.date(), end=summer_range.end.date()
            )
            * summer_range.days
            / summer_days
            for summer_range in summer_ranges
        ]
        average_spot_price_winter = sum(average_prices_winter)
        average_spot_price_summer = sum(average_prices_summer)

        # €/MWh -> ct/kWh
        average_spot_price_winter /= 10
        average_spot_price_summer /= 10

        costs_winter = kilowatt_hours_winter * float(average_spot_price_winter)
        costs_summer = kilowatt_hours_summer * float(average_spot_price_summer)
        return costs_winter + costs_summer

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

    def add_tax_and_grid_fee_to_costs(
        self, kilowatt_hours: float, costs_for_kilowatt_hours_cents: float
    ) -> float:
        """
        Given a number of kilowatt-hours and net costs for that number
        in cents, adds tax and grid fee.
        """
        tax = self.tax_per_kilowatt_hour_cents

        return costs_for_kilowatt_hours_cents + (
            kilowatt_hours * (tax + float(self.grid_fee.grid_fee_per_kilowatt_hour_cents))
        )

    def calculate_basic_fees(self) -> float:
        return float(self.grid_fee.basic_grid_fee_yearly_euro + 12 * self.basic_fee_monthly_dynamic)
