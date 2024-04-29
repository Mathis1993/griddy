import http

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_index_view_admin(admin_client):
    url = reverse("users:index")

    response = admin_client.get(url)
    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("admin:index")


@pytest.mark.django_db
def test_index_view_user(client):
    user = UserFactory.create(role=User.Role.USER)
    client.force_login(user)
    url = reverse("users:index")

    response = client.get(url)

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("home")


@pytest.mark.django_db
def test_password_change_view_invalid_form_submission(client):
    user = UserFactory.create(role=User.Role.USER)
    client.force_login(user)
    url = reverse("users:change_password")

    response = client.post(url)

    assert response.status_code == http.HTTPStatus.OK
    user.refresh_from_db()
    assert user.first_login_completed is False


@pytest.mark.django_db
def test_password_change_view_valid_form_submission(client):
    user = UserFactory.create(role=User.Role.USER)
    client.force_login(user)
    url = reverse("users:change_password")

    response = client.post(
        url,
        {
            "old_password": settings.TEST_USER_PASSWORD,
            "new_password1": "aioxRt6vc",
            "new_password2": "aioxRt6vc",
        },
    )

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("users:index")
    user.refresh_from_db()
    assert user.first_login_completed is True


@pytest.mark.django_db
def test_email_update_view(client):
    user = UserFactory.create(email="old_email@example.com")
    client.force_login(user)
    response = client.post(
        reverse("users:change_email", kwargs={"pk": user.id}),
        {"email": "new_email@example.com"},
    )
    assert response.status_code == 302
    assert response.url == reverse("users:index")
    user.refresh_from_db()
    assert user.email == "new_email@example.com"
