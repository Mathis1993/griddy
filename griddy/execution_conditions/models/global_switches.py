from django.db import models
from execution_conditions.models.base_models import SpecificExecutionCondition


class DummySwitch(SpecificExecutionCondition):
    class Meta:
        db_table = "execution_conditions_dummy_switches"

    value = models.BooleanField(default=False)

    def is_satisfied(self) -> bool:
        return self.value
