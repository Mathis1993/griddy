import factory.fuzzy
from devices.models import DummyHeatPump


class DummyHeatPumpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DummyHeatPump
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"dummy_heat_pump_{n}")
    api = factory.SubFactory("external.tests.factories.ApiFactory")
    some_config_value = factory.fuzzy.FuzzyChoice(["a", "b", "c", "6"])
