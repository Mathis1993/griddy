from django.contrib.auth import get_user_model
from electric_cars.json_import import CarImporter
from electric_cars.tests.factories import CarFactory
from electricity_rates.excel_import import NetworkOperatorImporter

NETWORK_OPERATOR_DATA_PATH = "data/network_operators_costs_2025.xlsx"
ELECTRIC_CARS_DATA_PATH = "data/electric_cars_2024.json"

User = get_user_model()


def seed_database():
    _import_network_operator_data()
    _import_electric_car_data()
    _seed_database()


def _seed_database():
    # ZipCodeFactory.create_batch(size=10)
    # NetworkOperatorFactory.create_batch(size=10)
    # CarFactory.create_batch(size=10)
    pass


def _import_network_operator_data():
    importer = NetworkOperatorImporter(NETWORK_OPERATOR_DATA_PATH)
    importer.import_network_operator_data()


def _import_electric_car_data():
    importer = CarImporter(ELECTRIC_CARS_DATA_PATH)
    importer.import_cars()
