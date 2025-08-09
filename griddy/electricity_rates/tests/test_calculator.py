from datetime import datetime

import freezegun
import pytest
from electricity_rates.calculator import Calculator
from electricity_rates.tests.factories import BasicInputFactory


@pytest.mark.django_db
def test_calculator_calculate_winter_and_summer_ranges():
    basic_input = BasicInputFactory.create()
    calculator = Calculator(basic_input, basic_fee_monthly_dynamic=6)

    # first quarter of the year
    with freezegun.freeze_time("2024-02-09"):
        winter_ranges, summer_ranges = calculator.calculate_winter_and_summer_ranges()

        assert len(winter_ranges) == 2
        assert len(summer_ranges) == 1
        winter_range_1, winter_range_2 = winter_ranges
        summer_range = summer_ranges[0]
        assert winter_range_1.start == datetime(year=2023, month=2, day=9)
        assert winter_range_1.end == datetime(year=2023, month=3, day=31)
        assert summer_range.start == datetime(year=2023, month=4, day=1)
        assert summer_range.end == datetime(year=2023, month=9, day=30)
        assert winter_range_2.start == datetime(year=2023, month=10, day=1)
        assert winter_range_2.end == datetime(year=2024, month=2, day=9)

    # summer half of the year
    with freezegun.freeze_time("2024-06-08"):
        winter_ranges, summer_ranges = calculator.calculate_winter_and_summer_ranges()

        assert len(winter_ranges) == 1
        assert len(summer_ranges) == 2
        winter_range = winter_ranges[0]
        summer_range_1, summer_range_2 = summer_ranges
        assert summer_range_1.start == datetime(year=2023, month=6, day=9)
        assert summer_range_1.end == datetime(year=2023, month=9, day=30)
        assert winter_range.start == datetime(year=2023, month=10, day=1)
        assert winter_range.end == datetime(year=2024, month=3, day=31)
        assert summer_range_2.start == datetime(year=2024, month=4, day=1)
        assert summer_range_2.end == datetime(year=2024, month=6, day=8)

    # fourth quarter of the year
    with freezegun.freeze_time("2024-11-12"):
        winter_ranges, summer_ranges = calculator.calculate_winter_and_summer_ranges()

        assert len(winter_ranges) == 2
        assert len(summer_ranges) == 1
        winter_range_1, winter_range_2 = winter_ranges
        summer_range = summer_ranges[0]
        assert winter_range_1.start == datetime(year=2023, month=11, day=13)
        assert winter_range_1.end == datetime(year=2024, month=3, day=31)
        assert summer_range.start == datetime(year=2024, month=4, day=1)
        assert summer_range.end == datetime(year=2024, month=9, day=30)
        assert winter_range_2.start == datetime(year=2024, month=10, day=1)
        assert winter_range_2.end == datetime(year=2024, month=11, day=12)

    # exactly winter end (no leap year)
    with freezegun.freeze_time("2023-03-31"):
        winter_ranges, summer_ranges = calculator.calculate_winter_and_summer_ranges()

        assert len(winter_ranges) == 1
        assert len(summer_ranges) == 1
        winter_range = winter_ranges[0]
        summer_range = summer_ranges[0]
        assert summer_range.start == datetime(year=2022, month=4, day=1)
        assert summer_range.end == datetime(year=2022, month=9, day=30)
        assert winter_range.start == datetime(year=2022, month=10, day=1)
        assert winter_range.end == datetime(year=2023, month=3, day=31)

    # summer start (no leap year)
    with freezegun.freeze_time("2023-04-01"):
        winter_ranges, summer_ranges = calculator.calculate_winter_and_summer_ranges()

        assert len(winter_ranges) == 1
        assert len(summer_ranges) == 1
        winter_range = winter_ranges[0]
        summer_range = summer_ranges[0]
        assert summer_range.start == datetime(year=2022, month=4, day=1)
        assert summer_range.end == datetime(year=2022, month=9, day=30)
        assert winter_range.start == datetime(year=2022, month=10, day=1)
        assert winter_range.end == datetime(year=2023, month=3, day=31)

    # summer end (leap year)
    with freezegun.freeze_time("2024-09-30"):
        winter_ranges, summer_ranges = calculator.calculate_winter_and_summer_ranges()

        assert len(winter_ranges) == 1
        assert len(summer_ranges) == 1
        winter_range = winter_ranges[0]
        summer_range = summer_ranges[0]
        assert winter_range.start == datetime(year=2023, month=10, day=1)
        assert winter_range.end == datetime(year=2024, month=3, day=31)
        assert summer_range.start == datetime(year=2024, month=4, day=1)
        assert summer_range.end == datetime(year=2024, month=9, day=30)

    # winter start (leap year)
    with freezegun.freeze_time("2024-10-01"):
        winter_ranges, summer_ranges = calculator.calculate_winter_and_summer_ranges()

        assert len(winter_ranges) == 1
        assert len(summer_ranges) == 1
        winter_range = winter_ranges[0]
        summer_range = summer_ranges[0]
        assert winter_range.start == datetime(year=2023, month=10, day=2)
        assert winter_range.end == datetime(year=2024, month=3, day=31)
        assert summer_range.start == datetime(year=2024, month=4, day=1)
        assert summer_range.end == datetime(year=2024, month=9, day=30)
