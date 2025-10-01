from rest_framework import serializers
from .models import Consultation, Prescription

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ["medicine_name", "dosage", "frequency", "timings", "duration"]

class ConsultationSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, write_only=True)  # allow nested input
    class Meta:
        model = Consultation
        fields = [
            "id", "doctor", "patient", "appointment",
            "notes", "temperature", "pulse", "respiratory_rate", "spo2",
            "height", "weight", "bmi", "waist",
            "complaints", "diagnosis", "advices", "investigations",
            "allergies", "next_consultation", "empty_stomach_required",
            "prescriptions",
        ]
        read_only_fields = ["doctor", "id", "created_at"]

    def create(self, validated_data):
        prescriptions_data = validated_data.pop("prescriptions", [])
        consultation = Consultation.objects.create(**validated_data)
        for presc in prescriptions_data:
            Prescription.objects.create(consultation=consultation, **presc)
        return consultation
