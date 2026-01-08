from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Clinic
from clinic_panel.models import Doctor, Patient, Appointment, PatientAttachment
from doctor_panel.models import Consultation
from .serializers import ClinicSerializer, DoctorSerializer, PatientSerializer, AppointmentSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from clinic_project.permissions import RoleBasedPanelAccess


User = get_user_model()

# class SwitchableUsersView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # ✅ Only superadmin can get list
#         if request.user.role.lower() != "superadmin":
#             return Response({"error": "Unauthorized"}, status=403)

#         # ✅ Clinics
#         clinics = Clinic.objects.filter(status="ACTIVE").select_related("user")
#         clinic_list = [
#             {
#                 "id": c.user.id,
#                 "role": "clinic",
#                 "name": c.name or c.user.username,
#             }
#             for c in clinics
#         ]

#         # ✅ Doctors
#         doctors = Doctor.objects.all().select_related("user", "clinic")
#         doctor_list = [
#             {
#                 "id": d.user.id,
#                 "role": "doctor",
#                 "name": d.name or d.user.username,
#             }
#             for d in doctors
#         ]

#         # ✅ Include Superadmin (self)
#         superadmin_info = {
#             "id": request.user.id,
#             "role": "superadmin",
#             "name": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
#         }

#         # ✅ Combine Superadmin + Clinics + Doctors
#         return Response({"users": [superadmin_info] + clinic_list + doctor_list})


class SwitchableUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only superadmin can get list
        if request.user.role.lower() != "superadmin":
            return Response({"error": "Unauthorized"}, status=403)

        # Clinics list
        clinics = Clinic.objects.filter(status="ACTIVE").select_related("user")
        clinic_list = [
            {
                "id": c.user.id,
                "role": "clinic",
                "name": c.name or c.user.username,
                "clinic_id": c.id,
            }
            for c in clinics
        ]

        # Doctors list (added doctor_id)
        doctors = Doctor.objects.select_related("user", "clinic").all()
        doctor_list = [
            {
                "id": d.user.id,
                "doctor_id": d.id,
                "role": "doctor",
                "name": d.name or d.user.username,
                "clinic_id": d.clinic.id if d.clinic else None,
            }
            for d in doctors
        ]

        # Superadmin info
        superadmin_info = {
            "id": request.user.id,
            "role": "superadmin",
            "name": f"{request.user.first_name} {request.user.last_name}".strip()
            or request.user.username,
            "clinic_id": None,
        }

        # Combine all
        return Response({
            "users": [superadmin_info] + clinic_list + doctor_list
        })
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_panel(request):
    user = request.user

    # Only Superadmin can switch
    if user.role.upper() != "SUPERADMIN":
        return Response({"error": "Only Superadmin can switch panels."}, status=403)

    target_id = request.data.get("target_id")

    try:
        target_user = User.objects.get(id=target_id)
    except User.DoesNotExist:
        return Response({"error": "Target user not found"}, status=404)

    # Create a token for the superadmin but add acting_as data
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    access_token["acting_as_role"] = target_user.role.lower()
    access_token["acting_as_user_id"] = target_user.id

    # ✅ Build a readable target name
    full_name = f"{target_user.first_name} {target_user.last_name}".strip()
    target_name = full_name if full_name else target_user.username

    return Response({
        "access": str(access_token),
        "acting_as": target_user.role.lower(),
        "target_name": target_name,
        "target_id": target_user.id
    })

# -------------------- Dashboard --------------------
class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    panel_role = 'Superadmin'

    def get(self, request):

        if not request.user.is_authenticated:
            login_url = reverse("accounts:login")
            return redirect(login_url)
        
        clinics = Clinic.objects.all()
        doctors_count = Doctor.objects.count()
        patients_count = Patient.objects.count()
        consultations_count = Consultation.objects.count()
        appointments_count = Appointment.objects.count()

        clinics_serializer = ClinicSerializer(clinics, many=True)

        # Annotate each patient with their appointment count
        patients = Patient.objects.annotate(appointments_count=Count('appointments'))
        patients_data = [
            {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "appointments_count": patient.appointments_count
            }
            for patient in patients
        ]

        # Annotate each doctor with their appointment count
        doctors = Doctor.objects.annotate(bookings=Count('appointments'))
        doctors_data = [
            {
                "id": doctor.id,
                "name": doctor.name,
                "specialization": doctor.specialization,
                "bookings": doctor.bookings
            }
            for doctor in doctors
        ]

        user_data = {
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }

        return Response({
            "user": user_data,
            "clinics": clinics_serializer.data,
            "doctors_count": doctors_count,
            "patients_count": patients_count,
            "consultations_count": consultations_count,
            "appointments_count": appointments_count,
            "patients": patients_data,   # For: {patient.appointments_count}
            "doctors": doctors_data      # For: {doctor.bookings}
        })

