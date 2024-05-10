"""
This file holds pytest fixtures that can be used across multiple subdirectories
to avoid code duplication.
"""

import pytest
from users.tests.factories import UserFactory


@pytest.fixture
def create_response(client):
    def _create_response(user, url, method="GET", data=None, content_type=None):
        client.force_login(user)
        if not content_type:
            response = getattr(client, method.lower())(url, data)
        else:
            response = getattr(client, method.lower())(url, data, content_type=content_type)
        return response

    return _create_response


@pytest.fixture
def user():
    return UserFactory.create()


@pytest.fixture
def vcr_config():
    return {"record_mode": "once"}
