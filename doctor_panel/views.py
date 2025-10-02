from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from clinic_panel.models import Appointment, Patient
from .models import Consultation, Prescription
from .serializers import ConsultationSerializer, PrescriptionSerializer, PrescriptionListSerializer


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
        doctor = request.user.doctor_profile

        # Scheduled appointments (without consultations yet)
        appointments = Appointment.objects.filter(
            doctor=doctor
        ).select_related("patient", "doctor__clinic", "consultation")
        
        data = []
        for a in appointments:
            date_time = f"{a.appointment_date.strftime('%d %b %Y')} - {a.appointment_time.strftime('%I:%M %p')}"
            patient_name = f"{a.patient.first_name} {a.patient.last_name}".strip()
            data.append({
                "appointment_id": a.id,
                "consultation_id": a.consultation.id if hasattr(a, 'consultation') and a.consultation else None,
                "date_time": date_time,
                "patient": patient_name,
                "patient_id": a.patient.id,
                "doctor": a.doctor.name,
                "doctor_id": a.doctor.id,
                "clinic": a.doctor.clinic.name if a.doctor.clinic else None,
                "status": a.status,
            })



        # Optional: sort by date and time
        data.sort(key=lambda x: x["date_time"])

        return Response(data)
    
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

# -------------------- AllAppointments --------------------

class DoctorAllAppointmentsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doctor = request.user.doctor_profile

        appointments = Appointment.objects.filter(doctor=doctor).select_related("patient", "doctor__clinic")

        data = []
        for a in appointments:
            status = "COMPLETED" if hasattr(a, 'consultation') else a.status
            date_time = f"{a.appointment_date.strftime('%d %b %Y')} - {a.appointment_time.strftime('%I:%M %p')}"
            patient_name = f"{a.patient.first_name} {a.patient.last_name}".strip()

            data.append({
                "appointment_id": a.appointment_id,
                "date_time": date_time,
                "patient": patient_name,
                "doctor": a.doctor.name,
                "clinic": a.doctor.clinic.name,
                "status": status,
            })

        data.sort(key=lambda x: x["date_time"])

        return Response(data)
    

# -------------------- Prescription --------------------
class PrescriptionListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, consultation_id):
        doctor = request.user.doctor_profile
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=doctor)
        serializer = ConsultationSerializer(consultation)
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



class DoctorPrescriptionListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doctor = request.user.doctor_profile
        prescriptions = Prescription.objects.filter(
            consultation__doctor=doctor
        ).order_by('-created_at')  # newest first
        serializer = PrescriptionListSerializer(prescriptions, many=True)
        return Response(serializer.data)
    
class DoctorPrescriptionDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        doctor = request.user.doctor_profile
        prescription = get_object_or_404(
            Prescription, id=pk, consultation__doctor=doctor
        )
        serializer = ConsultationSerializer(prescription.consultation)
        return Response(serializer.data)

