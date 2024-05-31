from external.apis.smartthings.commands import (
    Command,
    OffCommand,
    OnCommand,
    SetFlowTemperatureCommand,
)

FLOW_TEMPERATURE_CAPABILITY = "thermostatCoolingSetpoint"
ON_OFF_CAPABILITY = "switch"


class Capability:
    def __init__(self, name: str, commands: dict[str, Command]):
        self.name = name
        [setattr(self, name, command) for name, command in commands.items()]


FlowTemperatureCapability = Capability(
    name=FLOW_TEMPERATURE_CAPABILITY,
    commands={
        "set_flow_temperature": SetFlowTemperatureCommand(
            capability_name=FLOW_TEMPERATURE_CAPABILITY,
        )
    },
)

OnOffCapability = Capability(
    name=ON_OFF_CAPABILITY,
    commands={
        "turn_on": OnCommand(capability_name=ON_OFF_CAPABILITY),
        "turn_off": OffCommand(capability_name=ON_OFF_CAPABILITY),
    },
)
