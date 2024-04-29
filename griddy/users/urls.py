"""
URL patterns for the users app.
"""

from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.urls import path, reverse_lazy
from users import views

app_name = "users"

urlpatterns = [
    path("index/", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),
    path("profile/", views.ProfilePageView.as_view(), name="profile"),
    path("change_password/", views.PasswordUpdateView.as_view(), name="change_password"),
    path("<int:pk>/change_email/", views.EmailUpdateView.as_view(), name="change_email"),
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            email_template_name="users/password_reset_email.html",
            from_email=settings.FROM_EMAIL,
            template_name="users/password_reset.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="reset_password",
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            form_class=SetPasswordForm,
            success_url=reverse_lazy("users:login"),
        ),
        name="password_reset_confirm",
    ),
]
