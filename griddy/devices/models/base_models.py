import logging
from typing import Dict

from core.models import TrackCreationAndUpdates
from devices.models.time_control import TimeProfile
from devices.models.utils import ExecutionResult
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Device(TrackCreationAndUpdates):
    logger = logging.getLogger(__name__)

    class Meta:
        db_table = "devices_devices"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices"
    )
    address = models.ForeignKey(
        to="devices.Address", on_delete=models.RESTRICT, related_name="devices"
    )
    manufacturer = models.ForeignKey(
        to="devices.Manufacturer", on_delete=models.RESTRICT, related_name="devices"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.RESTRICT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    manual_mode = models.BooleanField(default=False)
    time_profile_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.id}"

    def online(self, *args, **kwargs) -> bool:
        return self.content_object.online(*args, **kwargs)

    def synchronize_current_with_desired_state(self, *args, **kwargs):
        if not self.online():
            self.logger.info(f"Device {self} is offline, skipping synchronization")
            return
        if self.manual_mode:
            self.logger.info(f"Device {self} is in manual mode, skipping synchronization")
            return
        if not self.time_profile_active:
            self.logger.info(f"Device {self} has no active time profile, skipping synchronization")
            return
        time_profile = self.time_profiles.first(active=True)
        self.content_object.synchronize_current_with_desired_state(time_profile)


class Manufacturer(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_manufacturers"

    name = models.CharField(max_length=255, unique=True)


class Address(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_addresses"

    zip_code = models.ForeignKey(
        to="netzentgelte.ZipCode", on_delete=models.RESTRICT, related_name="addresses"
    )


class Command(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_commands"

    class ExecutionStatus(models.TextChoices):
        WAITING = "waiting"
        QUEUED = "queued"
        DECLINED = "declined"
        EXECUTED = "executed"

    execution_time = models.DateTimeField()
    execution_status = models.CharField(choices=ExecutionStatus.choices, max_length=255)
    action = models.ForeignKey(
        to="devices.Action", on_delete=models.RESTRICT, related_name="commands"
    )

    def execute(self) -> ExecutionResult:
        execution_result = self.action.execute()
        if execution_result.success:
            self.execution_status = Command.ExecutionStatus.EXECUTED
        else:
            CommandLog.objects.create(
                command=self,
                message=execution_result.message,
            )
            self.execution_status = Command.ExecutionStatus.DECLINED
        self.save()
        return execution_result


# ToDo(ME-29.05.24): This is overkill, isn't it?
#  Every heat pump must implement say `set_current_flow_temperature`, `turn_on` and `turn_off`
#  and that's it
class Action(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_actions"
        unique_together = ["device", "type"]

    class ActionType(models.TextChoices):
        TURN_ON = "turn_on"
        TURN_OFF = "turn_off"
        SET_FLOW_TEMPERATURE = "set_flow_temperature"

    device = models.ForeignKey(
        to="devices.Device", on_delete=models.CASCADE, related_name="actions"
    )
    type = models.CharField(choices=ActionType.choices, max_length=255)
    parameters = models.JSONField(null=True, blank=True, default=None)

    def execute(self) -> ExecutionResult:
        return self._execute()

    def _execute(self) -> ExecutionResult:
        device = self.device
        action_method_name = device.content_object.actions.get(self.type)
        if not action_method_name:
            raise NotImplementedError(
                f"Action {self.type} ({self.pk}) not supported "
                f"by device {device.name} ({device.pk})"
            )
        action_method = getattr(device.content_object, action_method_name)
        result = action_method()
        return ExecutionResult(success=True, message="Execution successful", result=result)


class CommandLog(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_commands_logs"

    command = models.ForeignKey(to="devices.Command", on_delete=models.CASCADE, related_name="logs")
    message = models.TextField()


class SpecificDevice(TrackCreationAndUpdates):
    class Meta:
        abstract = True

    generic_devices = GenericRelation(Device, related_query_name="%(app_label)s_%(class)s")
    api_key = models.ForeignKey(
        to="external.ApiKey", on_delete=models.RESTRICT, related_name="%(app_label)s_%(class)s"
    )

    @property
    def actions(self) -> Dict[Action.ActionType, str]:
        raise NotImplementedError("actions property not implemented")

    def register_actions(self, device_id: int):
        [Action.objects.get_or_create(device_id=device_id, type=action) for action in self.actions]

    def online(self, *args, **kwargs) -> bool:
        raise NotImplementedError("Method online must be implemented in subclass")

    def synchronize_current_with_desired_state(self, time_profile: TimeProfile):
        raise NotImplementedError(
            "Method synchronize_current_with_desired_state must be implemented in subclass"
        )
