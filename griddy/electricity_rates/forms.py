from dataclasses import dataclass
from typing import Type, Union, Optional, Callable

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from core.forms import JsonSerializableForm, JsonSerializableModelForm, StyledCharField, StyledIntegerField, \
    CustomSelectWidget, CustomChoiceField
from electricity_rates.models import ZipCode, NetworkOperator


@dataclass
class FlowStep:
    form_class: Union[Type[JsonSerializableForm], Type[JsonSerializableModelForm]]
    template_name: str
    next: Optional[Callable[[dict], str]] = None


class ZipCodeForm(JsonSerializableForm):
    zip_code = StyledCharField(label="Wie lautet deine PLZ?", min_length=5, max_length=5, required=True)

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get("zip_code")
        try:
            ZipCode.objects.get(zip_code=zip_code)
        except ObjectDoesNotExist:
            raise forms.ValidationError(f"Unbekannte PLZ: {zip_code}")
        return zip_code


class NetworkOperatorForm(JsonSerializableForm):
    network_operator = forms.ModelChoiceField(
        queryset=NetworkOperator.objects.all(),
        label="Netzbetreiber",
        required=True,
        widget=CustomSelectWidget,
    )
    network_operator.widget.attrs.update(
        {
            "placeholder": "Wer ist dein Netzbetreiber?",
        }
    )


class BasicFeeMonthlyStaticForm(JsonSerializableForm):
    basic_fee_monthly_static = StyledIntegerField(label="Aktuelle monatliche Grundgebühr in Euro", required=True)


class KilowattHourRateStaticForm(JsonSerializableForm):
    kilowatt_hour_rate_static = StyledIntegerField(label="Aktueller Preis pro kWh in Cent", required=True)


class KilowattHoursLastYearStaticForm(JsonSerializableForm):
    kilowatt_hours_last_year_static = StyledIntegerField(label="Verbrauch in kWh der letzten 12 Monate", required=True)


class ElectricCarForm(JsonSerializableForm):
    electric_car = CustomChoiceField(label="Elektroauto vorhanden?", required=True,
                                     choices=((True, "Ja"), (False, "Nein")))


class ElectricCarKilowattHoursForm(JsonSerializableForm):
    electric_car_kilowatt_hours = StyledIntegerField(label="Kapazität der Autobatterie in kWh", required=True)
