from django.urls import path
from . import views

app_name = "doctor_panel"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
]
