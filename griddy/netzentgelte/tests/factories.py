import factory.fuzzy
from netzentgelte.models import ZipCode


class ZipCodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ZipCode
        django_get_or_create = ("code",)

    code = factory.fuzzy.FuzzyChoice(["12345", "54321"])
