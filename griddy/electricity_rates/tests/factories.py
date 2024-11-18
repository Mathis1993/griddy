import factory.fuzzy

from electricity_rates.models import ZipCode


class ZipCodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ZipCode
        django_get_or_create = ("zip_code",)

    zip_code = factory.fuzzy.FuzzyChoice(
        ["48127", "49652", "41569", "415901", "01234", "01235", "01236", "01237", "01238", "01239"])
