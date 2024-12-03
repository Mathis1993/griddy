import pytest
from electric_cars.tests.factories import CarFactory


@pytest.mark.django_db
def test_car_pick_charging_dates():
    car = CarFactory()

    # no remainder
    charging_frequency_per_month = 4
    charging_dates = car.pick_charging_dates(charging_frequency_per_month)
    assert len(charging_dates) == 12
    for days_by_month in charging_dates:
        assert len(days_by_month) == charging_frequency_per_month
        assert sorted(list(set(days_by_month))) == days_by_month  # no duplicates

    # remainder
    charging_frequency_per_month = 6
    charging_dates = car.pick_charging_dates(charging_frequency_per_month)
    assert len(charging_dates) == 12
    for days_by_month in charging_dates:
        assert len(days_by_month) == charging_frequency_per_month
        assert sorted(list(set(days_by_month))) == sorted(days_by_month)

    # preferred weekdays, no remainder, all charging days can be preferred weekdays
    charging_frequency_per_month = 4
    preferred_weekdays = ["monday", "tuesday"]
    charging_dates = car.pick_charging_dates(charging_frequency_per_month, preferred_weekdays)
    assert len(charging_dates) == 12
    for days_by_month in charging_dates:
        assert len(days_by_month) == charging_frequency_per_month
        assert sorted(list(set(days_by_month))) == days_by_month
        assert all(day.weekday() in [0, 1] for day in days_by_month)

    # preferred weekdays, no remainder, not all charging days can be preferred weekdays
    charging_frequency_per_month = 8
    preferred_weekdays = ["wednesday"]
    charging_dates = car.pick_charging_dates(charging_frequency_per_month, preferred_weekdays)
    assert len(charging_dates) == 12
    for days_by_month in charging_dates:
        assert len(days_by_month) == charging_frequency_per_month
        assert sorted(list(set(days_by_month))) == sorted(days_by_month)
        count_of_wednesdays = sum(day.weekday() == 2 for day in days_by_month)
        assert count_of_wednesdays == 4

    # preferred weekdays, remainder, all charging days can be preferred weekdays
    charging_frequency_per_month = 6
    preferred_weekdays = ["friday", "sunday"]
    charging_dates = car.pick_charging_dates(charging_frequency_per_month, preferred_weekdays)
    assert len(charging_dates) == 12
    for days_by_month in charging_dates:
        assert len(days_by_month) == charging_frequency_per_month
        assert sorted(list(set(days_by_month))) == sorted(days_by_month)
        assert all(day.weekday() in [4, 6] for day in days_by_month)

    # preferred weekdays, remainder, not all charging days can be preferred weekdays
    charging_frequency_per_month = 9
    preferred_weekdays = ["tuesday", "thursday"]
    charging_dates = car.pick_charging_dates(charging_frequency_per_month, preferred_weekdays)
    assert len(charging_dates) == 12
    for days_by_month in charging_dates:
        assert len(days_by_month) == charging_frequency_per_month
        assert sorted(list(set(days_by_month))) == sorted(days_by_month)
        count_of_tuesdays = sum(day.weekday() == 1 for day in days_by_month)
        count_of_thursdays = sum(day.weekday() == 3 for day in days_by_month)
        assert count_of_tuesdays == 4
        assert count_of_thursdays == 4


@pytest.mark.django_db
def test_car_calculate_charging_costs():
    car = CarFactory()

    charging_frequency_per_month = 4
    preferred_weekdays = ["monday", "tuesday"]

    charging_dates = car.calculate_charging_costs(charging_frequency_per_month, preferred_weekdays)
