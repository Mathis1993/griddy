from django.contrib.auth import get_user_model

from electricity_rates.models import NetworkOperator
from electricity_rates.tests.factories import ZipCodeFactory, NetworkOperatorFactory

User = get_user_model()


def seed_database():
    _seed_database()


def _seed_database():
    ZipCodeFactory.create_batch(size=10)
    NetworkOperatorFactory.create_batch(size=10)