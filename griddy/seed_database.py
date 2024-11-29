from django.contrib.auth import get_user_model

from electric_cars.tests.factories import CarFactory
from electricity_rates.tests.factories import ZipCodeFactory, NetworkOperatorFactory

User = get_user_model()


def seed_database():
    _seed_database()


def _seed_database():
    ZipCodeFactory.create_batch(size=10)
    NetworkOperatorFactory.create_batch(size=10)
    CarFactory.create_batch(size=10)
