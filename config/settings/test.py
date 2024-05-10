"""
Django settings for a test environment.
"""

from .base import *  # noqa: F401 F403

SECRET_KEY = SECRET_KEY or "simpletestsecret"  # noqa: F405

TEST_USER_PASSWORD = "password1"

# python manage.py runserver 0.0.0.0:8000 and local machine's host name in ALLOWED_HOSTS
# to connect from phone via host-name:8000/...
ALLOWED_HOSTS = ["localhost", "baby-yoda"]

# FROM_EMAIL = "test@test.de"

# Smartthings API (replace with actual values to record vcr cassettes)
TEST_SMARTTHINGS_API_TOKEN = "test_token"
TEST_SMARTTHINGS_DEVICE_ID = "test_device_id"
