from django.urls import path
from .views import (DoctorDashboardAPIView,
    ConsultationListCreateAPIView, ConsultationRetrieveUpdateDeleteAPIView,
    PrescriptionListCreateAPIView, PrescriptionRetrieveUpdateDeleteAPIView, DoctorAllAppointmentsAPIView, DoctorPrescriptionListAPIView, DoctorPrescriptionDetailAPIView
)

app_name = "doctor_panel"

urlpatterns = [

    path("dashboard/", DoctorDashboardAPIView.as_view(), name="doctor-dashboard"),

    path("appointments/",DoctorAllAppointmentsAPIView.as_view(), name="doctor-all-appointments"),
    # Consultations
    path("consultations/", ConsultationListCreateAPIView.as_view(), name="doctor-consultation-list-create"),
    path("consultations/<int:pk>/", ConsultationRetrieveUpdateDeleteAPIView.as_view(), name="doctor-consultation-detail"),

    # Prescriptions (nested under consultation)
    path("consultations/<int:consultation_id>/prescriptions/", PrescriptionListCreateAPIView.as_view(), name="doctor-prescription-list-create"),
    path("consultations/<int:consultation_id>/prescriptions/<int:pk>/", PrescriptionRetrieveUpdateDeleteAPIView.as_view(), name="doctor-prescription-detail"),

    path("prescriptions/", DoctorPrescriptionListAPIView.as_view(), name="doctor-prescription-list"),
    path("prescriptions/<int:pk>/", DoctorPrescriptionDetailAPIView.as_view(), name="doctor-prescription-detail"),

]
