import factory.fuzzy
from electric_cars.models import Car



class CarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Car

    name = factory.Faker('name')
    battery_capacity_kwh = factory.fuzzy.FuzzyInteger(low=30, high=100)