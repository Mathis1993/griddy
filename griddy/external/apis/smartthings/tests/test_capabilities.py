from external.apis.smartthings.capabilities import (
    FLOW_TEMPERATURE_CAPABILITY,
    Capability,
    FlowTemperatureCapability,
)
from external.apis.smartthings.commands import Command, SetFlowTemperatureCommand


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
