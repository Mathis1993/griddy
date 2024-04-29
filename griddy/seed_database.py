from django.conf import settings
from django.contrib.auth import get_user_model

from users.tests.factories import UserFactory

User = get_user_model()


def seed_database():
    """
    Seed the development database with some initial data and users so that the
    local application is ready to use.

    Returns
    -------
    None
    """
    User.objects.create_superuser(
        email="admin@production_domain.de",
        password=settings.TEST_USER_PASSWORD,
    )
    UserFactory.create(email="user@production_domain.de", password=settings.TEST_USER_PASSWORD)
    create_contents()


def seed_database_staging():
    """
    Seed the staging database with normalized entities, essentially just wrapping the
    create_contents() function.

    Returns
    -------
    None
    """
    create_contents()


def create_contents():
    """
    Create some normalized entities in the database.

    Returns
    -------
    None
    """
    return
