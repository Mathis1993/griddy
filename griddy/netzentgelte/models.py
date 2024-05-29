from typing import Optional

from core.models import TrackCreationAndUpdates
from django.db import models
from django.utils import timezone


class Netzentgelt(TrackCreationAndUpdates):
    class Meta:
        db_table = "netzentgelte_netzentgelte"

    rate = models.FloatField()
    magnitude = models.ForeignKey(
        to="netzentgelte.Magnitude", on_delete=models.RESTRICT, related_name="netzentgelte"
    )
    start = models.DateTimeField()
    end = models.DateTimeField()
    zip_code = models.ForeignKey(
        to="netzentgelte.ZipCode", on_delete=models.RESTRICT, related_name="netzentgelte"
    )

    @classmethod
    def get_currently_valid_netzentgelt(cls, zip_code: "ZipCode") -> Optional["Netzentgelt"]:
        now = timezone.now()
        return cls.objects.filter(start__lte=now, end__gte=now, zip_code=zip_code).first()


class Magnitude(TrackCreationAndUpdates):
    class Meta:
        db_table = "netzentgelte_magnitudes"

    class Magnitude(models.TextChoices):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    magnitude = models.CharField(max_length=255, choices=Magnitude.choices)


class ZipCode(TrackCreationAndUpdates):
    class Meta:
        db_table = "netzentgelte_zip_codes"

    code = models.CharField(max_length=5)
