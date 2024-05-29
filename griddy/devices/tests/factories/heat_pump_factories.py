import factory.fuzzy
from devices.models import DummyHeatPump
from devices.models.heat_pumps import SmartthingsHeatPump


class DummyHeatPumpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DummyHeatPump
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"dummy_heat_pump_{n}")
    api_key = factory.SubFactory("external.tests.factories.ApiKeyFactory")
    some_config_value = factory.fuzzy.FuzzyChoice(["a", "b", "c", "6"])


class SmartthingsHeatPumpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SmartthingsHeatPump
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"smartthings_heat_pump_{n}")
    api_key = factory.SubFactory("external.tests.factories.ApiKeyFactory")
    smartthings_device_id = factory.Sequence(lambda n: f"smartthings_device_{n}")
    module_name_water = "main"
    module_name_heating = "INDOOR"
    default_flow_temperature_water = factory.fuzzy.FuzzyInteger(low=30, high=70)
    default_flow_temperature_heating = factory.fuzzy.FuzzyInteger(low=30, high=70)
