from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.backends import TokenBackend
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from clinic_panel.models import Appointment, Patient
from clinic_panel.serializers import PatientHistorySerializer
from .models import Consultation, Prescription, Doctor
from .serializers import ConsultationSerializer, PrescriptionSerializer, PrescriptionListSerializer
from .serializers import DoctorAppointmentSerializer
from admin_panel.serializers import AppointmentSerializer
from django.db import transaction
from clinic_project.permissions import RoleBasedPanelAccess
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class DoctorDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    panel_role = 'Doctor'

    def get(self, request, doctor_id=None):
        user = request.user
        doctor = None

        # --- Case 1: Superadmin (switching between doctors) ---
        if user.role == "SUPERADMIN":
            if doctor_id:
                # If doctor_id is passed in URL, load that doctor's dashboard
                try:
                    target_user = User.objects.get(id=doctor_id, role="DOCTOR")
                    doctor = target_user.doctor_profile
                except (User.DoesNotExist, Doctor.DoesNotExist):
                    return Response({"error": "Doctor not found."}, status=404)
            else:
                # fallback: token may have 'acting_as' info
                auth_header = request.headers.get("Authorization", "")
                token = auth_header.split(" ")[1] if " " in auth_header else None
                if token:
                    try:
                        payload = TokenBackend(algorithm='HS256').decode(token, verify=False)
                        acting_as_id = payload.get("target_id")
                        if acting_as_id:
                            acting_user = User.objects.get(id=acting_as_id)
                            doctor = acting_user.doctor_profile
                    except Exception:
                        pass

            # fallback if no doctor found
            if not doctor:
                doctor = Doctor.objects.first()
                if not doctor:
                    return Response({"error": "No doctor found to access."}, status=404)

        # --- Case 2: Normal doctor user ---
        elif user.role == "DOCTOR":
            try:
                doctor = user.doctor_profile
            except Doctor.DoesNotExist:
                return Response({"error": "Doctor profile not found."}, status=404)

        # --- Case 3: Unauthorized roles ---
        else:
            return Response({"error": "Only doctors or superadmins can access this dashboard."}, status=403)

        # ✅ --- Dashboard Data ---
        total_consultations = Consultation.objects.filter(doctor=doctor).count()
        total_patients = Patient.objects.filter(appointments__doctor=doctor).distinct().count()
        total_prescriptions = Prescription.objects.filter(consultation__doctor=doctor).count()

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

        user_data = {
            "username": doctor.user.username,
            "first_name": doctor.user.first_name,
            "last_name": doctor.user.last_name,
        }

        data = {
            "user": user_data,
            "doctor_name": doctor.name,
            "total_consultations": total_consultations,
            "total_patients": total_patients,
            "total_prescriptions": total_prescriptions,
            "upcoming_appointments": upcoming_appointments_data,
        }

        return Response(data)

