from devices import views
from django.urls import path

app_name = "devices"

urlpatterns = [
    path(
        "heat_pumps/integrations/",
        views.HeatPumpIntegrationsListView.as_view(),
        name="list_heat_pump_integrations",
    ),
    path(
        "heat_pumps/<int:integration_id>/create",
        views.HeatPumpCreateView.as_view(),
        name="create_heat_pump",
    ),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
]
