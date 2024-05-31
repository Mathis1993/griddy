from external.apis.smartthings.capabilities import (
    FLOW_TEMPERATURE_CAPABILITY,
    ON_OFF_CAPABILITY,
    Capability,
    FlowTemperatureCapability,
    OnOffCapability,
)
from external.apis.smartthings.commands import (
    Command,
    OffCommand,
    OnCommand,
    SetFlowTemperatureCommand,
)


def test_capability_base_class():
    capability = Capability(name="test", commands={"test": Command(capability_name="test")})
    assert capability.name == "test"
    assert type(capability.test(module="test")) == Command


def test_flow_temperature_capability():
    capability = FlowTemperatureCapability
    assert capability.name == FLOW_TEMPERATURE_CAPABILITY
    assert getattr(capability, "set_flow_temperature", AttributeError)
    assert (
        type(capability.set_flow_temperature(temperature=35, module="main"))
        == SetFlowTemperatureCommand
    )


def test_on_off_capability():
    capability = OnOffCapability
    assert capability.name == ON_OFF_CAPABILITY
    assert getattr(capability, "turn_on", AttributeError)
    assert getattr(capability, "turn_off", AttributeError)
    assert type(capability.turn_on(module="main")) == OnCommand
    assert type(capability.turn_off(module="main")) == OffCommand
