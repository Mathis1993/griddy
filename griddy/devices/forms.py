from devices.models import Address
from devices.models.heat_pumps import DummyHeatPump, SmartthingsHeatPump
from django import forms


class AddressCreateForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["zip_code"]


class SmartthingsHeatPumpCreateForm(forms.ModelForm):
    class Meta:
        model = SmartthingsHeatPump
        fields = ["name"]


class DummyHeatPumpCreateForm(forms.ModelForm):
    class Meta:
        model = DummyHeatPump
        fields = ["name", "some_config_value"]
