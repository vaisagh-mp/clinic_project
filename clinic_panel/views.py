from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from clinic_project.permissions import RoleBasedPanelAccess
from .models import Doctor, Patient, Appointment
from admin_panel.models import Clinic
from doctor_panel.models import Prescription, Consultation    
from admin_panel.serializers import DoctorSerializer, PatientSerializer, AppointmentSerializer, ClinicAppointmentSerializer
from doctor_panel.serializers import PrescriptionSerializer, ConsultationSerializer
from .serializers import ClinicPrescriptionListSerializer, ClinicConsultationSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend


User = get_user_model()

class ClinicDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, clinic_id=None):
        user = request.user
        clinic = None

        # --- Case 1: Superadmin (switching between clinics) ---
        if user.role == "SUPERADMIN":
            if clinic_id:
                try:
                    target_user = User.objects.get(id=clinic_id, role="CLINIC")
                    clinic = target_user.clinic_profile
                except (User.DoesNotExist, Clinic.DoesNotExist):
                    return Response({"error": "Clinic not found."}, status=404)
            else:
                # fallback: use token acting_as info
                auth_header = request.headers.get("Authorization", "")
                token = auth_header.split(" ")[1] if " " in auth_header else None
                if token:
                    try:
                        payload = TokenBackend(algorithm='HS256').decode(token, verify=False)
                        acting_as_id = payload.get("target_id")
                        if acting_as_id:
                            acting_user = User.objects.get(id=acting_as_id)
                            clinic = acting_user.clinic_profile
                    except Exception:
                        pass

            if not clinic:
                clinic = Clinic.objects.first()
                if not clinic:
                    return Response({"error": "No clinic available to access."}, status=404)

        # --- Case 2: Normal clinic user ---
        elif user.role == "CLINIC":
            try:
                clinic = user.clinic_profile
                if clinic_id and clinic.user.id != clinic_id:
                    return Response({"error": "Unauthorized access."}, status=403)
            except Clinic.DoesNotExist:
                return Response({"error": "Clinic profile not found."}, status=404)

        # --- Case 3: Others ---
        else:
            return Response({"error": "Only clinic users or superadmin can access this endpoint."}, status=403)

        # --- Fetch related data ---
        doctors = Doctor.objects.filter(clinic=clinic)
        patients = Patient.objects.filter(clinic=clinic)
        appointments = Appointment.objects.filter(clinic=clinic)

        data = {
            "user": {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "clinic": clinic.name,
            "stats": {
                "total_doctors": doctors.count(),
                "total_patients": patients.count(),
                "total_appointments": appointments.count(),
                "upcoming_appointments": appointments.filter(appointment_date__gte=now().date()).count(),
                "completed_appointments": appointments.filter(status="COMPLETED").count(),
                "cancelled_appointments": appointments.filter(status="CANCELLED").count(),
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
# class DoctorListCreateAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         # Filter doctors by clinic of logged-in user
#         doctors = Doctor.objects.filter(clinic=request.user.clinic_profile).order_by("-created_at")
#         serializer = DoctorSerializer(doctors, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         data = request.data.copy()
#         data["clinic"] = request.user.clinic_profile.id  # assign logged-in clinic
#         serializer = DoctorSerializer(data=data)
#         if serializer.is_valid():
#             doctor = serializer.save()
#             return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class DoctorRetrieveUpdateDeleteAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self, pk, clinic):
#         return get_object_or_404(Doctor, pk=pk, clinic=clinic)

#     def get(self, request, pk):
#         doctor = self.get_object(pk, request.user.clinic_profile)
#         serializer = DoctorSerializer(doctor)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         doctor = self.get_object(pk, request.user.clinic_profile)
#         data = request.data.copy()
#         data["clinic"] = request.user.clinic_profile.id
#         serializer = DoctorSerializer(doctor, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, pk):
#         doctor = self.get_object(pk, request.user.clinic_profile)
#         data = request.data.copy()
#         data["clinic"] = request.user.clinic_profile.id
#         serializer = DoctorSerializer(doctor, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         doctor = self.get_object(pk, request.user.clinic_profile)
#         if doctor.user:
#             doctor.user.delete()
#         doctor.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class DoctorListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, clinic_id=None):
        """Get all doctors for a clinic or the logged-in clinic"""
        user = request.user

        if user.is_superuser:
            # Superadmin mode — must include clinic_id
            if not clinic_id:
                return Response(
                    {"detail": "clinic_id required for superadmin."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            doctors = Doctor.objects.filter(clinic_id=clinic_id).order_by("-created_at")
        else:
            # Normal clinic user
            if not hasattr(user, "clinic_profile"):
                return Response(
                    {"detail": "This user is not linked to any clinic."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            doctors = Doctor.objects.filter(clinic=user.clinic_profile).order_by("-created_at")

        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

    def post(self, request, clinic_id=None):
        """Create doctor for clinic"""
        user = request.user
        data = request.data.copy()

        if user.is_superuser:
            if not clinic_id:
                return Response(
                    {"detail": "clinic_id required for superadmin."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data["clinic"] = clinic_id
        else:
            if not hasattr(user, "clinic_profile"):
                return Response(
                    {"detail": "This user is not linked to any clinic."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data["clinic"] = user.clinic_profile.id

        serializer = DoctorSerializer(data=data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic_id, request):
        """Return the doctor object with correct access control"""
        user = request.user

        if user.is_superuser:
            if not clinic_id:
                raise PermissionError("clinic_id required for superadmin.")
            return get_object_or_404(Doctor, pk=pk, clinic_id=clinic_id)
        else:
            if not hasattr(user, "clinic_profile"):
                raise PermissionError("This user is not linked to any clinic.")
            return get_object_or_404(Doctor, pk=pk, clinic=user.clinic_profile)

    def get(self, request, pk, clinic_id=None):
        try:
            doctor = self.get_object(pk, clinic_id, request)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    def put(self, request, pk, clinic_id=None):
        try:
            doctor = self.get_object(pk, clinic_id, request)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data["clinic"] = clinic_id if clinic_id else request.user.clinic_profile.id

        serializer = DoctorSerializer(doctor, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, clinic_id=None):
        try:
            doctor = self.get_object(pk, clinic_id, request)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data["clinic"] = clinic_id if clinic_id else request.user.clinic_profile.id

        serializer = DoctorSerializer(doctor, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, clinic_id=None):
        try:
            doctor = self.get_object(pk, clinic_id, request)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if doctor.user:
            doctor.user.delete()
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------- Patient --------------------
class PatientListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        patients = Patient.objects.filter(clinic=request.user.clinic_profile).order_by("-created_at")
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
        """Filter appointments by user type and optionally by patient_id."""
        user = request.user
        patient_id = request.query_params.get("patient_id")

        # --- Start with base queryset depending on role ---
        if hasattr(user, "clinic_profile"):
            queryset = Appointment.objects.filter(clinic=user.clinic_profile)

        elif hasattr(user, "doctor_profile"):
            queryset = Appointment.objects.filter(doctor=user.doctor_profile)

        else:
            clinic_id = request.query_params.get("clinic")
            if clinic_id:
                queryset = Appointment.objects.filter(clinic_id=clinic_id)
            else:
                queryset = Appointment.objects.all()

        # --- ✅ Apply patient filter if provided ---
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
            
        queryset = queryset.order_by("-appointment_date", "-appointment_time")

        return queryset

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

        context = {}
        # Auto-assign clinic for clinic panel
        if hasattr(user, "clinic_profile"):
            data["clinic_id"] = user.clinic_profile.id
            context["clinic"] = user.clinic_profile
        else:
            # Admin must provide clinic_id
            if "clinic_id" not in data:
                return Response(
                    {"detail": "clinic_id is required for appointment creation."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = serializer_class(data=data, context=context)
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

class ClinicPrescriptionListAPIView(APIView):
    """
    List all prescriptions for the logged-in clinic.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = request.user.clinic_profile
        prescriptions = Prescription.objects.filter(
            consultation__doctor__clinic=clinic
        ).select_related("consultation", "consultation__patient").order_by("-created_at")

        serializer = ClinicPrescriptionListSerializer(prescriptions, many=True)
        return Response(serializer.data)


class ClinicPrescriptionDetailAPIView(APIView):
    """
    Retrieve a single prescription detail for the logged-in clinic.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        clinic = request.user.clinic_profile
        prescription = get_object_or_404(
            Prescription, id=pk, consultation__doctor__clinic=clinic
        )
        serializer = ClinicConsultationSerializer(prescription.consultation)
        return Response(serializer.data)
    

class ClinicConsultationListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if not hasattr(user, "clinic_profile"):
            return Response(
                {"detail": "Only clinic users can access this."}, status=403
            )

        # Fetch all consultations for patients under this clinic
        consultations = Consultation.objects.filter(
            doctor__clinic=user.clinic_profile
        ).order_by("-created_at")

        # Optional: filter by patient_id if provided
        patient_id = request.query_params.get("patient_id")
        if patient_id:
            consultations = consultations.filter(patient_id=patient_id)

        serializer = ConsultationSerializer(consultations, many=True)
        return Response(serializer.data)