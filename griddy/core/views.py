from django.contrib.auth.mixins import AccessMixin
from django.http import HttpRequest


class AuthenticatedAdminRoleMixin(AccessMixin):
    """
    Mixin to restrict access to admin users.
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not (user := request.user).is_authenticated or not user.is_admin():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AuthenticatedUserRoleMixin(AccessMixin):
    """
    Mixin to restrict access to regular users.
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not (user := request.user).is_authenticated or not user.is_user():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
