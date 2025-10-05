from django.urls import path
from .views import *
app_name = "clinic_panel"

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

    #Prescriptions
    path("clinic/prescriptions/", ClinicPrescriptionListAPIView.as_view(), name="clinic-prescription-list"),
    path("clinic/prescriptions/<int:pk>/", ClinicPrescriptionDetailAPIView.as_view(), name="clinic-prescription-detail"),
]
