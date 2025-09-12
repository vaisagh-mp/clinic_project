from django.urls import path
from . import views

app_name = "clinic_panel"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
]
