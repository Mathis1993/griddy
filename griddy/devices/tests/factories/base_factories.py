from datetime import timedelta

import factory.fuzzy
from devices.models import Action, Address, Command, Device, Manufacturer
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class DeviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Device

    name = factory.Sequence(lambda n: f"device_{n}")
    user = factory.SubFactory("users.tests.factories.UserFactory")
    address = factory.SubFactory("devices.tests.factories.AddressFactory")
    manufacturer = factory.SubFactory("devices.tests.factories.ManufacturerFactory")
    content_type = None
    object_id = None
    manual_mode = factory.fuzzy.FuzzyChoice([True, False])
    time_profile_active = factory.fuzzy.FuzzyChoice([True, False])

    @classmethod
    def create(cls, **kwargs):
        from .heat_pump_factories import DummyHeatPumpFactory

        specific_device = kwargs.pop("specific_device", None)
        if not specific_device:
            specific_device = DummyHeatPumpFactory.create(
                name=kwargs.get("name", "dummy_heat_pump")
            )
        content_type = ContentType.objects.get_for_model(specific_device)
        object_id = specific_device.id
        return super().create(content_type=content_type, object_id=object_id, **kwargs)


class ManufacturerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Manufacturer
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"manufacturer_{n}")


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address
        django_get_or_create = ("zip_code",)

    zip_code = factory.SubFactory("netzentgelte.tests.factories.ZipCodeFactory")


class CommandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Command

    execution_time = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now(), end_dt=timezone.now() + timedelta(days=1)
    )
    execution_status = factory.fuzzy.FuzzyChoice(Command.ExecutionStatus.values)
    action = factory.SubFactory("devices.tests.factories.ActionFactory")


class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Action

    device = factory.SubFactory("devices.tests.factories.DeviceFactory")
    type = factory.fuzzy.FuzzyChoice(Action.ActionType.values)
    parameters = None
