from django.urls import path
from .views import *

urlpatterns = [

    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    
    # Clinics
    path("clinics/", ClinicListCreateAPIView.as_view(), name="clinic-list-create"),
    path("clinics/<int:pk>/", ClinicRetrieveUpdateDeleteAPIView.as_view(), name="clinic-rud"),

    # Doctors
    path("doctors/", DoctorListCreateAPIView.as_view(), name="doctor-list-create"),
    path("doctors/<int:pk>/", DoctorRetrieveUpdateDeleteAPIView.as_view(), name="doctor-rud"),

    # Patients
    path("patients/", PatientListCreateAPIView.as_view(), name="patient-list-create"),
    path("patients/<int:pk>/", PatientRetrieveUpdateDeleteAPIView.as_view(), name="patient-rud"),

    # Appointments
    path("appointments/", AppointmentListCreateAPIView.as_view(), name="appointment-list-create"),
    path("appointments/<int:pk>/", AppointmentRetrieveUpdateDeleteAPIView.as_view(), name="appointment-rud"),
]
