from django.urls import path
from .views import (ClinicDashboardAPIView,
    DoctorListCreateAPIView, DoctorRetrieveUpdateDeleteAPIView,
    PatientListCreateAPIView, PatientRetrieveUpdateDeleteAPIView,
    AppointmentListCreateAPIView, AppointmentRetrieveUpdateDeleteAPIView
)

urlpatterns = [

    path("dashboard/", ClinicDashboardAPIView.as_view(), name="clinic-dashboard"),

    # Doctors
    path("doctors/", DoctorListCreateAPIView.as_view(), name="clinic-doctor-list-create"),
    path("doctors/<int:pk>/", DoctorRetrieveUpdateDeleteAPIView.as_view(), name="clinic-doctor-detail"),

    # Patients
    path("patients/", PatientListCreateAPIView.as_view(), name="clinic-patient-list-create"),
    path("patients/<int:pk>/", PatientRetrieveUpdateDeleteAPIView.as_view(), name="clinic-patient-detail"),

    # Appointments
    path("appointments/", AppointmentListCreateAPIView.as_view(), name="clinic-appointment-list-create"),
    path("appointments/<int:pk>/", AppointmentRetrieveUpdateDeleteAPIView.as_view(), name="clinic-appointment-detail"),
]
