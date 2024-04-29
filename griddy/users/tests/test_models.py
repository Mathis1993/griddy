from http import HTTPStatus

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from users.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_create_superuser():
    user_manager = User.objects
    email = "admin@example.com"
    password = "adminpass"

    assert not user_manager.exists()

    user = user_manager.create_superuser(email, password)

    assert user.email == email
    assert user.check_password(password)
    assert user.is_admin()
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.first_login_completed is True
    assert user_manager.count() == 1


@pytest.mark.django_db
def test_create_superuser_without_password():
    user_manager = User.objects
    email = "admin@example.com"

    with pytest.raises(TypeError) as exc_info:
        user_manager.create_superuser(email, None)
    assert str(exc_info.value) == "Superusers must have a password."


@pytest.mark.django_db
def test_user_model_fields():
    email = "user@example.com"
    role = User.Role.USER

    user = User.objects.create(email=email, role=role)

    assert user.email == email
    assert user.role == role
    assert user.first_login_completed is False
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_user_model_invalid_email():
    class UserForm(ModelForm):
        class Meta:
            model = User
            fields = ["email"]

    user_form = UserForm(data={"email": "invalid-email"})
    assert not user_form.is_valid()
    assert type(user_form.errors.get("email").data[0]) == ValidationError


@pytest.mark.django_db
def test_user_model_authentication():
    @login_required
    def dummy_view(request):
        return HttpResponse("test")

    factory = RequestFactory()

    # Unauthenticated
    request = factory.get("/something")
    request.user = AnonymousUser()
    response = dummy_view(request)
    # Redirect to login page
    assert response.status_code == HTTPStatus.FOUND
    assert reverse(settings.LOGIN_URL) in response.url

    # Authenticated
    email = "user@example.com"
    password = "userpass"
    user = User.objects.create(email=email, role=User.Role.USER)
    user.set_password(password)
    user.save()
    request = factory.get("/something")
    request.user = user
    response = dummy_view(request)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_user_model_authorization_checks():
    admin = UserFactory.create(role=User.Role.ADMIN)
    user = UserFactory.create(role=User.Role.USER)

    assert admin.is_admin()
    assert user.is_user()
    assert not admin.is_user()
    assert not user.is_admin()
