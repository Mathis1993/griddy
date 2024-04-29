import factory.fuzzy
from django.conf import settings
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: "user{0}@example.com".format(n))
    password = factory.PostGenerationMethodCall("set_password", settings.TEST_USER_PASSWORD)
    role = factory.fuzzy.FuzzyChoice(["admin", "user"])
    first_login_completed = False
    is_staff = False
