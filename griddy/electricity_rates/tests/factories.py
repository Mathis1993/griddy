import random

import factory.fuzzy
from electric_cars.tests.factories import CarFactory
from electricity_rates.models import BasicInput, NetworkOperator, ZipCode


class ZipCodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ZipCode
        django_get_or_create = ("zip_code",)

    zip_code = factory.fuzzy.FuzzyChoice(
        ["48127", "49652", "41569", "415901", "01234", "01235", "01236", "01237", "01238", "01239"]
    )


class NetworkOperatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NetworkOperator
        django_get_or_create = ("name",)

    name = factory.Faker("company")


class BasicInputFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BasicInput

    zip_code = factory.SubFactory(ZipCodeFactory)
    network_operator = factory.SubFactory(NetworkOperatorFactory)
    kilowatt_hour_rate_static = factory.fuzzy.FuzzyDecimal(low=10, high=60)
    basic_fee_monthly_static = factory.fuzzy.FuzzyDecimal(low=5, high=30)
    kilowatt_hours_last_year_static = factory.fuzzy.FuzzyDecimal(low=1000, high=10000)
    electric_car = factory.SubFactory(CarFactory)
    electric_car_charging_frequency = factory.fuzzy.FuzzyInteger(low=1, high=6)
    electric_car_charging_weekdays = factory.fuzzy.FuzzyChoice(
        [None, "wednesday,friday", "wednesday,thursday", "saturday"]
    )
    solar_system_exists = factory.fuzzy.FuzzyChoice([True, False])
    electric_car_charging_with_solar_power = factory.LazyAttribute(
        lambda obj: random.choice([True, False]) if obj.solar_system_exists else False
    )
    battery_exists = factory.LazyAttribute(
        lambda obj: random.choice([True, False]) if obj.solar_system_exists else False
    )
