from datetime import timedelta

import factory.fuzzy
from django.utils import timezone
from netzentgelte.models import Magnitude, Netzentgelt, ZipCode


class NetzentgeltFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Netzentgelt

    rate = factory.fuzzy.FuzzyFloat(0.0, 100.0)
    magnitude = factory.SubFactory("netzentgelte.tests.factories.MagnitudeFactory")
    start = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now(), end_dt=timezone.now() + timedelta(days=1)
    )
    end = factory.LazyAttribute(lambda obj: obj.start + timedelta(hours=2))
    zip_code = factory.SubFactory("netzentgelte.tests.factories.ZipCodeFactory")


class MagnitudeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Magnitude

    magnitude = factory.fuzzy.FuzzyChoice([Magnitude.Magnitude.choices])


class ZipCodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ZipCode
        django_get_or_create = ("code",)

    code = factory.fuzzy.FuzzyChoice(["12345", "54321"])
