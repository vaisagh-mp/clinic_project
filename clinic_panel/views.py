from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from .models import Doctor, Patient, Appointment
from doctor_panel.models import Prescription, Consultation    
from admin_panel.serializers import DoctorSerializer, PatientSerializer, AppointmentSerializer, ClinicAppointmentSerializer
from doctor_panel.serializers import PrescriptionSerializer   



class ClinicDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Make sure only CLINIC role users can access this
        if request.user.role != "CLINIC":
            return Response({"error": "Only clinic users can access this endpoint."}, status=403)

        clinic = request.user.clinic_profile  # ✅ use related_name

        # Doctors, Patients, Appointments filtered by clinic
        doctors = Doctor.objects.filter(clinic=clinic)
        patients = Patient.objects.filter(clinic=clinic)
        appointments = Appointment.objects.filter(clinic=clinic)

        # Stats
        total_doctors = doctors.count()
        total_patients = patients.count()
        total_appointments = appointments.count()
        upcoming_appointments = appointments.filter(appointment_date__gte=now().date()).count()
        completed_appointments = appointments.filter(status="COMPLETED").count()
        cancelled_appointments = appointments.filter(status="CANCELLED").count()

        data = {
            "clinic": clinic.name,
            "stats": {
                "total_doctors": total_doctors,
                "total_patients": total_patients,
                "total_appointments": total_appointments,
                "upcoming_appointments": upcoming_appointments,
                "completed_appointments": completed_appointments,
                "cancelled_appointments": cancelled_appointments,
            },
            "latest_doctors": DoctorSerializer(doctors.order_by("-created_at")[:5], many=True).data,
            "latest_patients": PatientSerializer(patients.order_by("-created_at")[:5], many=True).data,
            "upcoming_appointments": AppointmentSerializer(
                appointments.filter(appointment_date__gte=now().date()).order_by("appointment_date")[:5], 
                many=True
            ).data,
        }

        return Response(data)

