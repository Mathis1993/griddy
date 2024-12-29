from dataclasses import dataclass
from typing import Callable, Optional, Type, Union

from core.forms import (
    CustomChoiceField,
    CustomMultipleSelectWidget,
    CustomSelectWidget,
    JsonSerializableForm,
    JsonSerializableModelForm,
    PreviousResponsesMixin,
    StyledCharField,
    StyledIntegerField,
)
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from electric_cars.models import Car
from electricity_rates.constants import (
    HELP_TEXT_BASIC_FEE_MONTHLY_STATIC,
    HELP_TEXT_BATTERY_EXISTS,
    HELP_TEXT_CHARGING_FREQUENCY,
    HELP_TEXT_CHARGING_SPECIFIC_WEEKDAYS,
    HELP_TEXT_CHARGING_WEEKDAYS,
    HELP_TEXT_CHARGING_WITH_SOLAR_POWER,
    HELP_TEXT_ELECTRIC_CAR,
    HELP_TEXT_ELECTRIC_CAR_EXISTS,
    HELP_TEXT_KILOWATT_HOUR_RATE_STATIC,
    HELP_TEXT_KILOWATT_HOURS_LAST_YEAR_STATIC,
    HELP_TEXT_NETWORK_OPERATOR,
    HELP_TEXT_SOLAR_SYSTEM_EXISTS,
    HELP_TEXT_ZIP_CODE,
)
from electricity_rates.models import NetworkOperator, ZipCode


@dataclass
class FlowStep:
    form_class: Union[Type[JsonSerializableForm], Type[JsonSerializableModelForm]]
    template_name: str
    next: Optional[Callable[[dict], str]] = None
    number: int = 1


