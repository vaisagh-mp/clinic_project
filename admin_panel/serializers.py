from rest_framework import serializers
import json
from datetime import date
from .models import Clinic
from clinic_panel.models import Doctor, Patient, Appointment, Education, Certification
from accounts.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ["id", "degree", "university", "from_year", "to_year"]
        extra_kwargs = {field: {"required": False} for field in fields}


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ["id", "name", "from_year"]
        extra_kwargs = {field: {"required": False} for field in fields}


class DoctorSerializer(serializers.ModelSerializer):
    clinic = serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all())
    user = serializers.SerializerMethodField()

    username = serializers.CharField(write_only=True, required=False)  # optional on update
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)  # optional on update

    educations = EducationSerializer(many=True, required=False)
    certifications = CertificationSerializer(many=True, required=False)

    class Meta:
        model = Doctor
        fields = [
            "id", "clinic", "user",
            "profile_image", "name", "username", "password",
            "phone_number", "email", "dob",
            "years_of_experience", "medical_license_number",
            "blood_group", "gender", "address", "specialization",
            "educations", "certifications",
        ]
        read_only_fields = ["user"]

    def get_user(self, obj):
        if obj.user:
            return {
                "id": obj.user.id,
                "username": obj.user.username,
                "first_name": obj.user.first_name,
                "last_name": obj.user.last_name,
            }
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.clinic:
            rep["clinic"] = {"id": instance.clinic.id, "name": instance.clinic.name}
        rep["educations"] = EducationSerializer(instance.educations.all(), many=True).data
        rep["certifications"] = CertificationSerializer(instance.certifications.all(), many=True).data
        return rep

    def create(self, validated_data):
        # Only required on create
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        
        educations_data = validated_data.pop("educations", [])
        certifications_data = validated_data.pop("certifications", [])

        user = User.objects.create_user(username=username, password=password, role="DOCTOR")
        doctor = Doctor.objects.create(user=user, **validated_data)

        for edu in educations_data:
            Education.objects.create(doctor=doctor, **edu)
        for cert in certifications_data:
            Certification.objects.create(doctor=doctor, **cert)

        return doctor

    def update(self, instance, validated_data):
        # Update username/password only if provided
        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)
        educations_data = validated_data.pop("educations", None)
        certifications_data = validated_data.pop("certifications", None)

        if instance.user:
            if username:
                instance.user.username = username
            if password:
                instance.user.set_password(password)
            instance.user.save()

        instance = super().update(instance, validated_data)

        # Update educations if provided
        if educations_data is not None:
            instance.educations.all().delete()
            for edu in educations_data:
                Education.objects.create(doctor=instance, **edu)

        # Update certifications if provided
        if certifications_data is not None:
            instance.certifications.all().delete()
            for cert in certifications_data:
                Certification.objects.create(doctor=instance, **cert)

        return instance


# -------------------- Clinic --------------------
class ClinicSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    doctors = DoctorSerializer(many=True, read_only=True)

    class Meta:
        model = Clinic
        fields = [
            "id", "name", "description", "address", "phone_number",
            "email", "website", "type", "status", "user",
            "username", "password", "doctors"
        ]
        read_only_fields = ["user"]

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=username,
            password=password,
            role="CLINIC"
        )

        clinic = Clinic.objects.create(user=user, **validated_data)
        return clinic

    def update(self, instance, validated_data):
        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)

        if instance.user:
            if username:
                instance.user.username = username
            if password:
                instance.user.set_password(password)
            if username or password:
                instance.user.save()

        return super().update(instance, validated_data)

# -------------------- Patient --------------------
class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(read_only=True)
    clinic = serializers.SerializerMethodField(read_only=True)
    attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Patient
        fields = [
            "id", "first_name", "last_name", "email", "phone_number",
            "dob", "age", "gender", "blood_group", "address",
            "care_of", "clinic", "attachment"
        ]
        read_only_fields = ["age", "clinic"]

    def get_age(self, obj):
        if not obj.dob:
            return None
        today = date.today()
        return today.year - obj.dob.year - (
            (today.month, today.day) < (obj.dob.month, obj.dob.day)
        )

    def get_clinic(self, obj):
        if obj.clinic:
            return {
                "id": obj.clinic.id,
                "name": obj.clinic.name
            }
        return None

    def create(self, validated_data):
        request = self.context.get("request")

        # Ensure the user has a clinic_profile
        clinic_profile = getattr(request.user, "clinic_profile", None)
        if not clinic_profile:
            raise serializers.ValidationError("User does not have an associated clinic.")

        validated_data["clinic"] = clinic_profile

        return super().create(validated_data)

# -------------------- Appointment --------------------
class AppointmentSerializer(serializers.ModelSerializer):
    clinic = ClinicSerializer(read_only=True)  # already good
    doctor = DoctorSerializer(read_only=True)  # change to nested serializer
    patient = PatientSerializer(read_only=True)  # change to nested serializer
    created_by = serializers.StringRelatedField(read_only=True)

    # For creating/updating, accept IDs
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source="doctor"
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source="patient"
    )
    clinic_id = serializers.PrimaryKeyRelatedField(
        queryset=Clinic.objects.all(), write_only=True, source="clinic"
    )

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ["created_by", "appointment_id"]


class ClinicAppointmentSerializer(serializers.ModelSerializer):
    # Nested serializers for GET
    clinic = ClinicSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    # Write-only fields for POST/PUT (clinic auto-assigned)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source="doctor"
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source="patient"
    )

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ["created_by", "appointment_id", "clinic"]

    def create(self, validated_data):
        clinic = self.context.get("clinic")
        if not clinic:
            raise serializers.ValidationError("Clinic context is required.")
        validated_data["clinic"] = clinic
        return super().create(validated_data)
