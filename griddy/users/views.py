from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import TemplateView, UpdateView
from users.forms import UserEmailForm, UserSignUpForm

User = get_user_model()


@login_required(login_url="users:login")
def index(request: HttpRequest) -> HttpResponse:
    """
    This view redirects the user to the appropriate page after login.
    If the user is an admin, they are redirected to django's admin interface.
    If the user is a user, they are redirected to the home page.

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------
    HttpResponse
        Redirects to the appropriate page.
    """
    user = request.user
    if user.is_admin():
        return redirect("admin:index")

    if user.is_user():
        return redirect("devices:dashboard")


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "users/home.html"


class PasswordUpdateView(LoginRequiredMixin, PasswordChangeView):
    """
    This view handles the changing of passwords.
    """

    form_class = PasswordChangeForm
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:index")

    def form_valid(self, form: PasswordChangeForm) -> HttpResponse:
        """
        If the submitted form is valid, set the `first_login_completed` flag to `True`,
        because the user now has chosen their own password.

        Parameters
        ----------
        form: PasswordChangeForm

        Returns
        -------
        HttpResponse
            Redirects to the index url for the user role.
        """
        response = super().form_valid(form)

        user = self.request.user
        user.first_login_completed = True
        user.save()

        return response


class ProfilePageView(LoginRequiredMixin, TemplateView):
    """
    This view handles the profile page of users.
    """

    template_name = "users/profile.html"


class EmailUpdateView(LoginRequiredMixin, UpdateView):
    """
    This view handles the updating of the email address of users.
    """

    model = User
    form_class = UserEmailForm
    template_name = "users/email_update.html"
    success_url = reverse_lazy("users:index")


class SignUpView(generic.CreateView):
    form_class = UserSignUpForm
    success_url = reverse_lazy("users:login")
    template_name = "users/signup.html"
