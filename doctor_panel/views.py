from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from clinic_panel.models import Appointment, Patient
from .models import Consultation, Prescription
from .serializers import ConsultationSerializer, PrescriptionSerializer


class DoctorDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doctor = request.user.doctor_profile

        # Total consultations for this doctor
        total_consultations = Consultation.objects.filter(doctor=doctor).count()

        # Total unique patients
        total_patients = Patient.objects.filter(appointments__doctor=doctor).distinct().count()

        # Total prescriptions
        total_prescriptions = Prescription.objects.filter(consultation__doctor=doctor).count()

        # Upcoming appointments (next 7 days)
        today = timezone.now().date()
        upcoming_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=today,
            appointment_date__lte=today + timezone.timedelta(days=7),
            status="SCHEDULED"
        ).order_by("appointment_date", "appointment_time")

        upcoming_appointments_data = [
            {
                "id": appt.id,
                "appointment_id": appt.appointment_id,
                "patient_name": f"{appt.patient.first_name} {appt.patient.last_name}",
                "appointment_date": appt.appointment_date,
                "appointment_time": appt.appointment_time,
                "status": appt.status,
            }
            for appt in upcoming_appointments
        ]

        data = {
            "total_consultations": total_consultations,
            "total_patients": total_patients,
            "total_prescriptions": total_prescriptions,
            "upcoming_appointments": upcoming_appointments_data
        }

        return Response(data)

# -------------------- Consultation --------------------
class ConsultationListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doctor = request.user.doctor_profile  # logged-in doctor
        consultations = Consultation.objects.filter(doctor=doctor).select_related("patient", "doctor", "appointment")
        serializer = ConsultationSerializer(consultations, many=True)
        return Response(serializer.data)

    def post(self, request):
        doctor = request.user.doctor_profile
        patient_id = request.data.get("patient")
        appointment_id = request.data.get("appointment")

        patient = get_object_or_404(Patient, id=patient_id, clinic=doctor.clinic)
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

        serializer = ConsultationSerializer(data=request.data)
        if serializer.is_valid():
            consultation = serializer.save(doctor=doctor, patient=patient, appointment=appointment)
            return Response(ConsultationSerializer(consultation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsultationRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, pk=pk, doctor=doctor)
        serializer = ConsultationSerializer(consultation)
        return Response(serializer.data)

    def put(self, request, pk):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, pk=pk, doctor=doctor)
        serializer = ConsultationSerializer(consultation, data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, pk=pk, doctor=doctor)
        serializer = ConsultationSerializer(consultation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, pk=pk, doctor=doctor)
        consultation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Prescription --------------------
class PrescriptionListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, consultation_id):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=doctor)
        prescriptions = consultation.prescriptions.all()
        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)

    def post(self, request, consultation_id):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=doctor)
        serializer = PrescriptionSerializer(data=request.data)
        if serializer.is_valid():
            prescription = serializer.save(consultation=consultation)
            return Response(PrescriptionSerializer(prescription).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrescriptionRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, consultation_id, pk):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=doctor)
        prescription = get_object_or_404(Prescription, id=pk, consultation=consultation)
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)

    def put(self, request, consultation_id, pk):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=doctor)
        prescription = get_object_or_404(Prescription, id=pk, consultation=consultation)
        serializer = PrescriptionSerializer(prescription, data=request.data)
        if serializer.is_valid():
            serializer.save(consultation=consultation)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, consultation_id, pk):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=doctor)
        prescription = get_object_or_404(Prescription, id=pk, consultation=consultation)
        serializer = PrescriptionSerializer(prescription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(consultation=consultation)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, consultation_id, pk):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=doctor)
        prescription = get_object_or_404(Prescription, id=pk, consultation=consultation)
        prescription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
