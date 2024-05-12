import factory.fuzzy
from execution_conditions.models.global_switches import DummySwitch, GlobalSwitchHeatPump


class DummySwitchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DummySwitch

    value = factory.fuzzy.FuzzyChoice([True, False])


class GlobalSwitchHeatPumpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GlobalSwitchHeatPump

    control_heat_pump = factory.fuzzy.FuzzyChoice([True, False])
