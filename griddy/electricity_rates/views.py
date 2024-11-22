from django.http import HttpResponse
from django.views.generic import FormView

from electricity_rates.forms import (
    FlowStep,
    NetworkOperatorForm,
    KilowattHourRateStaticForm,
    BasicFeeMonthlyStaticForm, KilowattHoursLastYearStaticForm, ElectricCarForm, ElectricCarKilowattHoursForm,
)
from electricity_rates.forms import ZipCodeForm


class ZipCodeView(FormView):
    template_name = "calculator.html"
    form_class = ZipCodeForm
    flow = {
        "zip_code": FlowStep(
            form_class=ZipCodeForm,
            template_name="zip_code.html",
            next=lambda _: "network_operator",
        ),
        "network_operator": FlowStep(
            form_class=NetworkOperatorForm,
            template_name="network_operator.html",
            next=lambda _: "basic_fee_monthly_static",
        ),
        "basic_fee_monthly_static": FlowStep(
            form_class=BasicFeeMonthlyStaticForm,
            template_name="basic_fee_monthly_static.html",
            next=lambda _: "kilowatt_hour_rate_static"
        ),
        "kilowatt_hour_rate_static": FlowStep(
            form_class=KilowattHourRateStaticForm,
            template_name="kilowatt_hour_rate_static.html",
            next=lambda _: "kilowatt_hours_last_year_static"
        ),
        "kilowatt_hours_last_year_static": FlowStep(
            form_class=KilowattHoursLastYearStaticForm,
            template_name="kilowatt_hours_last_year_static.html",
            next=lambda _: "electric_car",
        ),
        "electric_car": FlowStep(
            form_class=ElectricCarForm,
            template_name="electric_car.html",
            next=lambda responses: "electric_car_kilowatt_hours" if responses["electric_car"]["electric_car"] == "True" else None,
        ),
        "electric_car_kilowatt_hours": FlowStep(
            form_class=ElectricCarKilowattHoursForm,
            template_name="electric_car_kilowatt_hours.html",
        ),
    }

    def get(self, request, *args, **kwargs):
        # ToDo(ME-22.11.24): Handle full page reload somewhere during the form process
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "form_progress" not in self.request.session:
            self.request.session["form_progress"] = {
                "current_step": "zip_code",
                "responses": {}
            }

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
            return self.handle_completion()

        self.template_name = next_step.template_name
        self.form_class = next_step.form_class
        return self.render_to_response(self.get_context_data(form=self.form_class()))

    def get_current_step(self):
        return self.flow.get(self.get_current_step_key())

    def get_current_step_key(self):
        return self.request.session["form_progress"]["current_step"]

    def store_response(self, form):
        self.request.session["form_progress"]["responses"][self.get_current_step_key()] = form.to_dict()

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
        print(form_responses)
        del self.request.session["form_progress"]
        return HttpResponse("Form completed")
