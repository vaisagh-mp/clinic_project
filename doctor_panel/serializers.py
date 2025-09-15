from rest_framework import serializers
from .models import Consultation, Prescription

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ["consultation"]

class ConsultationSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = Consultation
        fields = "__all__"
