import json

from django import forms
from django.db import models

STYLED_FORM_CLASSES = "py-2.5 px-4 block w-full border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-0 dark:bg-neutral-900 dark:border-gray-700 dark:text-neutral-400 dark:placeholder-neutral-500 dark:focus:border-blue-500"


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
