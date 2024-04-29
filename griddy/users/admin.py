from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

admin.site.register(User)
# ... And, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
