from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Clinic
from clinic_panel.models import Doctor, Patient, Appointment
from doctor_panel.models import Consultation
from .serializers import ClinicSerializer, DoctorSerializer, PatientSerializer, AppointmentSerializer
from django.shortcuts import get_object_or_404


# -------------------- Dashboard --------------------
class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
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
        clinics = Clinic.objects.all()
        serializer = ClinicSerializer(clinics, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClinicSerializer(data=request.data)
        if serializer.is_valid():
            clinic = serializer.save()
            return Response(ClinicSerializer(clinic).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        clinic = get_object_or_404(Clinic, pk=pk)
        serializer = ClinicSerializer(clinic)
        return Response(serializer.data)

    def put(self, request, pk):
        """Full update (all fields must be provided)"""
        clinic = get_object_or_404(Clinic, pk=pk)
        serializer = ClinicSerializer(clinic, data=request.data)  # full update
        if serializer.is_valid():
            clinic = serializer.save()
            return Response(ClinicSerializer(clinic).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
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
        appointments = Appointment.objects.filter(
            clinic=request.user
        ).order_by("-appointment_date", "-appointment_time")
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Use this fixed version
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                created_by=request.user,
                clinic=request.user
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

