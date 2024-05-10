import pytest
from devices.models import Action, Address, Command, CommandLog, Device, Manufacturer
from devices.models.heat_pumps import SmartthingsHeatPump
from devices.tests.factories import DeviceFactory, DummyHeatPumpFactory
from devices.tests.factories.base_factories import ActionFactory, CommandFactory
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from execution_conditions.tests.factories import DummySwitchFactory, ExecutionConditionFactory
from external.models import ApiConfig, ApiKey
from external.tests.factories import ApiConfigFactory, ApiKeyFactory


@pytest.fixture()
def user_with_dummy_heatpump(user):
    dummy_heat_pump = DummyHeatPumpFactory.create(name="Little Dummy")
    device = DeviceFactory.create(user=user, specific_device=dummy_heat_pump)
    dummy_heat_pump.register_actions(device.id)
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
def test_executing_a_command(user_with_dummy_heatpump):
    assert Action.objects.count() == 2

    action_on = Action.objects.filter(type=Action.ActionType.TURN_ON).first()
    action_off = Action.objects.filter(type=Action.ActionType.TURN_OFF).first()

    command_on = CommandFactory.create(
        execution_time=timezone.now(),
        execution_status=Command.ExecutionStatus.WAITING,
        action=action_on,
    )
    command_off = CommandFactory.create(
        execution_time=timezone.now(),
        execution_status=Command.ExecutionStatus.WAITING,
        action=action_off,
    )

    assert command_on.execution_status == Command.ExecutionStatus.WAITING
    assert command_off.execution_status == Command.ExecutionStatus.WAITING

    result = command_on.execute()
    assert result.success
    assert result.result == "Turning on Little Dummy"

    result = command_off.execute()
    assert result.success
    assert result.result == "Turning off Little Dummy"

    command_on.refresh_from_db()
    command_off.refresh_from_db()
    assert command_on.execution_status == Command.ExecutionStatus.EXECUTED
    assert command_off.execution_status == Command.ExecutionStatus.EXECUTED


@pytest.mark.django_db()
def test_executing_a_command_device_does_not_implement_action(user_with_dummy_heatpump):
    _, _, device = user_with_dummy_heatpump
    new_action = ActionFactory.create(type="so_new", device=device)
    command = CommandFactory.create(
        execution_time=timezone.now(),
        execution_status=Command.ExecutionStatus.WAITING,
        action=new_action,
    )

    with pytest.raises(NotImplementedError):
        command.execute()


@pytest.mark.django_db()
def test_executing_a_command_with_execution_conditions(user_with_dummy_heatpump):
    user, dummy_heat_pump, device = user_with_dummy_heatpump
    dummy_switch_on = DummySwitchFactory.create(value=True)
    dummy_switch_off = DummySwitchFactory.create(value=False)
    execution_condition_1 = ExecutionConditionFactory.create(
        name="condition_1", specific_condition=dummy_switch_on
    )
    execution_condition_2 = ExecutionConditionFactory.create(
        name="condition_2", specific_condition=dummy_switch_off
    )

    action = Action.objects.filter(type=Action.ActionType.TURN_ON).first()
    command_1 = CommandFactory.create(
        execution_time=timezone.now(),
        execution_status=Command.ExecutionStatus.WAITING,
        action=action,
    )
    command_2 = CommandFactory.create(
        execution_time=timezone.now(),
        execution_status=Command.ExecutionStatus.WAITING,
        action=action,
    )

    # all conditions fulfilled
    device.execution_conditions.add(execution_condition_1)
    action.execution_conditions.add(execution_condition_1)

    result = command_1.execute()
    assert result.success
    assert result.message == "Execution successful"
    assert result.result == "Turning on Little Dummy"

    command_1.refresh_from_db()
    assert command_1.execution_status == Command.ExecutionStatus.EXECUTED
    assert not CommandLog.objects.exists()

    # one condition not fulfilled
    device.execution_conditions.add(execution_condition_2)

    result = command_2.execute()
    assert result.success is False
    assert result.failed_execution_condition == execution_condition_2
    assert result.message == "Action not executable"

    command_2.refresh_from_db()
    assert command_2.execution_status == Command.ExecutionStatus.DECLINED
    assert CommandLog.objects.count() == 1
    command_log = CommandLog.objects.first()
    assert command_log.command == command_2
    assert command_log.failed_execution_condition == execution_condition_2


@pytest.mark.django_db()
def test_device_reverse_generic_relation(user):
    dummy_heat_pump = DummyHeatPumpFactory.create(name="Little Dummy", api_key__user=user)
    device = DeviceFactory.create(user=user, specific_device=dummy_heat_pump)

    assert dummy_heat_pump.generic_devices.first() == device


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
        module_name_water="main",
        module_name_heating="INDOOR",
        default_flow_temperature_water=35,
        default_flow_temperature_heating=35,
        api_key=api_key,
    )

    assert heat_pump.api.base_url == "https://api.smartthings.com/v1/"
    assert heat_pump.api.token == settings.TEST_SMARTTHINGS_API_TOKEN

    assert heat_pump.actions == {
        Action.ActionType.SET_FLOW_TEMPERATURE: "set_flow_temperature",
    }

    module_name = "INDOOR"
    assert heat_pump.online(module_name) is True

    current_flow_temperature = heat_pump.current_flow_temperature(module_name)
    assert current_flow_temperature == 35

    heat_pump.set_flow_temperature(temperature=50, module=module_name)

    current_flow_temperature = heat_pump.current_flow_temperature(module_name)
    assert current_flow_temperature == 50
