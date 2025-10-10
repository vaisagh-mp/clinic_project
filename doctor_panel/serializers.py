from rest_framework import serializers
from .models import Consultation, Prescription
from admin_panel.serializers import PatientSerializer, DoctorSerializer, ClinicSerializer, Appointment
from datetime import date

class DoctorAppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    has_consultation = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "appointment_id",
            "appointment_date",
            "appointment_time",
            "reason",
            "status",
            "notes",
            "patient",
            "clinic",
            "created_by",
            "has_consultation",
        ]

    def get_has_consultation(self, obj):
        return hasattr(obj, "consultation")



class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ["medicine_name", "dosage", "frequency", "timings", "duration"]
        read_only_fields = ["consultation"]

class PrescriptionListSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    clinic = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            "id", "medicine_name", "dosage", "frequency", "timings", "duration",
            "consultation_id", "patient", "doctor", "clinic", "created_at"
        ]

    def get_patient(self, obj):
        patient = obj.consultation.patient

        # Calculate age if dob exists
        if patient.dob:
            today = date.today()
            age = today.year - patient.dob.year - ((today.month, today.day) < (patient.dob.month, patient.dob.day))
        else:
            age = None

        return {
            "patient_id": patient.id,
            "full_name": f"{patient.first_name} {patient.last_name}",
            "phone_number": patient.phone_number,
            "dob": patient.dob,
            "age": age,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
        }
    
    def get_doctor(self, obj):
        return {
            "id": obj.consultation.doctor.id,
            "name": obj.consultation.doctor.name,
        }

    def get_clinic(self, obj):
        clinic = getattr(obj.consultation.doctor, "clinic", None)
        if clinic:
            return {
                "id": clinic.id,
                "name": clinic.name,
            }
        return None


class ConsultationSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    clinic = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = [
            "id", "doctor", "patient", "clinic", "appointment",
            "notes", "advices", "temperature", "pulse", "respiratory_rate", "spo2",
            "height", "weight", "bmi", "waist", "blood_pressure", "heart_rate",
            "complaints", "diagnosis", "investigations", "allergies",
            "next_consultation", "empty_stomach_required",
            "prescriptions",
        ]
        extra_kwargs = {
            "next_consultation": {"required": False, "allow_null": True},
        }

    def get_clinic(self, obj):
        if hasattr(obj.doctor, "clinic"):
            return ClinicSerializer(obj.doctor.clinic).data
        return None

