from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Clinic
from clinic_panel.models import Doctor, Patient, Appointment
from doctor_panel.models import Consultation
from .serializers import ClinicSerializer, DoctorSerializer, PatientSerializer, AppointmentSerializer
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse


# -------------------- Dashboard --------------------
class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        if not request.user.is_authenticated:
            login_url = reverse("accounts:login")  # uses your app_name
            return redirect(login_url)
        
        clinics = Clinic.objects.all()
        doctors_count = Doctor.objects.count()
        patients_count = Patient.objects.count()
        consultations_count = Consultation.objects.count()
        appointments_count = Appointment.objects.count()

        clinics_serializer = ClinicSerializer(clinics, many=True)

        return Response({
            "clinics": clinics_serializer.data,
            "doctors_count": doctors_count,
            "patients_count": patients_count,
            "consultations_count": consultations_count,
            "appointments_count": appointments_count,
        })

# -------------------- Clinic --------------------
class ClinicListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        clinics = Clinic.objects.all()
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
        doctors = Doctor.objects.all()
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

    def get(self, request):
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        serializer = PatientSerializer(patient, data=request.data)  # full update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        serializer = PatientSerializer(patient, data=request.data, partial=True)  # partial update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# -------------------- Appointment --------------------
class AppointmentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Admin: see all appointments
        appointments = Appointment.objects.all().order_by("-appointment_date", "-appointment_time")

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
                "bloodPressure": "N/A",  # field not in model
                "heartRate": latest_consultation.pulse if latest_consultation else "N/A",
                "spo2": latest_consultation.spo2 if latest_consultation else "N/A",
                "temperature": latest_consultation.temperature if latest_consultation else "N/A",
                "respiratoryRate": latest_consultation.respiratory_rate if latest_consultation else "N/A",
                "weight": latest_consultation.weight if latest_consultation else "N/A",
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

