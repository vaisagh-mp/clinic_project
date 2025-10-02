from rest_framework import serializers
from .models import Consultation, Prescription
from admin_panel.serializers import PatientSerializer, DoctorSerializer, ClinicSerializer

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ["medicine_name", "dosage", "frequency", "timings", "duration"]
        read_only_fields = ["consultation"]

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

