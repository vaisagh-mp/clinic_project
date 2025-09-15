from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from .models import Doctor, Patient, Appointment    
from admin_panel.serializers import DoctorSerializer, PatientSerializer, AppointmentSerializer   



class ClinicDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = request.user.clinic  # get clinic of logged-in user

        # Doctors, Patients, Appointments filtered by clinic
        doctors = Doctor.objects.filter(clinic=clinic)
        patients = Patient.objects.filter(clinic=clinic)
        appointments = Appointment.objects.filter(clinic=clinic)

        # Some quick stats
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
        doctors = Doctor.objects.filter(clinic=request.user.clinic)
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id  # assign logged-in clinic
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
        doctor = self.get_object(pk, request.user.clinic)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    def put(self, request, pk):
        doctor = self.get_object(pk, request.user.clinic)
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id
        serializer = DoctorSerializer(doctor, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        doctor = self.get_object(pk, request.user.clinic)
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id
        serializer = DoctorSerializer(doctor, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = self.get_object(pk, request.user.clinic)
        if doctor.user:
            doctor.user.delete()
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# -------------------- Patient --------------------
class PatientListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        patients = Patient.objects.filter(clinic=request.user.clinic)
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id
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
        patient = self.get_object(pk, request.user.clinic)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk):
        patient = self.get_object(pk, request.user.clinic)
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id
        serializer = PatientSerializer(patient, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        patient = self.get_object(pk, request.user.clinic)
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id
        serializer = PatientSerializer(patient, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        patient = self.get_object(pk, request.user.clinic)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# -------------------- Appointment --------------------
class AppointmentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        appointments = Appointment.objects.filter(clinic=request.user.clinic).order_by("-appointment_date", "-appointment_time")
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id
        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(Appointment, pk=pk, clinic=clinic)

    def get(self, request, pk):
        appointment = self.get_object(pk, request.user.clinic)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    def put(self, request, pk):
        appointment = self.get_object(pk, request.user.clinic)
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id
        serializer = AppointmentSerializer(appointment, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        appointment = self.get_object(pk, request.user.clinic)
        data = request.data.copy()
        data["clinic"] = request.user.clinic.id
        serializer = AppointmentSerializer(appointment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        appointment = self.get_object(pk, request.user.clinic)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

