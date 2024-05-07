from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import TrackCreationAndUpdates


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


class Action(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_actions"

    class ActionType(models.TextChoices):
        TURN_ON = "turn_on"
        TURN_OFF = "turn_off"

    device = models.ForeignKey(
        to="devices.Device", on_delete=models.CASCADE, related_name="actions"
    )
    type = models.CharField(choices=ActionType.choices, max_length=255)
    parameters = models.JSONField()
    execution_conditions = models.ManyToManyField(
        through="devices.ActionExecutionCondition",
        to="execution_conditions.ExecutionCondition",
        related_name="actions",
    )


class CommandLog(TrackCreationAndUpdates):
    class Meta:
        db_table = "devices_commands_logs"

    command = models.ForeignKey(
        to="devices.Command", on_delete=models.CASCADE, related_name="logs"
    )
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