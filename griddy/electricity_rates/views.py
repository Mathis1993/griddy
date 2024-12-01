from django.conf import settings
from django.contrib import messages
from django.utils.datastructures import MultiValueDict
from django.views.generic import FormView
from electricity_rates.calculator import Calculator
from electricity_rates.forms import (
    BasicFeeMonthlyStaticForm,
    ChargingFrequencyForm,
    ChargingSpecificWeekdaysForm,
    ChargingWeekdaysForm,
    ElectricCarExistsForm,
    ElectricCarForm,
    FlowStep,
    KilowattHourRateStaticForm,
    KilowattHoursLastYearStaticForm,
    NetworkOperatorForm,
    ZipCodeForm,
)
from electricity_rates.models import BasicInput, NetworkOperator, ZipCode


class ZipCodeView(FormView):
    template_name = "calculator.html"
    form_class = ZipCodeForm
    flow = {
        "zip_code": FlowStep(
            form_class=ZipCodeForm,
            template_name="zip_code.html",
            next=lambda responses: (
                "basic_fee_monthly_static"
                if ZipCode.objects.get(
                    zip_code=responses["zip_code"]["zip_code"]
                ).one_to_one_network_operator()
                else "network_operator"
            ),
        ),
        "network_operator": FlowStep(
            form_class=NetworkOperatorForm,
            template_name="network_operator.html",
            next=lambda _: "basic_fee_monthly_static",
        ),
        "basic_fee_monthly_static": FlowStep(
            form_class=BasicFeeMonthlyStaticForm,
            template_name="basic_fee_monthly_static.html",
            next=lambda _: "kilowatt_hour_rate_static",
        ),
        "kilowatt_hour_rate_static": FlowStep(
            form_class=KilowattHourRateStaticForm,
            template_name="kilowatt_hour_rate_static.html",
            next=lambda _: "kilowatt_hours_last_year_static",
        ),
        "kilowatt_hours_last_year_static": FlowStep(
            form_class=KilowattHoursLastYearStaticForm,
            template_name="kilowatt_hours_last_year_static.html",
            next=lambda _: "electric_car_exists",
        ),
        "electric_car_exists": FlowStep(
            form_class=ElectricCarExistsForm,
            template_name="electric_car_exists.html",
            next=lambda responses: (
                "electric_car"
                if responses["electric_car_exists"]["electric_car_exists"] == "True"
                else None
            ),
        ),
        # ToDo(ME-29.11.24): Option to add multiple electric cars
        "electric_car": FlowStep(
            form_class=ElectricCarForm,
            template_name="electric_car.html",
            next=lambda _: "charging_frequency",
        ),
        "charging_frequency": FlowStep(
            form_class=ChargingFrequencyForm,
            template_name="charging_frequency.html",
            next=lambda _: "charging_specific_weekdays",
        ),
        "charging_specific_weekdays": FlowStep(
            form_class=ChargingSpecificWeekdaysForm,
            template_name="charging_specific_weekdays.html",
            next=lambda responses: (
                "charging_weekdays"
                if responses["charging_specific_weekdays"]["charging_specific_weekdays"] == "True"
                else None
            ),
        ),
        "charging_weekdays": FlowStep(
            form_class=ChargingWeekdaysForm,
            template_name="charging_weekdays.html",
        ),
    }

    def get(self, request, *args, **kwargs):
        # ToDo(ME-22.11.24): Handle full page reload somewhere during the form process
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["previous_responses"] = self.request.session.get("form_progress", {}).get(
            "responses"
        )
        return form_kwargs

    def post(self, request, *args, **kwargs):
        if "form_progress" not in self.request.session:
            self.request.session["form_progress"] = {"current_step": "zip_code", "responses": {}}

        current_step = self.get_current_step()
        self.template_name = current_step.template_name
        self.form_class = current_step.form_class
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        self.store_response(form)
        next_step = self.get_next_step()
        if not next_step:
            result_data = self.handle_completion()
            self.template_name = "result.html"
            context = self.get_context_data()
            context["result"] = result_data.get("result")
            context["savings"] = result_data.get("savings")
            context["positive_savings"] = result_data.get("positive_savings")
            messages.add_message(
                self.request,
                (
                    settings.CONFETTI_MESSAGE_LEVEL
                    if context["positive_savings"]
                    else messages.SUCCESS
                ),
                "Dein Ergebnis wurde berechnet!",
            )
            return self.render_to_response(context)

        self.template_name = next_step.template_name
        self.form_class = next_step.form_class
        # get_form calls get_form_kwargs which for request.method == POST
        # sets the data attribute on the form leading it to be "bound",
        # triggering validation resulting in an error message because of course
        # the field the form consists of is empty (but probably required)
        form = self.get_form()
        form.is_bound = False
        return self.render_to_response(self.get_context_data(form=form))

    def get_current_step(self):
        return self.flow.get(self.get_current_step_key())

    def get_current_step_key(self):
        return self.request.session["form_progress"]["current_step"]

    def store_response(self, form):
        self.request.session["form_progress"]["responses"][
            self.get_current_step_key()
        ] = form.to_dict()

    def get_next_step(self):
        current_step = self.get_current_step()
        if not current_step.next:
            return None
        next_step = current_step.next(self.request.session["form_progress"]["responses"])
        if not next_step:
            return None
        self.request.session["form_progress"]["current_step"] = next_step
        # Necessary because of altering session["form_progress"] and not the session itself
        # (https://docs.djangoproject.com/en/5.1/topics/http/sessions/#when-sessions-are-saved)
        self.request.session.modified = True
        return self.flow.get(next_step)

    def handle_completion(self):
        form_responses = self.request.session["form_progress"]["responses"]
        result_data = self.process_form_responses(form_responses)
        del self.request.session["form_progress"]
        return result_data

    @staticmethod
    # ToDo(ME-22.11.24): Move logic somewhere else?
    def process_form_responses(form_responses):
        zip_code = form_responses["zip_code"]["zip_code"]
        zip_code = ZipCode.objects.get(zip_code=zip_code)
        network_operator_id = form_responses.get("network_operator", {}).get(
            "network_operator",
            (
                network_operator.id
                if (
                    network_operator := ZipCode.objects.get(
                        zip_code=zip_code
                    ).network_operators.first()
                )
                else None
            ),
        )
        electric_car_id = form_responses.get("electric_car", {}).get("electric_car")
        form_data = {
            "zip_code": zip_code,
            "network_operator_id": network_operator_id,
            "basic_fee_monthly_static": form_responses["basic_fee_monthly_static"][
                "basic_fee_monthly_static"
            ],
            "kilowatt_hour_rate_static": form_responses["kilowatt_hour_rate_static"][
                "kilowatt_hour_rate_static"
            ],
            "kilowatt_hours_last_year_static": form_responses["kilowatt_hours_last_year_static"][
                "kilowatt_hours_last_year_static"
            ],
            "electric_car_id": electric_car_id,
            "electric_car_charging_frequency": form_responses.get("charging_frequency", {}).get(
                "charging_frequency"
            ),
            "electric_car_charging_weekdays": form_responses.get("charging_weekdays", {}).get(
                "charging_weekdays"
            ),
        }
        basic_input = BasicInput(**form_data)
        basic_input.save()
        calculator = Calculator(basic_input=basic_input)
        result = calculator.calculate_costs()
        savings, positive_savings = result.potential_savings()
        return {
            "result": result,
            "savings": savings,
            "positive_savings": positive_savings,
        }
