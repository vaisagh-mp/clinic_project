from django.urls import path
from .views import (DoctorDashboardAPIView,
    ConsultationListCreateAPIView, ConsultationRetrieveUpdateDeleteAPIView,
    PrescriptionListCreateAPIView, PrescriptionRetrieveUpdateDeleteAPIView, DoctorAllAppointmentsAPIView, DoctorPrescriptionListAPIView, DoctorPrescriptionDetailAPIView, DoctorAppointmentDetailAPIView, DoctorScheduledAppointmentsAPIView
)

app_name = "doctor_panel"

urlpatterns = [

    path("dashboard/", DoctorDashboardAPIView.as_view(), name="doctor-dashboard"),
    path("dashboard/<int:doctor_id>/", DoctorDashboardAPIView.as_view(), name="doctor-dashboard-with-id"),

    path("appointments/",DoctorAllAppointmentsAPIView.as_view(), name="doctor-all-appointments"),
    path("appointments/scheduled/", DoctorScheduledAppointmentsAPIView.as_view(), name="doctor-scheduled-appointments"),
    path("appointments/<int:pk>/", DoctorAppointmentDetailAPIView.as_view(), name="doctor-appointment-detail"),

    # Consultations
    path("consultations/", ConsultationListCreateAPIView.as_view(), name="doctor-consultation-list-create"),
    path("consultations/<int:pk>/", ConsultationRetrieveUpdateDeleteAPIView.as_view(), name="doctor-consultation-detail"),

    # Prescriptions (nested under consultation)
    path("consultations/<int:consultation_id>/prescriptions/", PrescriptionListCreateAPIView.as_view(), name="doctor-prescription-list-create"),
    path("consultations/<int:consultation_id>/prescriptions/<int:pk>/", PrescriptionRetrieveUpdateDeleteAPIView.as_view(), name="doctor-prescription-detail"),

    path("prescriptions/", DoctorPrescriptionListAPIView.as_view(), name="doctor-prescription-list"),
    path("prescriptions/<int:pk>/", DoctorPrescriptionDetailAPIView.as_view(), name="doctor-prescription-detail"),
    

]
