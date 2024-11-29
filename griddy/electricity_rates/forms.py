from dataclasses import dataclass
from typing import Callable, Optional, Type, Union

from core.forms import (
    CustomChoiceField,
    CustomSelectWidget,
    JsonSerializableForm,
    JsonSerializableModelForm,
    PreviousResponsesMixin,
    StyledCharField,
    StyledIntegerField,
)
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from electric_cars.models import Car
from electricity_rates.models import NetworkOperator, ZipCode


@dataclass
class FlowStep:
    form_class: Union[Type[JsonSerializableForm], Type[JsonSerializableModelForm]]
    template_name: str
    next: Optional[Callable[[dict], str]] = None


class JsonSerializablePreviousResponsesForm(PreviousResponsesMixin, JsonSerializableForm):
    pass


class ZipCodeForm(JsonSerializablePreviousResponsesForm):
    zip_code = StyledCharField(
        label="Wie lautet deine PLZ?", min_length=5, max_length=5, required=True
    )

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get("zip_code")
        try:
            ZipCode.objects.get(zip_code=zip_code)
        except ObjectDoesNotExist:
            raise forms.ValidationError(f"Unbekannte PLZ: {zip_code}")
        return zip_code


class NetworkOperatorForm(JsonSerializablePreviousResponsesForm):
    class Meta:
        model = NetworkOperator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.previous_responses:
            zip_code = self.previous_responses.get("zip_code", {}).get("zip_code")
            self.fields["network_operator"].queryset = NetworkOperator.objects.filter(
                zip_code__zip_code=zip_code
            )

    network_operator = forms.ModelChoiceField(
        queryset=NetworkOperator.objects.none(),
        label="Netzbetreiber",
        required=True,
        widget=CustomSelectWidget,
    )
    network_operator.widget.attrs.update(
        {
            "placeholder": "Wer ist dein Netzbetreiber?",
        }
    )


class BasicFeeMonthlyStaticForm(JsonSerializablePreviousResponsesForm):
    basic_fee_monthly_static = StyledIntegerField(
        label="Aktuelle monatliche Grundgebühr in Euro", required=True
    )


class KilowattHourRateStaticForm(JsonSerializablePreviousResponsesForm):
    kilowatt_hour_rate_static = StyledIntegerField(
        label="Aktueller Preis pro kWh in Cent", required=True
    )


class KilowattHoursLastYearStaticForm(JsonSerializablePreviousResponsesForm):
    kilowatt_hours_last_year_static = StyledIntegerField(
        label="Verbrauch in kWh der letzten 12 Monate", required=True
    )


class ElectricCarExistsForm(JsonSerializablePreviousResponsesForm):
    electric_car_exists = CustomChoiceField(
        label="Elektroauto vorhanden?", required=True, choices=((True, "Ja"), (False, "Nein"))
    )


class ElectricCarForm(JsonSerializablePreviousResponsesForm):
    electric_car = forms.ModelChoiceField(
        queryset=Car.objects.all(),
        label="Elektroauto",
        required=True,
        widget=CustomSelectWidget,
    )
    electric_car.widget.attrs.update(
        {
            "placeholder": "Was für ein Elektroauto hast du?",
        }
    )
