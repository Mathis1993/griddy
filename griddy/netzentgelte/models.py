from django.db import models

from core.models import TrackCreationAndUpdates


class Netzentgelt(TrackCreationAndUpdates):
    class Meta:
        db_table = "netzentgelte_netzentgelte"

    rate = models.FloatField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    zip_code = models.ForeignKey(
        to="netzentgelte.ZipCode", on_delete=models.RESTRICT, related_name="netzentgelte"
    )


class ZipCode(TrackCreationAndUpdates):
    class Meta:
        db_table = "netzentgelte_zip_codes"

    code = models.CharField(max_length=5)
