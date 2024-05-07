import pytest
from devices.models import Address, Device, Manufacturer
from devices.tests.factories import DeviceFactory, DummyHeatPumpFactory
from django.contrib.contenttypes.models import ContentType
from external.models import ApiKey
from users.tests.factories import UserFactory


@pytest.mark.django_db()
def test_registering_dummy_heat_pump_as_device():
    user = UserFactory.create()
    dummy_heat_pump = DummyHeatPumpFactory.create(name="Little Dummy")

    # use factory
    device_1 = DeviceFactory.create(user=user, specific_device=dummy_heat_pump)
    assert device_1.content_object == dummy_heat_pump

    # use model manager
    device_2 = Device.objects.create(
        name="my_device",
        user=user,
        api_key=ApiKey.objects.first(),
        address=Address.objects.first(),
        manufacturer=Manufacturer.objects.first(),
        content_type=ContentType.objects.get_for_model(dummy_heat_pump),
        object_id=dummy_heat_pump.id,
    )
    assert device_2.content_object == dummy_heat_pump

    # Action
    # Command