# -------------------- Consultation --------------------
class ConsultationListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_doctor(self, request):
        """
        Determine which doctor to use:
        - If Superadmin, use ?doctor_id=<id>
        - If Doctor, use their profile
        """
        user = request.user
        if user.role.lower() == "superadmin":
            doctor_id = request.query_params.get("doctor_id")
            if not doctor_id:
                raise PermissionDenied("doctor_id is required for superadmin.")
            return get_object_or_404(Doctor, id=doctor_id)
        elif hasattr(user, "doctor_profile"):
            return user.doctor_profile
        raise PermissionDenied("Only doctors or superadmins can access consultations.")

    def get(self, request):
        doctor = self.get_doctor(request)

        scheduled_appointments = (
            Appointment.objects.filter(doctor=doctor, status="SCHEDULED")
            .exclude(consultation__isnull=False)
            .select_related("patient", "doctor__clinic")
            .order_by("-appointment_date", "-appointment_time")
        )

        data = []
        for a in scheduled_appointments:
            date_time = f"{a.appointment_date.strftime('%d %b %Y')} - {a.appointment_time.strftime('%I:%M %p')}"
            patient_name = f"{a.patient.first_name} {a.patient.last_name}".strip()
            data.append({
                "appointment_id": a.id,
                "date_time": date_time,
                "patient": patient_name,
                "patient_id": a.patient.id,
                "doctor": a.doctor.name,
                "doctor_id": a.doctor.id,
                "clinic": a.doctor.clinic.name,
                "status": a.status,
            })

        data.sort(key=lambda x: x["date_time"])
        return Response(data)

    @transaction.atomic
    def post(self, request):
        doctor = self.get_doctor(request)
        patient_id = request.data.get("patient")
        appointment_id = request.data.get("appointment")

        patient = get_object_or_404(Patient, id=patient_id, clinic=doctor.clinic)
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

        if hasattr(appointment, "consultation"):
            return Response(
                {"appointment": ["Consultation for this appointment already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ConsultationSerializer(data=request.data)
        if serializer.is_valid():
            consultation = serializer.save(doctor=doctor, patient=patient, appointment=appointment)
            appointment.status = "COMPLETED"
            appointment.save()

            # Optional prescriptions
            prescriptions_data = request.data.get("prescriptions", [])
            for p in prescriptions_data:
                medicine_name = p.get("medicine_name")
                procedure_id = p.get("procedure")
                if medicine_name:
                    Prescription.objects.create(
                        consultation=consultation,
                        medicine_name=medicine_name,
                        dosage=p.get("dosage"),
                        frequency=p.get("frequency"),
                        duration=p.get("duration"),
                        timings=p.get("timings"),
                    )
                elif procedure_id:
                    Prescription.objects.create(
                        consultation=consultation,
                        procedure_id=procedure_id,
                    )

            return Response(ConsultationSerializer(consultation).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsultationRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_doctor(self, request):
        user = request.user
        if user.role.lower() == "superadmin":
            doctor_id = request.query_params.get("doctor_id") or request.data.get("doctor_id")
            if not doctor_id:
                raise PermissionDenied("doctor_id is required for superadmin.")
            return get_object_or_404(Doctor, id=doctor_id)
        elif hasattr(user, "doctor_profile"):
            return user.doctor_profile
        raise PermissionDenied("Only doctors or superadmins can access consultations.")

    def get_object(self, pk, doctor):
        return get_object_or_404(Consultation, pk=pk, doctor=doctor)

    def get(self, request, pk):
        doctor = self.get_doctor(request)
        consultation = self.get_object(pk, doctor)
        serializer = ConsultationSerializer(consultation)
        return Response(serializer.data)

    def put(self, request, pk):
        doctor = self.get_doctor(request)
        consultation = self.get_object(pk, doctor)
        serializer = ConsultationSerializer(consultation, data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        doctor = self.get_doctor(request)
        consultation = self.get_object(pk, doctor)
        serializer = ConsultationSerializer(consultation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = self.get_doctor(request)
        consultation = self.get_object(pk, doctor)
        consultation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# -------------------- AllAppointments --------------------

class DoctorAllAppointmentsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_doctor(self, request):
        """Get the doctor profile based on role."""
        user = request.user
        if user.role.lower() == "superadmin":
            doctor_id = request.query_params.get("doctor_id")
            if not doctor_id:
                raise PermissionDenied("doctor_id is required for superadmin.")
            return get_object_or_404(Doctor, id=doctor_id)
        elif hasattr(user, "doctor_profile"):
            return user.doctor_profile
        raise PermissionDenied("Only doctors or superadmins can access this endpoint.")

    def get(self, request):
        doctor = self.get_doctor(request)
        appointments = (
            Appointment.objects.filter(doctor=doctor)
            .select_related("patient", "doctor__clinic")
            .order_by("-created_at")
        )
        serializer = DoctorAppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class DoctorScheduledAppointmentsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_doctor(self, request):
        user = request.user
        if user.role.lower() == "superadmin":
            doctor_id = request.query_params.get("doctor_id")
            if not doctor_id:
                raise PermissionDenied("doctor_id is required for superadmin.")
            return get_object_or_404(Doctor, id=doctor_id)

        if hasattr(user, "doctor_profile"):
            return user.doctor_profile

        raise PermissionDenied("Only doctors or superadmins can access this endpoint.")

    def cancel_expired_appointments(self, doctor):
        """
        Auto-cancel appointments that crossed date/time
        and have no consultation.
        """
        now = timezone.localtime()
        today = now.date()
        current_time = now.time()

        Appointment.objects.filter(
            doctor=doctor,
            status="SCHEDULED",
            consultation__isnull=True
        ).filter(
            Q(appointment_date__lt=today) |
            Q(
                appointment_date=today,
                appointment_time__lt=current_time
            )
        ).update(status="CANCELLED")

    def get(self, request):
        doctor = self.get_doctor(request)

        # ✅ Auto-cancel expired appointments
        self.cancel_expired_appointments(doctor)

        appointments = (
            Appointment.objects.filter(
                doctor=doctor,
                status="SCHEDULED",
                consultation__isnull=True
            )
            .select_related("patient", "doctor__clinic")
            .order_by("appointment_date", "appointment_time")
        )

        serializer = DoctorAppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class DoctorAppointmentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_doctor(self, request):
        """Get doctor for current user or superadmin."""
        user = request.user
        if user.role.lower() == "superadmin":
            doctor_id = request.query_params.get("doctor_id")
            if not doctor_id:
                raise PermissionDenied("doctor_id is required for superadmin.")
            return get_object_or_404(Doctor, id=doctor_id)
        elif hasattr(user, "doctor_profile"):
            return user.doctor_profile
        raise PermissionDenied("Only doctors or superadmins can access this endpoint.")

    def get(self, request, pk):
        doctor = self.get_doctor(request)
        appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
        serializer = DoctorAppointmentSerializer(appointment)
        return Response(serializer.data)

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

    def get_doctor(self, request):
        user = request.user

        # Superadmin can view any doctor's prescriptions
        if user.role.lower() == "superadmin":
            doctor_id = request.query_params.get("doctor_id")
            if not doctor_id:
                raise PermissionDenied("doctor_id is required for superadmin.")
            return get_object_or_404(Doctor, id=doctor_id)

        # Doctor user can only view their own
        if hasattr(user, "doctor_profile"):
            return user.doctor_profile

        raise PermissionDenied("Only doctors or superadmins can access this endpoint.")

    def get(self, request):
        doctor = self.get_doctor(request)

        prescriptions = (
            Prescription.objects.filter(consultation__doctor=doctor)
            .select_related("consultation", "consultation__patient")
            .order_by("-created_at")
        )

        serializer = PrescriptionListSerializer(prescriptions, many=True)
        return Response(serializer.data)


class DoctorPrescriptionDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_doctor(self, request):
        user = request.user

        if user.role.lower() == "superadmin":
            doctor_id = request.query_params.get("doctor_id")
            if not doctor_id:
                raise PermissionDenied("doctor_id is required for superadmin.")
            return get_object_or_404(Doctor, id=doctor_id)

        if hasattr(user, "doctor_profile"):
            return user.doctor_profile

        raise PermissionDenied("Only doctors or superadmins can access this endpoint.")

    def get(self, request, pk):
        doctor = self.get_doctor(request)

        prescription = get_object_or_404(
            Prescription, id=pk, consultation__doctor=doctor
        )

        serializer = ConsultationSerializer(prescription.consultation)
        return Response(serializer.data)


class DoctorPatientHistoryView(RetrieveAPIView):
    serializer_class = PatientHistorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user

        # 🔒 Doctor-only access
        if not hasattr(user, "doctor_profile"):
            return Patient.objects.none()

        doctor = user.doctor_profile

        return (
            Patient.objects
            .filter(
                appointments__consultation__doctor=doctor
            )
            .distinct()
            .prefetch_related(
                "attachments",
                Prefetch(
                    "appointments",
                    queryset=Appointment.objects.filter(
                        consultation__doctor=doctor
                    ).select_related(
                        "doctor", "clinic"
                    ).prefetch_related(
                        "consultation__prescriptions"
                    )
                )
            )
            .select_related("clinic")
        )