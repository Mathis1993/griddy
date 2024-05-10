import pytest
from external.apis.smartthings.capabilities import FLOW_TEMPERATURE_CAPABILITY
from external.apis.smartthings.commands import (
    FLOW_TEMPERATURE_COMMAND,
    Command,
    SetFlowTemperatureCommand,
)
from external.apis.smartthings.exceptions import CommandModuleException


def test_command_base_class():
    command = Command(capability_name="test")
    with pytest.raises(NotImplementedError):
        command.name()

    with pytest.raises(CommandModuleException):
        command()

    command_with_module = command(module="main")
    assert command_with_module.module == "main"
    assert command_with_module.arguments == tuple()

    command_with_args = command(1, 2, 3, module="main")
    assert command_with_args.arguments == (1, 2, 3)


def test_flow_temperature_command():
    command = SetFlowTemperatureCommand(capability_name=FLOW_TEMPERATURE_CAPABILITY)

    assert command.name == FLOW_TEMPERATURE_COMMAND
    assert command.to_dict() == {
        "commands": [
            {
                "component": None,
                "capability": FLOW_TEMPERATURE_CAPABILITY,
                "command": FLOW_TEMPERATURE_COMMAND,
                "arguments": [],
            }
        ]
    }

    command_with_args = command(temperature="35", module="main")
    assert command_with_args.to_dict() == {
        "commands": [
            {
                "component": "main",
                "capability": FLOW_TEMPERATURE_CAPABILITY,
                "command": FLOW_TEMPERATURE_COMMAND,
                "arguments": ["35"],
            }
        ]
    }
