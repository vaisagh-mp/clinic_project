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

    def get(self, request):
        if hasattr(request.user, "clinic_profile"):
            # Clinic panel user → show only their clinic appointments
            appointments = Appointment.objects.filter(
                clinic=request.user.clinic_profile
            )
        else:
            # Admin panel user → show all, or filter by ?clinic=ID
            clinic_id = request.query_params.get("clinic")
            if clinic_id:
                appointments = Appointment.objects.filter(clinic_id=clinic_id)
            else:
                appointments = Appointment.objects.all()

        appointments = appointments.order_by("-appointment_date", "-appointment_time")
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        if hasattr(request.user, "clinic_profile"):
            # Clinic panel user → force clinic_id to their clinic_profile
            data["clinic_id"] = request.user.clinic_profile.id
        else:
            # Admin panel user → must provide clinic_id in request body
            if "clinic_id" not in data:
                return Response(
                    {"detail": "clinic_id is required for appointment creation."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

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
        appointment = self.get_object(pk, request.user.clinic_profile)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    def put(self, request, pk):
        appointment = self.get_object(pk, request.user.clinic_profile)
        data = request.data.copy()
        data["clinic"] = request.user.clinic_profile.id
        serializer = AppointmentSerializer(appointment, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        appointment = self.get_object(pk, request.user.clinic_profile)
        data = request.data.copy()
        data["clinic"] = request.user.clinic_profile.id
        serializer = AppointmentSerializer(appointment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        appointment = self.get_object(pk, request.user.clinic_profile)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

