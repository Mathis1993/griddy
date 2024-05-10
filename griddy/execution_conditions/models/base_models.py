from core.models import TrackCreationAndUpdates
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ExecutionCondition(TrackCreationAndUpdates):
    class Meta:
        db_table = "execution_conditions_execution_conditions"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="execution_conditions"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.RESTRICT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    def is_satisfied(self) -> bool:
        return self.content_object.is_satisfied()


class SpecificExecutionCondition(TrackCreationAndUpdates):
    class Meta:
        abstract = True

    generic_execution_conditions = GenericRelation(
        ExecutionCondition,
        related_query_name="%(app_label)s_%(class)s",
    )

    def is_satisfied(self) -> bool:
        raise NotImplementedError("This method must be implemented in the subclass")
