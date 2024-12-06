from django.contrib.auth import get_user_model
from electric_cars.tests.factories import CarFactory
from electricity_rates.excel_import import NetworkOperatorImporter

NETWORK_OPERATOR_DATA_PATH = "data/network_operators_costs_2025.xlsx"

User = get_user_model()


def seed_database():
    _import_network_operator_data()
    _seed_database()


def _seed_database():
    # ZipCodeFactory.create_batch(size=10)
    # NetworkOperatorFactory.create_batch(size=10)
    CarFactory.create_batch(size=10)


def _import_network_operator_data():
    importer = NetworkOperatorImporter(NETWORK_OPERATOR_DATA_PATH)
    importer.import_network_operator_data()
