from django.conf import settings
from django.db import models

from core.models import TrackCreationAndUpdates


class Api(TrackCreationAndUpdates):
    name = models.CharField(max_length=255, unique=True)
    base_url = models.URLField(unique=True)


class ApiKey(TrackCreationAndUpdates):
    key = models.TextField(unique=True)
    expiration = models.DateTimeField()
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_keys"
    )
    api = models.ForeignKey(
        to="external.Api", on_delete=models.CASCADE, related_name="api_keys"
    )
