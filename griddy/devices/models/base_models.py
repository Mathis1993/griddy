import logging

from core.models import TrackCreationAndUpdates
from devices.models.time_control import TimeProfile
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
        time_profile = self.time_profiles.filter(active=True).first()
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


class SpecificDevice(TrackCreationAndUpdates):
    class Meta:
        abstract = True

    generic_devices = GenericRelation(Device, related_query_name="%(app_label)s_%(class)s")
    api_key = models.ForeignKey(
        to="external.ApiKey", on_delete=models.RESTRICT, related_name="%(app_label)s_%(class)s"
    )

    def online(self, *args, **kwargs) -> bool:
        raise NotImplementedError("Method online must be implemented in subclass")

    def synchronize_current_with_desired_state(self, time_profile: TimeProfile):
        raise NotImplementedError(
            "Method synchronize_current_with_desired_state must be implemented in subclass"
        )
