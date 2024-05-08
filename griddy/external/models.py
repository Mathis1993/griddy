from core.models import TrackCreationAndUpdates
from django.conf import settings
from django.db import models


class ApiConfig(TrackCreationAndUpdates):
    class Meta:
        db_table = "external_apis"

    class ApiNames(models.TextChoices):
        SMARTTHINGS = "smartthings"

    name = models.CharField(max_length=255, unique=True, choices=ApiNames.choices)
    base_url = models.URLField(unique=True)


class ApiKey(TrackCreationAndUpdates):
    class Meta:
        db_table = "external_api_keys"

    key = models.TextField(unique=True)
    expiration = models.DateTimeField()
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_keys"
    )
    api_config = models.ForeignKey(
        to="external.ApiConfig", on_delete=models.CASCADE, related_name="api_keys"
    )