class JsonSerializablePreviousResponsesForm(PreviousResponsesMixin, JsonSerializableForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.set_initial_value(field_name)

    def set_initial_value(self, field_name: str):
        if self.previous_responses:
            initial_value = self.previous_responses.get(field_name, {}).get(field_name)
            self.fields[field_name].initial = initial_value


class ZipCodeForm(JsonSerializablePreviousResponsesForm):
    zip_code = StyledCharField(
        label="Wie lautet deine PLZ?",
        placeholder="PLZ",
        min_length=5,
        max_length=5,
        required=True,
    )
    zip_code.help_text = HELP_TEXT_ZIP_CODE

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
            network_operators = ZipCode.objects.get(zip_code=zip_code).network_operators.all()
            self.fields["network_operator"].queryset = (
                network_operators if network_operators.exists() else NetworkOperator.objects.all()
            )

    network_operator = forms.ModelChoiceField(
        queryset=NetworkOperator.objects.none(),
        label="Wer ist dein Netzbetreiber?",
        required=True,
        widget=CustomSelectWidget,
    )
    network_operator.help_text = HELP_TEXT_NETWORK_OPERATOR
    network_operator.widget.attrs.update(
        {
            "placeholder": "Auswählen...",
        }
    )


class BasicFeeMonthlyStaticForm(JsonSerializablePreviousResponsesForm):
    basic_fee_monthly_static = StyledIntegerField(
        label="Wie hoch ist deine aktuelle monatliche Grundgebühr (in Euro)?",
        placeholder="€",
        required=True,
    )
    basic_fee_monthly_static.help_text = HELP_TEXT_BASIC_FEE_MONTHLY_STATIC


class KilowattHourRateStaticForm(JsonSerializablePreviousResponsesForm):
    kilowatt_hour_rate_static = StyledIntegerField(
        label="Aktueller Preis pro kWh in Cent", placeholder="ct", required=True
    )
    kilowatt_hour_rate_static.help_text = HELP_TEXT_KILOWATT_HOUR_RATE_STATIC


class KilowattHoursLastYearStaticForm(JsonSerializablePreviousResponsesForm):
    kilowatt_hours_last_year_static = StyledIntegerField(
        label="Verbrauch in kWh der letzten 12 Monate", placeholder="kWh", required=True
    )
    kilowatt_hours_last_year_static.help_text = HELP_TEXT_KILOWATT_HOURS_LAST_YEAR_STATIC


class ElectricCarExistsForm(JsonSerializablePreviousResponsesForm):
    electric_car_exists = CustomChoiceField(
        label="Hast du ein Elektroauto?", required=True, choices=((True, "Ja"), (False, "Nein"))
    )
    electric_car_exists.help_text = HELP_TEXT_ELECTRIC_CAR_EXISTS


class ElectricCarForm(JsonSerializablePreviousResponsesForm):
    electric_car = forms.ModelChoiceField(
        queryset=Car.objects.all(),
        label="Welches Elektroauto hast du?",
        required=True,
        widget=CustomSelectWidget,
    )
    electric_car.help_text = HELP_TEXT_ELECTRIC_CAR
    electric_car.widget.attrs.update(
        {
            "placeholder": "Auswählen...",
        }
    )


class ChargingFrequencyForm(JsonSerializablePreviousResponsesForm):
    # ToDo(ME-04.12.24): Check if electric_car_kilowatt_hours is an abnormally big amount of or even more than the total kilowatt_hours_last_year_static
    charging_frequency = StyledIntegerField(
        label="Wie häufig lädst du dein Auto im Schnitt pro Monat zuhause?",
        placeholder="Häufigkeit",
        required=True,
    )
    charging_frequency.help_text = HELP_TEXT_CHARGING_FREQUENCY


class ChargingSpecificWeekdaysForm(JsonSerializablePreviousResponsesForm):
    charging_specific_weekdays = CustomChoiceField(
        label="Lädst du dein Auto in der Regel an bestimmten Wochentagen?",
        required=True,
        choices=((True, "Ja"), (False, "Nein")),
    )
    charging_specific_weekdays.help_text = HELP_TEXT_CHARGING_SPECIFIC_WEEKDAYS


class ChargingWeekdaysForm(JsonSerializablePreviousResponsesForm):
    charging_weekdays = forms.MultipleChoiceField(
        label="Welche Wochentage sind das?",
        required=True,
        choices=(
            ("monday", "Montag"),
            ("tuesday", "Dienstag"),
            ("wednesday", "Mittwoch"),
            ("thursday", "Donnerstag"),
            ("friday", "Freitag"),
            ("saturday", "Samstag"),
            ("sunday", "Sonntag"),
        ),
        widget=CustomMultipleSelectWidget,
    )
    charging_weekdays.help_text = HELP_TEXT_CHARGING_WEEKDAYS
    charging_weekdays.widget.attrs.update(
        {
            "placeholder": "Auswählen...",
        }
    )

    def clean_charging_weekdays(self):
        weekdays = self.cleaned_data["charging_weekdays"]
        return ",".join(weekdays) if weekdays else None


class SolarSystemExistsForm(JsonSerializablePreviousResponsesForm):
    solar_system_exists = CustomChoiceField(
        label="Hast du eine Solaranlage?", required=True, choices=((True, "Ja"), (False, "Nein"))
    )
    solar_system_exists.help_text = HELP_TEXT_SOLAR_SYSTEM_EXISTS


class ChargingWithSolarPowerForm(JsonSerializablePreviousResponsesForm):
    charging_with_solar_power = CustomChoiceField(
        label="Lädst du dein Auto im Sommer hauptsächlich mit Solarstrom?",
        required=True,
        choices=((True, "Ja"), (False, "Nein")),
    )
    charging_with_solar_power.help_text = HELP_TEXT_CHARGING_WITH_SOLAR_POWER


class BatteryExistsForm(JsonSerializablePreviousResponsesForm):
    battery_exists = CustomChoiceField(
        label="Hast du einen Stromspeicher?", required=True, choices=((True, "Ja"), (False, "Nein"))
    )
    battery_exists.help_text = HELP_TEXT_BATTERY_EXISTS
