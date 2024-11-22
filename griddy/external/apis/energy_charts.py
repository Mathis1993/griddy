import http
from datetime import date

import requests

from external.apis import exceptions

ENERGY_CHARTS_BASE_URL = "https://api.energy-charts.info"
BIDDING_ZONE_DE_AT_LUX = "DE-LU"

class Api:
    def __init__(self, base_url: str, headers: dict=None):
        self.base_url = base_url
        self.headers = headers or {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @staticmethod
    def process_response(response):
        if response.status_code != http.HTTPStatus.OK:
            raise exceptions.ApiException(response.text)
        return response.json()

    def get(self, url: str):
        response = requests.get(url, headers=self.headers)
        return self.process_response(response)


class EnergyChartsApi(Api):
    def __init__(self, base_url: str=ENERGY_CHARTS_BASE_URL):
        super().__init__(base_url)

    def get_spot_prices(self, start: date, end: date, bidding_zone: str=BIDDING_ZONE_DE_AT_LUX):
        """
        Get spot prices for a given bidding zone and time range.
        Returns a list of timestamps and a list of prices (one per hour).
        Note: "end" is inclusive.
        """
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        url = f"{self.base_url}/price?bzn={bidding_zone}&start={start}&end={end}"
        return self.get(url)
