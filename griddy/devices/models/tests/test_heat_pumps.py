import pytest
from devices.models import Address, Device, Manufacturer
from devices.models.heat_pumps import SmartthingsHeatPump
from devices.tests.factories import DeviceFactory, DummyHeatPumpFactory
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from external.models import ApiConfig, ApiKey
from external.tests.factories import ApiConfigFactory, ApiKeyFactory
from pytest_mock import MockerFixture


@pytest.fixture()
def user_with_dummy_heatpump(user):
    dummy_heat_pump = DummyHeatPumpFactory.create(name="Little Dummy")
    device = DeviceFactory.create(user=user, specific_device=dummy_heat_pump)
    return user, dummy_heat_pump, device


@pytest.mark.django_db()
def test_registering_dummy_heat_pump_as_device(user):
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


@pytest.mark.django_db()
def test_device_reverse_generic_relation(user):
    dummy_heat_pump = DummyHeatPumpFactory.create(name="Little Dummy", api_key__user=user)
    device = DeviceFactory.create(user=user, specific_device=dummy_heat_pump)

    assert dummy_heat_pump.generic_devices.first() == device


@pytest.mark.django_db()
def test_device_synchronize_current_with_desired_state(
    user_with_dummy_heatpump, mocker: MockerFixture
):
    _, dummy_heat_pump, device = user_with_dummy_heatpump
    mocked_synch_method = mocker.patch(
        "devices.models.DummyHeatPump.synchronize_current_with_desired_state"
    )

    # device offline
    mocker.patch.object(device, "online", return_value=False)
    device.synchronize_current_with_desired_state()
    assert not mocked_synch_method.called

    # device online, manual mode
    mocker.patch.object(device, "online", return_value=True)
    device.manual_mode = True
    device.save()
    device.synchronize_current_with_desired_state()
    assert not mocked_synch_method.called

    # device online, no manual mode, time profile inactive
    device.manual_mode = False
    device.save()
    device.synchronize_current_with_desired_state()
    assert not mocked_synch_method.called

    # device online, no manual mode, time profile active
    device.time_profile_active = True
    device.save()
    device.synchronize_current_with_desired_state()
    assert mocked_synch_method.called


@pytest.mark.django_db()
def test_dummy_heat_pump_synchronize_current_with_desired_state(
    user_with_dummy_heatpump, mocker: MockerFixture
):
    _, dummy_heat_pump, device = user_with_dummy_heatpump
    mocked_current_flow_temperature = mocker.patch.object(
        dummy_heat_pump, "current_flow_temperature"
    )
    mocked_set_flow_temperature = mocker.patch.object(dummy_heat_pump, "set_flow_temperature")

    # no time profile
    dummy_heat_pump.synchronize_current_with_desired_state(None)
    assert not mocked_current_flow_temperature.called
    assert not mocked_set_flow_temperature.called

    # time profile inactive
    time_profile = mocker.MagicMock(active=False)
    dummy_heat_pump.synchronize_current_with_desired_state(time_profile)
    assert not mocked_current_flow_temperature.called
    assert not mocked_set_flow_temperature.called

    # time slot not found
    time_profile = mocker.MagicMock(active=True)
    time_profile.get_current_time_slot.return_value = None
    dummy_heat_pump.synchronize_current_with_desired_state(time_profile)
    assert not mocked_current_flow_temperature.called
    assert not mocked_set_flow_temperature.called

    # target value not found
    time_slot_mock = mocker.MagicMock()
    time_profile.get_current_time_slot.return_value = time_slot_mock
    time_slot_mock.get_current_target_value.return_value = None
    dummy_heat_pump.synchronize_current_with_desired_state(time_profile)
    assert not mocked_current_flow_temperature.called
    assert not mocked_set_flow_temperature.called

    # current and desired flow temperature are equal
    target_value_mock = mocker.MagicMock(flow_temperature=50)
    time_slot_mock.get_current_target_value.return_value = target_value_mock
    mocked_current_flow_temperature.return_value = 50
    dummy_heat_pump.synchronize_current_with_desired_state(time_profile)
    assert mocked_current_flow_temperature.called
    assert not mocked_set_flow_temperature.called

    # current and desired flow temperature are not equal
    mocked_current_flow_temperature.return_value = 40
    dummy_heat_pump.synchronize_current_with_desired_state(time_profile)
    assert mocked_current_flow_temperature.called
    assert mocked_set_flow_temperature.called


@pytest.mark.django_db()
@pytest.mark.vcr()
@pytest.mark.block_network()
def test_smartthings_heat_pump(user):
    api_config = ApiConfigFactory.create(
        name=ApiConfig.ApiNames.SMARTTHINGS,
        base_url="https://api.smartthings.com/v1/",
    )
    api_key = ApiKeyFactory.create(
        user=user,
        key=settings.TEST_SMARTTHINGS_API_TOKEN,
        api_config=api_config,
    )
    heat_pump = SmartthingsHeatPump.objects.create(
        name="my_heat_pump",
        smartthings_device_id=settings.TEST_SMARTTHINGS_DEVICE_ID,
        module_name=SmartthingsHeatPump.Module.HEATING,
        default_flow_temperature=35,
        api_key=api_key,
    )

    assert heat_pump.api.base_url == "https://api.smartthings.com/v1/"
    assert heat_pump.api.token == settings.TEST_SMARTTHINGS_API_TOKEN

    assert heat_pump.online() is True

    current_flow_temperature = heat_pump.current_flow_temperature()
    assert current_flow_temperature == 35

    heat_pump.set_flow_temperature(temperature=50)

    current_flow_temperature = heat_pump.current_flow_temperature()
    assert current_flow_temperature == 50
