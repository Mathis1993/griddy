from datetime import timedelta

import factory.fuzzy
from django.utils import timezone
from external.models import ApiConfig, ApiKey


class ApiFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ApiConfig
        django_get_or_create = ("name",)

    name = factory.fuzzy.FuzzyChoice(ApiConfig.ApiNames.values)
    base_url = factory.Faker("url")


class ApiKeyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ApiKey
        django_get_or_create = ("key",)

    key = factory.Sequence(lambda n: f"api_key_{n}")
    expiration = factory.LazyAttribute(lambda _: timezone.now() + timedelta(days=1))
    user = factory.SubFactory("users.tests.factories.UserFactory")
    api = factory.SubFactory(ApiFactory)
