import http

import pytest
from core.views import AuthenticatedAdminRoleMixin, AuthenticatedUserRoleMixin
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory
from django.urls import reverse
from django.views import View
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_authenticated_admin_role_mixin(django_user_model):
    class MyView(AuthenticatedAdminRoleMixin, View):
        def get(self, request):
            return "ok"

    view = MyView.as_view()
    request = RequestFactory().get("/")

    # Unauthenticated user
    request.user = AnonymousUser()

    response = view(request)

    assert response.status_code == http.HTTPStatus.FOUND
    assert reverse(settings.LOGIN_URL) in response.url

    # user user
    user_user = UserFactory.create(role=django_user_model.Role.USER)
    request.user = user_user

    with pytest.raises(PermissionDenied):
        view(request)

    # admin user
    admin_user = UserFactory.create(role=django_user_model.Role.ADMIN)
    request.user = admin_user

    response = view(request)

    assert response == "ok"


@pytest.mark.django_db
def test_authenticated_user_role_mixin(django_user_model):
    class MyView(AuthenticatedUserRoleMixin, View):
        def get(self, request):
            return "ok"

    view = MyView.as_view()
    request = RequestFactory().get("/")

    # Unauthenticated user
    request.user = AnonymousUser()

    response = view(request)

    assert response.status_code == http.HTTPStatus.FOUND
    assert reverse(settings.LOGIN_URL) in response.url

    # admin user
    admin = UserFactory.create(role=django_user_model.Role.ADMIN)
    request.user = admin

    with pytest.raises(PermissionDenied):
        view(request)

    # user user
    user_user = UserFactory.create(role=django_user_model.Role.USER)
    request.user = user_user

    response = view(request)

    assert response == "ok"
