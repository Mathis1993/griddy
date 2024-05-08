import factory.fuzzy
from execution_conditions.models.global_switches import DummySwitch


class DummySwitchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DummySwitch

    value = factory.fuzzy.FuzzyChoice([True, False])
