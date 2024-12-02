from datetime import datetime

import pandas as pd
from electricity_rates.models import GridFee, NetworkOperator, NetworkOperatorZipCode, ZipCode


class Importer:
    """
    Used to import network operators per zip code and their grid fees.
    """

    column_network_operators = "Netzbetreiber"
    column_zip_codes = "postalCode"
    column_grid_fee_per_kilowatt_hour_cents = "Netzentgelt 2025 in ct/kWh"
    column_basic_grid_fee_yearly_euro = "Netzgrundpreis 2025 in €"
    network_operators_name_to_id = {}
    zip_codes_code_to_id = {}

    def __init__(self, path: str):
        self.df = pd.read_excel(path)

    def import_network_operator_data(self):
        self.create_zip_codes()
        self.create_network_operators()
        self.create_network_operator_zip_code_associations()
        self.create_network_operator_grid_fees()

    def create_zip_codes(self):
        zip_codes = self.df.loc[:, self.column_zip_codes]
        zip_codes.dropna(inplace=True)
        zip_codes = list(set(zip_codes))
        zip_code_objs = [ZipCode(zip_code=str(int(code))) for code in zip_codes]
        zip_codes = ZipCode.objects.bulk_create(zip_code_objs, ignore_conflicts=True)
        self.zip_codes_code_to_id = {
            zip_code.zip_code: zip_code.id for zip_code in ZipCode.objects.all()
        }

    def create_network_operators(self):
        network_operators = self.df.loc[:, self.column_network_operators]
        network_operators.dropna(inplace=True)
        network_operators = list(set(network_operators))
        network_operators = [
            NetworkOperator(name=network_operator) for network_operator in network_operators
        ]
        NetworkOperator.objects.bulk_create(network_operators, ignore_conflicts=True)
        self.network_operators_name_to_id = {
            network_operator.name: network_operator.id
            for network_operator in NetworkOperator.objects.all()
        }

    def create_network_operator_zip_code_associations(self):
        network_operators_and_zip_codes = self.df.loc[
            :, [self.column_network_operators, self.column_zip_codes]
        ]
        network_operators_and_zip_codes.dropna(inplace=True)
        network_operators_zip_codes = [
            NetworkOperatorZipCode(
                network_operator_id=network_operator_id,
                zip_code_id=zip_code_id,
            )
            for _, row in network_operators_and_zip_codes.iterrows()
            if (
                network_operator_id := self.network_operators_name_to_id.get(
                    row.get(self.column_network_operators)
                )
            )
            and (
                zip_code_id := self.zip_codes_code_to_id.get(
                    str(int(row.get(self.column_zip_codes)))
                )
            )
        ]
        NetworkOperatorZipCode.objects.bulk_create(
            network_operators_zip_codes, ignore_conflicts=True
        )

    def create_network_operator_grid_fees(self):
        grid_fees = self.df.loc[
            :,
            [
                self.column_network_operators,
                self.column_grid_fee_per_kilowatt_hour_cents,
                self.column_basic_grid_fee_yearly_euro,
            ],
        ]
        grid_fees.dropna(inplace=True)
        grid_fees = [
            GridFee(
                network_operator_id=network_operator_id,
                grid_fee_per_kilowatt_hour_cents=row.get(
                    self.column_grid_fee_per_kilowatt_hour_cents
                ),
                basic_grid_fee_yearly_euro=row.get(self.column_basic_grid_fee_yearly_euro),
                year=datetime.now().year,
            )
            for _, row in grid_fees.iterrows()
            if (
                network_operator_id := self.network_operators_name_to_id.get(
                    row.get(self.column_network_operators)
                )
            )
        ]
        GridFee.objects.bulk_create(grid_fees, ignore_conflicts=True)
