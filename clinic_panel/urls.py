from django.urls import path
from .views import *
app_name = "clinic_panel"

urlpatterns = [

    path("dashboard/", ClinicDashboardAPIView.as_view(), name="clinic-dashboard"),
    path("dashboard/<int:clinic_id>/", ClinicDashboardAPIView.as_view(), name="clinic-dashboard-with-id"),

    # Doctors
    # path("doctors/", DoctorListCreateAPIView.as_view(), name="clinic-doctor-list-create"),
    # path("doctors/<int:clinic_id>/", DoctorListCreateAPIView.as_view(), name="clinic-doctor-list-create-by-id"),
    # path("doctors/<int:pk>/", DoctorRetrieveUpdateDeleteAPIView.as_view(), name="clinic-doctor-detail"),
    # path("doctors/<int:clinic_id>/<int:pk>/", DoctorRetrieveUpdateDeleteAPIView.as_view(), name="clinic-doctor-detail-by-id"),

    path("doctors/", DoctorListCreateAPIView.as_view(), name="doctor-list-create"),
    path("doctors/<int:clinic_id>/", DoctorListCreateAPIView.as_view(), name="doctor-list-by-clinic"),
    path("doctors/<int:pk>/", DoctorRetrieveUpdateDeleteAPIView.as_view(), name="doctor-detail"),
    path("doctors/<int:clinic_id>/<int:pk>/", DoctorRetrieveUpdateDeleteAPIView.as_view(), name="doctor-detail-by-clinic"),
    # Patients
    path("patients/", PatientListCreateAPIView.as_view(), name="clinic-patient-list-create"),
    path("patients/<int:pk>/", PatientRetrieveUpdateDeleteAPIView.as_view(), name="clinic-patient-detail"),

    # Appointments
    path("appointments/", AppointmentListCreateAPIView.as_view(), name="clinic-appointment-list-create"),
    path("appointments/<int:pk>/", AppointmentRetrieveUpdateDeleteAPIView.as_view(), name="clinic-appointment-detail"),

    path("consultations/", ClinicConsultationListAPIView.as_view(), name="clinic-consultations"),

    #Prescriptions
    path("prescriptions/", ClinicPrescriptionListAPIView.as_view(), name="clinic-prescription-list"),
    path("prescriptions/<int:pk>/", ClinicPrescriptionDetailAPIView.as_view(), name="clinic-prescription-detail"),
]
