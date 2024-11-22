import factory.fuzzy

from external.models import SpotPriceHourly, SpotPriceAverageLastYear


class SpotPriceHourlyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpotPriceHourly
        django_get_or_create = ("at",)

    price = factory.fuzzy.FuzzyDecimal(0.1, 1000.0)
    at = factory.Faker("date_time_this_year")
    electricity_unit = factory.fuzzy.FuzzyChoice([SpotPriceHourly.ElectricityUnit.choices])
    currency_unit = factory.fuzzy.FuzzyChoice([SpotPriceHourly.CurrencyUnit.choices])


class SpotPriceAverageLastYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpotPriceAverageLastYear
        django_get_or_create = ("at",)

    price = factory.fuzzy.FuzzyDecimal(0.1, 1000.0)
    at = factory.Faker("date_this_year")
    electricity_unit = factory.fuzzy.FuzzyChoice([SpotPriceAverageLastYear.ElectricityUnit.choices])
    currency_unit = factory.fuzzy.FuzzyChoice([SpotPriceAverageLastYear.CurrencyUnit.choices])