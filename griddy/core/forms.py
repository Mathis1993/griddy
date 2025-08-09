import json

from django import forms
from django.db import models

STYLED_FORM_CLASSES = "w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-white backdrop-blur-sm focus:border-green-500 !focus:outline-none focus:ring-2 focus:ring-green-500/20 placeholder:text-white/50 [&:focus]:border-green-500 [&:focus]:outline-none [&:focus]:ring-green-500/20"


class JsonSerializableForm(forms.Form):
    def to_json(self):
        raise json.dumps(self.to_dict())

    def to_dict(self):
        dict_data = {
            field: (
                self.cleaned_data[field]
                if not isinstance(self.cleaned_data[field], models.Model)
                else self.cleaned_data[field].pk
            )
            for field in self.cleaned_data
        }
        return dict_data


class JsonSerializableModelForm(forms.ModelForm):
    def to_json(self):
        raise json.dumps(self.to_dict())

    def to_dict(self):
        dict_data = {
            field: (
                self.cleaned_data[field]
                if not isinstance(self.cleaned_data[field], models.Model)
                else self.cleaned_data[field].pk
            )
            for field in self.cleaned_data
        }
        return dict_data


class PreviousResponsesMixin:
    def __init__(self, *args, **kwargs):
        self.previous_responses = kwargs.pop("previous_responses", {})
        super().__init__(*args, **kwargs)


class StyledFieldMixin:
    def __init__(self, *args, **kwargs):
        placeholder = kwargs.pop("placeholder", "")
        super().__init__(*args, **kwargs)
        self.widget.attrs.update(
            {
                "class": STYLED_FORM_CLASSES,
                "placeholder": placeholder,
            }
        )


class StyledCharField(StyledFieldMixin, forms.CharField):
    pass


class StyledIntegerField(StyledFieldMixin, forms.IntegerField):
    pass


class StyledBooleanField(StyledFieldMixin, forms.BooleanField):
    pass


class CustomSelectWidget(forms.Select):
    template_name = "widgets/select.html"
    option_template_name = "widgets/select_option.html"


class CustomMultipleSelectWidget(forms.SelectMultiple):
    template_name = "widgets/select_multiple.html"
    option_template_name = "widgets/select_option.html"


class CustomCheckBoxWidget(forms.CheckboxInput):
    template_name = "widgets/checkbox.html"


class CustomChoiceField(forms.ChoiceField):
    widget = CustomCheckBoxWidget
