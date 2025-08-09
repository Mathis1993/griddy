import base64

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


class TrackCreation(models.Model):
    """
    Abstract model that tracks the creation date of a model instance.
    """

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TrackUpdates(models.Model):
    """
    Abstract model that tracks the last update date of a model instance.
    """

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TrackCreationAndUpdates(TrackCreation, TrackUpdates):
    """
    Abstract model that tracks the creation and last update date of a model instance.
    """

    class Meta:
        abstract = True


class EncodePkMixin:
    """
    Mixin that encodes/decodes the primary key of a model instance to/from an encrypted string.
    """

    cipher_suite = Fernet(settings.FERNET_KEY)

    def encode_pk(self) -> str:
        # Convert the primary key to a string and encode it to bytes
        pk_bytes = str(self.pk).encode("utf-8")
        # Encrypt the primary key
        encrypted_pk = self.cipher_suite.encrypt(pk_bytes)
        # Return the base64 encoded string of the encrypted primary key
        return base64.urlsafe_b64encode(encrypted_pk).decode("utf-8")

    @classmethod
    def decode_pk(cls, encrypted_str: str) -> int:
        # Decode the base64 encoded string to bytes
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_str.encode("utf-8"))
        # Decrypt the primary key
        decrypted_pk = cls.cipher_suite.decrypt(encrypted_bytes)
        # Convert the decrypted primary key back to an integer
        return int(decrypted_pk.decode("utf-8"))
