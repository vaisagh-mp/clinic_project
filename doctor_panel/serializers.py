from rest_framework import serializers
from .models import Consultation, Prescription
from admin_panel.serializers import PatientSerializer, DoctorSerializer, ClinicSerializer

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
        return {
            "patient_id": patient.id,
            "full_name": f"{patient.first_name} {patient.last_name}",
            "phone_number": patient.phone_number,
            "dob": patient.dob,
            "age": patient.age,
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
            "height", "weight", "bmi", "waist", "complaints", "diagnosis",
            "investigations", "allergies", "next_consultation", "empty_stomach_required",
            "prescriptions",
        ]

    def get_clinic(self, obj):
        if hasattr(obj.doctor, "clinic"):
            return ClinicSerializer(obj.doctor.clinic).data
        return None

