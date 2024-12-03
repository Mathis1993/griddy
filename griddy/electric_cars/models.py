import random
from datetime import date, datetime, timedelta
from typing import List, Optional

from core.models import TrackCreationAndUpdates
from django.db import models
from external.models import SpotPriceHourly

CHARGING_SPEED_KWH_PER_HOUR = 11


class Car(TrackCreationAndUpdates):
    class Meta:
        db_table = "electric_cars"

    name = models.CharField(max_length=255)
    battery_capacity_kwh = models.IntegerField()

    def __str__(self):
        return f"{self.name}"

    def calculate_charging_time_hours(self) -> int:
        return int(self.battery_capacity_kwh / CHARGING_SPEED_KWH_PER_HOUR)

    def calculate_charging_kilowatt_hours(self, charging_frequency_per_month) -> int:
        """
        Calculates the total kilowatt-hours charged into the car over the last 12 months based
        on a charging frequency per month.
        """
        return self.battery_capacity_kwh * charging_frequency_per_month * 12

    def calculate_charging_costs(
        self, charging_frequency_per_month: int, preferred_weekdays: Optional[List[str]] = None
    ) -> float:
        """
        Calculates the charging costs for the last 12 months based on the charging frequency per month and historical data.
        The charging events per month are distributed over the last 12 months.
        For the selected dates, it is assumed that charging happened during the cheapest hours of the day.
        If preferred_weekdays are given, dates corresponding to these weekdays will be used for the calculation.
        Otherwise, dates with no restriction to weekdays will be used.
        """
        charging_dates = sorted(
            [
                charging_date
                for charging_dates_per_month in self.pick_charging_dates(
                    charging_frequency_per_month, preferred_weekdays
                )
                for charging_date in charging_dates_per_month
            ]
        )

        charging_costs = float(
            sum(
                [
                    self.calculate_charging_costs_for_date(charging_date)
                    for charging_date in charging_dates
                ]
            )
        )

        return charging_costs

    @staticmethod
    def pick_charging_dates(
        charging_frequency_per_month: int, preferred_weekdays: Optional[List[str]] = None
    ) -> List[List[date]]:
        one_year_ago = datetime.now() - timedelta(days=365)
        months = [one_year_ago + timedelta(weeks=4 * i) for i in range(12)]
        weeks_by_month = [[month + timedelta(weeks=i) for i in range(4)] for month in months]
        days_by_week_and_month = [
            [[(week + timedelta(days=i)).date() for i in range(7)] for week in weeks]
            for weeks in weeks_by_month
        ]
        charging_days_per_week = charging_frequency_per_month // 4
        remaining_days_per_month = charging_frequency_per_month % 4
        if charging_days_per_week >= 7:
            charging_days_per_week = 7
            remaining_days_per_month = 0

        if preferred_weekdays:
            return _pick_charging_days_preferred_weekdays(
                days_by_week_and_month,
                charging_days_per_week,
                remaining_days_per_month,
                preferred_weekdays,
            )

        return _pick_charging_dates(
            days_by_week_and_month, charging_days_per_week, remaining_days_per_month
        )

    def calculate_charging_costs_for_date(self, charging_date: date) -> float:
        charging_hours = self.calculate_charging_time_hours()
        sport_prices = SpotPriceHourly.get_prices_for_date(charging_date)
        cheapest_hours = sorted(sport_prices, key=lambda x: x.price)[:charging_hours]
        # ToDo(ME-04.12.24): More exact calculation -> take into account the exact charging time (not only full hours)
        # €/MWh -> ct/kWh
        charging_costs_date = sum(
            [(hour.price / 10) * CHARGING_SPEED_KWH_PER_HOUR for hour in cheapest_hours]
        )
        return charging_costs_date


def _pick_charging_dates(
    days_by_week_and_month: List[List[List[date]]],
    charging_days_per_week: int,
    remainder_days_per_month: int,
) -> List[List[date]]:
    charging_dates_by_month = []
    for month in days_by_week_and_month:
        charging_days = []
        for week in month:
            day_indices = random.sample(range(0, 7), charging_days_per_week)
            charging_days += [week[j] for j in day_indices]

        if remainder_days_per_month:
            remainder_days_picked = 0
            for week in month:
                for day in week:
                    if not day in charging_days:
                        if not remainder_days_picked == remainder_days_per_month:
                            charging_days.append(day)
                            remainder_days_picked += 1
        charging_dates_by_month.append(charging_days)

    return charging_dates_by_month


def _pick_charging_days_preferred_weekdays(
    days_by_week_and_month: List[List[List[date]]],
    charging_days_per_week: int,
    remainder_days_per_month: int,
    preferred_weekdays: List[str],
) -> List[List[date]]:
    charging_dates_by_month = []
    for month in days_by_week_and_month:
        charging_days = []
        preferred_weekdays_available_per_month = (
            n_preferred_weekdays := len(preferred_weekdays)
        ) * 4
        preferred_weekdays_left_per_month = preferred_weekdays_available_per_month
        for week in month:
            preferred_weekdays_to_pick = n_preferred_weekdays
            if charging_days_per_week < n_preferred_weekdays:
                preferred_weekdays_to_pick = charging_days_per_week
            preferred_weekdays_picked = 0
            for day in week:
                if day.strftime("%A").lower() in preferred_weekdays:
                    if preferred_weekdays_picked < preferred_weekdays_to_pick:
                        charging_days.append(day)
                        preferred_weekdays_picked += 1
                        preferred_weekdays_left_per_month -= 1

            preferred_weekdays_left_per_week = n_preferred_weekdays - preferred_weekdays_picked
            if preferred_weekdays_to_pick < charging_days_per_week:
                days_picked = 0
                for day in week:
                    if not day in charging_days:
                        if (
                            preferred_weekdays_left_per_week > 0
                            and not day.strftime("%A").lower() in preferred_weekdays
                        ):
                            continue
                        if not preferred_weekdays_picked + days_picked == charging_days_per_week:
                            charging_days.append(day)
                            days_picked += 1
                            preferred_weekdays_left_per_week -= 1
                            preferred_weekdays_left_per_month -= 1

        if remainder_days_per_month:
            remainder_days_picked = 0
            for week in month:
                for day in week:
                    if (
                        preferred_weekdays_left_per_month > 0
                        and not day.strftime("%A").lower() in preferred_weekdays
                    ):
                        continue
                    if not day in charging_days:
                        if not remainder_days_picked == remainder_days_per_month:
                            charging_days.append(day)
                            remainder_days_picked += 1
                            preferred_weekdays_left_per_month -= 1

        charging_dates_by_month.append(charging_days)

    return charging_dates_by_month
