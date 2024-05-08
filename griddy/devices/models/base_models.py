from typing import Dict, Optional, Union

from core.models import TrackCreationAndUpdates
from devices.models.utils import ExecutionResult
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from execution_conditions.models import ExecutionCondition


class Device(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_devices"

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices"
    )
    api_key = models.ForeignKey(
        to="external.ApiKey", on_delete=models.RESTRICT, related_name="devices"
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
    execution_conditions = models.ManyToManyField(
        through="devices.DeviceExecutionCondition",
        to="execution_conditions.ExecutionCondition",
        related_name="devices",
    )


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
                failed_execution_condition=execution_result.failed_execution_condition,
                message=execution_result.message,
            )
            self.execution_status = Command.ExecutionStatus.DECLINED
        self.save()
        return execution_result


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
    execution_conditions = models.ManyToManyField(
        through="devices.ActionExecutionCondition",
        to="execution_conditions.ExecutionCondition",
        related_name="actions",
    )

    def execute(self) -> ExecutionResult:
        executable, failed_condition = self._is_executable()
        if executable:
            return self._execute()

        return ExecutionResult(
            success=False,
            message="Action not executable",
            failed_execution_condition=failed_condition,
        )

    def _is_executable(self) -> Union[bool, Optional[ExecutionCondition]]:
        for execution_condition in self.device.execution_conditions.all():
            if not execution_condition.is_satisfied():
                return False, execution_condition

        for execution_condition in self.execution_conditions.all():
            if not execution_condition.is_satisfied():
                return False, execution_condition

        return True, None

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
    failed_execution_condition = models.ForeignKey(
        to="execution_conditions.ExecutionCondition",
        on_delete=models.CASCADE,
        related_name="failed_command_logs",
    )
    message = models.TextField()


class DeviceExecutionCondition(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_devices_execution_conditions"

    device = models.ForeignKey(
        to="devices.Device", on_delete=models.CASCADE, related_name="devices_execution_conditions"
    )
    execution_condition = models.ForeignKey(
        to="execution_conditions.ExecutionCondition",
        on_delete=models.CASCADE,
        related_name="devices_execution_conditions",
    )


class ActionExecutionCondition(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_actions_execution_conditions"

    action = models.ForeignKey(
        to="devices.Action", on_delete=models.CASCADE, related_name="actions_execution_conditions"
    )
    execution_condition = models.ForeignKey(
        to="execution_conditions.ExecutionCondition",
        on_delete=models.CASCADE,
        related_name="actions_execution_conditions",
    )


class SpecificDevice(TrackCreationAndUpdates):
    class Meta:
        abstract = True

    @property
    def actions(self) -> Dict[Action.ActionType, str]:
        raise NotImplementedError("actions property not implemented")

    def register_actions(self, device_id: int):
        [Action.objects.get_or_create(device_id=device_id, type=action) for action in self.actions]
