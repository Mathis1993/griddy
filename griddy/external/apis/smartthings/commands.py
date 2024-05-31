from external.apis.smartthings.exceptions import CommandModuleException

FLOW_TEMPERATURE_COMMAND = "setCoolingSetpoint"
ON_COMMAND = "on"
OFF_COMMAND = "off"


class Command:
    @property
    def name(self):
        raise NotImplementedError

    def __init__(self, capability_name: str):
        self.capability_name = capability_name
        self.module = None
        self.arguments = None

    def __call__(self, *args, **kwargs):
        self.arguments = args
        self.module = kwargs.get("module")
        if not self.module:
            raise CommandModuleException
        return self

    def to_dict(self):
        return {
            "commands": [
                {
                    "component": self.module,
                    "capability": self.capability_name,
                    "command": self.name,
                    "arguments": list(self.arguments or []),
                }
            ]
        }


class SetFlowTemperatureCommand(Command):
    name = FLOW_TEMPERATURE_COMMAND

    def __call__(self, temperature: str, module: str):
        args = [temperature]
        kwargs = {"module": module}
        return super().__call__(*args, **kwargs)


class OnCommand(Command):
    name = ON_COMMAND


class OffCommand(Command):
    name = OFF_COMMAND
