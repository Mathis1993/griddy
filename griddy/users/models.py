from __future__ import annotations

from core.models import TrackCreationAndUpdates
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user model manager that is used for the `User` model.
    """

    def create_superuser(self, email: str, password: str) -> User:
        """
        Create and save a superuser with the given email and password.
        Sets the user's role to `User.Role.ADMIN` and the
        `first_login_completed` flag to `True`.

        Parameters
        ----------
        email: str
        password: str

        Returns
        -------
        User
            The created superuser.
        """
        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.model(email=email)
        user.set_password(password)
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.first_login_completed = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin, TrackCreationAndUpdates):
    """
    This is the custom user model that is used for the project.
    It represents a user of the application.
    The users can have one of three roles: `ADMIN`, `COUNSELOR` or `CLIENT`.
    """

    class Meta:
        db_table = "users_users"

    class Role(models.TextChoices):
        ADMIN = "admin"
        USER = "user"

    first_name = models.CharField(max_length=255, null=True, default=None)
    last_name = models.CharField(max_length=255, null=True, default=None)
    email = models.EmailField(db_index=True, unique=True, max_length=255)
    role = models.CharField(choices=Role.choices, max_length=255, default=Role.USER)
    first_login_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site
    is_staff = models.BooleanField(default=False)

    # The `USERNAME_FIELD` property tells us which field we will use to log in
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    # The BaseUserManager contains a "get_by_natural_key" method using the
    # `USERNAME_FIELD` property during authentication
    objects = UserManager()

    def is_admin(self) -> bool:
        """
        Used as authorization check.
        """
        return self.role == User.Role.ADMIN

    def is_user(self) -> bool:
        """
        Used as authorization check.
        """
        return self.role == User.Role.USER

    @property
    def initials(self):
        try:
            return self.first_name[0] + self.last_name[0]
        except (KeyError, TypeError):
            return ""

