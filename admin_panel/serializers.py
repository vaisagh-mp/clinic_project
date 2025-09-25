from rest_framework import serializers
from datetime import date
from .models import Clinic
from clinic_panel.models import Doctor, Patient, Appointment
from accounts.models import User

# -------------------- Clinic --------------------
class ClinicSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Clinic
        fields = [
            "id", "name", "description", "address", "phone_number",
            "email", "website", "type", "status", "user",
            "username", "password"
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

# -------------------- Doctor --------------------
class DoctorSerializer(serializers.ModelSerializer):
    # Nested fields
    user = serializers.SerializerMethodField()
    clinic = serializers.SerializerMethodField()

    # Make credentials optional
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Doctor
        fields = [
            "id", "clinic", "user",
            "profile_image", "name", "username", "password",
            "phone_number", "email", "dob",
            "years_of_experience", "medical_license_number",
            "blood_group", "gender", "address", "specialization"
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

    def get_clinic(self, obj):
        if obj.clinic:
            return {
                "id": obj.clinic.id,
                "name": obj.clinic.name,
            }
        return None

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=username,
            password=password,
            role="DOCTOR"
        )
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

    def update(self, instance, validated_data):
        # Pop optional credentials
        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)

        # Only update credentials if provided
        if instance.user:
            if username or password:
                if username:
                    instance.user.username = username
                if password:
                    instance.user.set_password(password)
                instance.user.save()

        return super().update(instance, validated_data)
# -------------------- Patient --------------------
class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id", "first_name", "last_name", "email", "phone_number",
            "dob", "age", "gender", "blood_group", "address", "care_of", "clinic"
        ]
        read_only_fields = ["age"]

    def get_age(self, obj):
        if not obj.dob:
            return None
        today = date.today()
        return today.year - obj.dob.year - (
            (today.month, today.day) < (obj.dob.month, obj.dob.day)
        )

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request.user, "clinic_profile"):
            validated_data["clinic"] = request.user.clinic_profile
        return super().create(validated_data)
# -------------------- Appointment --------------------
class AppointmentSerializer(serializers.ModelSerializer):
    clinic = ClinicSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    created_by = serializers.StringRelatedField()  # shows __str__ of user

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ["created_by", "appointment_id"]

    def validate(self, data):
        appointment_date = data.get("appointment_date")
        if appointment_date and appointment_date < date.today():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return data

