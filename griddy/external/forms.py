from django import forms
from external.models import ApiKey


class ApiKeyCreateForm(forms.ModelForm):
    class Meta:
        model = ApiKey
        fields = ["key"]
