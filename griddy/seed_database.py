from datetime import timedelta

from devices.tests.factories import AddressFactory, DeviceFactory, ManufacturerFactory
from devices.tests.factories.heat_pump_factories import SmartthingsHeatPumpFactory
from devices.tests.factories.time_control_factories import (
    TimeProfileFactory,
    TimeSlotFactory,
    TimeSlotTargetValueFactory,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from external.tests.factories import ApiConfigFactory, ApiKeyFactory
from netzentgelte.models import Magnitude
from netzentgelte.tests.factories import MagnitudeFactory, NetzentgeltFactory, ZipCodeFactory

User = get_user_model()


def seed_database():
    _seed_database(
        smartthings_api_key=settings.TEST_SMARTTHINGS_API_TOKEN,
        smartthings_device_id=settings.TEST_SMARTTHINGS_DEVICE_ID,
    )


def _seed_database(smartthings_api_key: str, smartthings_device_id: str):
    user = User.objects.create_superuser(
        email="john@ofus.com",
        password=settings.TEST_USER_PASSWORD,
    )

    api_config = ApiConfigFactory.create(
        name="smartthings", base_url="https://api.smartthings.com/v1/"
    )
    api_key = ApiKeyFactory.create(
        key=smartthings_api_key,
        expiration=timezone.now() + timedelta(days=365),
        user=user,
        api_config=api_config,
    )

    zip_code = ZipCodeFactory.create(code="12345")
    address = AddressFactory.create(zip_code=zip_code)

    manufacturer = ManufacturerFactory.create(name="samsung")
    smartthings_heat_pump = SmartthingsHeatPumpFactory.create(
        name="wingst_heat_pump",
        api_key=api_key,
        smartthings_device_id=smartthings_device_id,
        default_flow_temperature_water=35,
        default_flow_temperature_heating=35,
    )
    device = DeviceFactory.create(
        name="wingst_device",
        user=user,
        address=address,
        manufacturer=manufacturer,
        specific_device=smartthings_heat_pump,
    )

    now = timezone.now()
    magnitude = MagnitudeFactory.create(magnitude=Magnitude.Magnitude.LOW)
    NetzentgeltFactory.create(
        rate=0.5,
        magnitude=magnitude,
        start=now - timedelta(hours=1),
        end=now + timedelta(hours=1),
        zip_code=zip_code,
    )

    time_profile = TimeProfileFactory.create(
        name="wingst_time_profile",
        device=device,
        active=True,
    )
    time_slot = TimeSlotFactory.create(
        time_profile=time_profile,
        start=now.time(),
        end=now.time() + timedelta(hours=2),
    )
    TimeSlotTargetValueFactory.create(
        time_slot=time_slot,
        flow_temperature=35,
        netzentgelt_magnitude=magnitude,
    )
