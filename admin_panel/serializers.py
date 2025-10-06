from rest_framework import serializers
from datetime import date
from .models import Clinic
from clinic_panel.models import Doctor, Patient, Appointment
from accounts.models import User

# -------------------- Doctor --------------------
class DoctorSerializer(serializers.ModelSerializer):
    # Accept clinic ID for writes
    clinic = serializers.PrimaryKeyRelatedField(
        queryset=Clinic.objects.all()
    )
    user = serializers.SerializerMethodField()

    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Doctor
        fields = [
            "id", "clinic", "user",
            "profile_image", "name", "username", "password",
            "phone_number", "email", "dob",
            "years_of_experience", "medical_license_number",
            "blood_group", "gender", "address", "specialization",
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
        """Customize output for clinic to show {id, name} instead of just ID"""
        rep = super().to_representation(instance)
        if instance.clinic:
            rep["clinic"] = {
                "id": instance.clinic.id,
                "name": instance.clinic.name,
            }
        return rep

    def create(self, validated_data):
        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)

        if not username or not password:
            raise serializers.ValidationError(
                {"detail": "Username and password are required to create a doctor."}
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            role="DOCTOR"
        )
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor


    def update(self, instance, validated_data):
        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)

        if instance.user:
            if username:
                instance.user.username = username
            if password:
                instance.user.set_password(password)
            instance.user.save()

        return super().update(instance, validated_data)
    
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
