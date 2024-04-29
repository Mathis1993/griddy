from django import forms

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import BaseUserCreationForm

User = get_user_model()

class FormWithUIClassMixin:
    """
    Mixin for forms that adds the class "form-control" to all fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [
            self.fields[field].widget.attrs.update({"class": "form-control"})
            for field in self.fields.keys()
        ]


class UserSignUpForm(FormWithUIClassMixin, BaseUserCreationForm):

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


class UserEmailForm(FormWithUIClassMixin, forms.ModelForm):
    """
    A form for updating a user's email address.
    """

    class Meta:
        model = User
        fields = [
            "email",
        ]