# -------------------- Clinic --------------------
class ClinicListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        clinics = Clinic.objects.order_by("-created_at")
        serializer = ClinicSerializer(clinics, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        
        serializer = ClinicSerializer(data=request.data)
        if serializer.is_valid():
            clinic = serializer.save()
            return Response(ClinicSerializer(clinic).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        
        clinic = get_object_or_404(Clinic, pk=pk)
        serializer = ClinicSerializer(clinic)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        
        """Full update (all fields must be provided)"""
        clinic = get_object_or_404(Clinic, pk=pk)
        serializer = ClinicSerializer(clinic, data=request.data)  # full update
        if serializer.is_valid():
            clinic = serializer.save()
            return Response(ClinicSerializer(clinic).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        
        """Partial update (only provided fields updated)"""
        clinic = get_object_or_404(Clinic, pk=pk)
        serializer = ClinicSerializer(clinic, data=request.data, partial=True)  # partial=True
        if serializer.is_valid():
            clinic = serializer.save()
            return Response(ClinicSerializer(clinic).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clinic = get_object_or_404(Clinic, pk=pk)
        if clinic.user:
            clinic.user.delete()
        clinic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------- Doctor --------------------
class DoctorListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doctors = Doctor.objects.order_by("-created_at")
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    def put(self, request, pk):
        """Full update (replace all fields)"""
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorSerializer(doctor, data=request.data)  # full update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partial update (only provided fields)"""
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorSerializer(doctor, data=request.data, partial=True)  # partial update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        if doctor.user:
            doctor.user.delete()
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------- Patient --------------------
class PatientListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        patients = Patient.objects.order_by("-created_at")
        serializer = PatientSerializer(patients, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        serializer = PatientSerializer(patient, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        serializer = PatientSerializer(patient, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)

        # ✅ 1. Update normal fields (NO FILES)
        data = request.data.copy()
        data.pop("files", None)

        serializer = PatientSerializer(
            patient,
            data=data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ✅ 2. Handle files manually
        for file in request.FILES.getlist("files"):
            PatientAttachment.objects.create(
                patient=patient,
                file=file
            )

        return Response(PatientSerializer(patient).data)

    def delete(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientAttachmentDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        attachment = get_object_or_404(PatientAttachment, pk=pk)

        # Optional: permission check
        user = request.user
        patient = attachment.patient

        if hasattr(user, "clinic_profile"):
            if patient.clinic != user.clinic_profile:
                return Response(
                    {"detail": "Not authorized"},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Delete file from storage + DB
        attachment.file.delete(save=False)
        attachment.delete()

        return Response(
            {"detail": "Attachment deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
# -------------------- Appointment --------------------
class AppointmentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Admin: see all appointments
        appointments = Appointment.objects.all().order_by("-created_at")

        # Optional patient filter
        patient_id = request.query_params.get("patient_id")
        if patient_id:
            appointments = appointments.filter(patient_id=patient_id)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        # Admin must provide clinic_id
        clinic_id = data.get("clinic_id")
        if not clinic_id:
            return Response(
                {"detail": "clinic_id is required to create an appointment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        clinic = get_object_or_404(Clinic, id=clinic_id)
        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(
                created_by=request.user,
                clinic=clinic  # assign clinic based on clinic_id
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    def put(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentSerializer(appointment, data=request.data)  # full update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)  # partial update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminPatientVitalSignsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        patients = Patient.objects.all()
        if patient_id:
            patients = patients.filter(id=patient_id)

        response_data = []

        for patient in patients:
            # Get latest consultation for this patient
            latest_consultation = (
                Consultation.objects.filter(patient=patient)
                .order_by("-created_at")
                .first()
            )

            vital_signs = {
                "bloodPressure": latest_consultation.blood_pressure if latest_consultation and latest_consultation.blood_pressure else "N/A",
                "heartRate": latest_consultation.pulse if latest_consultation and latest_consultation.pulse else "N/A",
                "spo2": latest_consultation.spo2 if latest_consultation and latest_consultation.spo2 else "N/A",
                "temperature": latest_consultation.temperature if latest_consultation and latest_consultation.temperature else "N/A",
                "respiratoryRate": latest_consultation.respiratory_rate if latest_consultation and latest_consultation.respiratory_rate else "N/A",
                "weight": latest_consultation.weight if latest_consultation and latest_consultation.weight else "N/A",
            }

            response_data.append({
                "id": patient.id,
                "name": f"{patient.first_name} {patient.last_name}".strip(),
                "dob": patient.dob,
                "bloodGroup": patient.blood_group,
                "gender": patient.gender,
                "email": patient.email,
                "phone": patient.phone_number,
                "address": patient.address,
                "lastVisited": latest_consultation.appointment.appointment_date if latest_consultation and latest_consultation.appointment else "N/A",
                "vitalSigns": vital_signs,
            })

        return Response(response_data)

