from external.apis.smartthings.commands import Command, SetFlowTemperatureCommand

FLOW_TEMPERATURE_CAPABILITY = "thermostatCoolingSetpoint"


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
