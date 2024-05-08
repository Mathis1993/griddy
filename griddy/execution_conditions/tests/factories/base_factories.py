import factory.fuzzy
from django.contrib.contenttypes.models import ContentType
from execution_conditions.models import ExecutionCondition


class ExecutionConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExecutionCondition

    name = factory.Sequence(lambda n: f"execution_condition_{n}")
    user = factory.SubFactory("users.tests.factories.UserFactory")
    content_type = None
    object_id = None

    @classmethod
    def create(cls, **kwargs):
        from .global_switches_factories import DummySwitchFactory

        specific_condition = kwargs.pop("specific_condition", None)
        if not specific_condition:
            specific_condition = DummySwitchFactory.create(value=kwargs.get("value", True))
        content_type = ContentType.objects.get_for_model(specific_condition)
        object_id = specific_condition.id
        return super().create(content_type=content_type, object_id=object_id, **kwargs)
