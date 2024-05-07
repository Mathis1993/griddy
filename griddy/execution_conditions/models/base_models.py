from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import TrackCreationAndUpdates


class ExecutionCondition(TrackCreationAndUpdates):
    class Meta:
        db_table = "execution_conditions_execution_conditions"

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="execution_conditions"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.RESTRICT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")

