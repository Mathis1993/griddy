import factory.fuzzy
from devices.models import TimeProfile, TimeSlot, TimeSlotTargetValue
from django.utils import timezone


class TimeProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimeProfile
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"time_profile_{n}")
    device = factory.SubFactory("devices.tests.factories.DeviceFactory")
    active = factory.fuzzy.FuzzyChoice([True, False])


class TimeSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimeSlot
        django_get_or_create = ("time_profile", "start", "end")

    time_profile = factory.SubFactory(TimeProfileFactory)
    start = factory.LazyAttribute(lambda o: timezone.now().time())
    end = factory.LazyAttribute(lambda o: o.start + timezone.timedelta(hours=2))


class TimeSlotTargetValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimeSlotTargetValue
        django_get_or_create = ("time_slot", "netzentgelt_magnitude")

    time_slot = factory.SubFactory(TimeSlotFactory)
    flow_temperature = factory.fuzzy.FuzzyInteger(30, 70)
    netzentgelt_magnitude = factory.SubFactory("netzentgelte.tests.factories.MagnitudeFactory")
