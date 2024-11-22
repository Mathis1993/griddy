from datetime import date

import pytest

from external.models import SpotPriceHourly


@pytest.mark.django_db
@pytest.mark.vcr
@pytest.mark.block_network
def test_sport_price_hourly_import_prices():
    assert not SpotPriceHourly.objects.exists()

    SpotPriceHourly.import_prices(start=date(2024, 11, 1), end=date(2024, 11, 2))

    assert SpotPriceHourly.objects.exists()
    assert SpotPriceHourly.objects.count() == 48  # end is inclusive

