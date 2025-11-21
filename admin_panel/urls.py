from django.urls import path
from .views import *
from clinic_panel.views import PatientHistoryView
app_name = "admin_panel"

urlpatterns = [

    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),

    path('switchable-users/', SwitchableUsersView.as_view(), name='switchable-users'),

    path('switch-panel/', switch_panel, name='switch_panel'),
    
    # Clinics
    path("clinics/", ClinicListCreateAPIView.as_view(), name="clinic-list-create"),
    path("clinics/<int:pk>/", ClinicRetrieveUpdateDeleteAPIView.as_view(), name="clinic-rud"),

    # Doctors
    path("doctors/", DoctorListCreateAPIView.as_view(), name="doctor-list-create"),
    path("doctors/<int:pk>/", DoctorRetrieveUpdateDeleteAPIView.as_view(), name="doctor-rud"),

    # Patients
    path("patients/", PatientListCreateAPIView.as_view(), name="patient-list-create"),
    path("patients/<int:pk>/", PatientRetrieveUpdateDeleteAPIView.as_view(), name="patient-rud"),
    path("patients/<int:id>/history/", PatientHistoryView.as_view(), name="patient-history"),

    # Appointments
    path("appointments/", AppointmentListCreateAPIView.as_view(), name="appointment-list-create"),
    path("appointments/<int:pk>/", AppointmentRetrieveUpdateDeleteAPIView.as_view(), name="appointment-rud"),

    path(
        "patient-vital-signs/",
        AdminPatientVitalSignsAPIView.as_view(),
        name="admin-patient-vital-signs",
    ),
]
