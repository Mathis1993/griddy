from django import forms
from django.urls import reverse_lazy

from electricity_rates.models import BasicInput


class BasicInputForm(forms.ModelForm):
    class Meta:
        model = BasicInput
        fields = "__all__"

    def __init__(self, ):
        super().__init__()
        self.fields["zip_code"].widget.attrs.update(
            {"hx-get": f"{reverse_lazy("electricity_rates:expand_input")}"
                       f"?expand_type=network_operator"})

    # ToDo(ME-16.11.24): Add htmx stuff for network operator selection
    zip_code = forms.CharField(label="PLZ", required=True, widget=forms.TextInput(attrs={
        "hx-trigger": "keyup changed delay:1000ms",
        "hx-target": "#network-operators-container",
    }))