# -------------------- Doctor --------------------
class DoctorListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Filter doctors by clinic of logged-in user
        doctors = Doctor.objects.filter(clinic=request.user.clinic_profile)
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["clinic"] = request.user.clinic_profile.id  # assign logged-in clinic
        serializer = DoctorSerializer(data=data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(Doctor, pk=pk, clinic=clinic)

    def get(self, request, pk):
        doctor = self.get_object(pk, request.user.clinic_profile)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    def put(self, request, pk):
        doctor = self.get_object(pk, request.user.clinic_profile)
        data = request.data.copy()
        data["clinic"] = request.user.clinic_profile.id
        serializer = DoctorSerializer(doctor, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        doctor = self.get_object(pk, request.user.clinic_profile)
        data = request.data.copy()
        data["clinic"] = request.user.clinic_profile.id
        serializer = DoctorSerializer(doctor, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = self.get_object(pk, request.user.clinic_profile)
        if doctor.user:
            doctor.user.delete()
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# -------------------- Patient --------------------
class PatientListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        patients = Patient.objects.filter(clinic=request.user.clinic_profile)
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["clinic"] = request.user.clinic_profile.id
        serializer = PatientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(Patient, pk=pk, clinic=clinic)

    def get(self, request, pk):
        patient = self.get_object(pk, request.user.clinic_profile)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk):
        patient = self.get_object(pk, request.user.clinic_profile)
        data = request.data.copy()
        data["clinic"] = request.user.clinic_profile.id
        serializer = PatientSerializer(patient, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        patient = self.get_object(pk, request.user.clinic_profile)
        data = request.data.copy()
        data["clinic"] = request.user.clinic_profile.id
        serializer = PatientSerializer(patient, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        patient = self.get_object(pk, request.user.clinic_profile)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# -------------------- Appointment --------------------
class AppointmentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Choose serializer based on user type."""
        user = self.request.user
        if hasattr(user, "clinic_profile"):
            return ClinicAppointmentSerializer
        return AppointmentSerializer

    def get_queryset(self, request):
        """Filter appointments by user type."""
        user = request.user

        if hasattr(user, "clinic_profile"):
            return Appointment.objects.filter(clinic=user.clinic_profile)

        elif hasattr(user, "doctor_profile"):
            return Appointment.objects.filter(doctor=user.doctor_profile)

        else:
            clinic_id = request.query_params.get("clinic")
            if clinic_id:
                return Appointment.objects.filter(clinic_id=clinic_id)
            return Appointment.objects.all()

    def get(self, request):
        appointments = self.get_queryset(request).order_by(
            "-appointment_date", "-appointment_time"
        )
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        user = request.user
        serializer_class = self.get_serializer_class()

        # Auto-assign clinic for clinic panel
        if hasattr(user, "clinic_profile"):
            data["clinic_id"] = user.clinic_profile.id
        else:
            # Admin must provide clinic_id
            if "clinic_id" not in data:
                return Response(
                    {"detail": "clinic_id is required for appointment creation."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        user = self.request.user
        if hasattr(user, "doctor_profile"):
            return get_object_or_404(Appointment, pk=pk, doctor=user.doctor_profile)
        elif hasattr(user, "clinic_profile"):
            return get_object_or_404(Appointment, pk=pk, clinic=user.clinic_profile)
        else:
            return get_object_or_404(Appointment, pk=pk)

    def get_serializer_class(self):
        """Return serializer based on user type."""
        user = self.request.user
        if hasattr(user, "clinic_profile"):
            return ClinicAppointmentSerializer
        return AppointmentSerializer

    def get(self, request, pk):
        appointment = self.get_object(pk)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(appointment)
        return Response(serializer.data)

    def put(self, request, pk):
        appointment = self.get_object(pk)
        serializer_class = self.get_serializer_class()

        context = {}
        if hasattr(request.user, "clinic_profile"):
            context["clinic"] = request.user.clinic_profile

        serializer = serializer_class(
            appointment, data=request.data, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        appointment = self.get_object(pk)
        serializer_class = self.get_serializer_class()

        context = {}
        if hasattr(request.user, "clinic_profile"):
            context["clinic"] = request.user.clinic_profile

        serializer = serializer_class(
            appointment, data=request.data, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        appointment = self.get_object(pk)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ------------------------------------------------Prescriptions-------------------------------------------------------------

class ClinicPrescriptionListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = request.user.clinic_profile
        prescriptions = Prescription.objects.filter(
            consultation__doctor__clinic=clinic
        ).select_related("consultation", "consultation__doctor", "consultation__patient")

        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a prescription under a specific consultation belonging to this clinic."""
        clinic = request.user.clinic_profile
        consultation_id = request.data.get("consultation_id")

        if not consultation_id:
            return Response(
                {"detail": "consultation_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        consultation = get_object_or_404(Consultation, id=consultation_id, doctor__clinic=clinic)
        serializer = PrescriptionSerializer(data=request.data)

        if serializer.is_valid():
            prescription = serializer.save(consultation=consultation)
            return Response(
                PrescriptionSerializer(prescription).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicPrescriptionRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        """Ensure the prescription belongs to a consultation under this clinic."""
        return get_object_or_404(Prescription, id=pk, consultation__doctor__clinic=clinic)

    def get(self, request, pk):
        clinic = request.user.clinic_profile
        prescription = self.get_object(pk, clinic)
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)

    def put(self, request, pk):
        clinic = request.user.clinic_profile
        prescription = self.get_object(pk, clinic)
        serializer = PrescriptionSerializer(prescription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        clinic = request.user.clinic_profile
        prescription = self.get_object(pk, clinic)
        serializer = PrescriptionSerializer(prescription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clinic = request.user.clinic_profile
        prescription = self.get_object(pk, clinic)
        prescription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)