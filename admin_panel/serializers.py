from rest_framework import serializers
import json
from django.http import QueryDict
from django.db.models import Max
from datetime import date
from .models import Clinic
from clinic_panel.models import Doctor, Patient, Appointment, Education, Certification, PatientAttachment
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

    def validate_email(self, value):
        """Ensure email is unique across users."""
        qs = User.objects.filter(email=value)
        if self.instance and self.instance.user:
            qs = qs.exclude(id=self.instance.user.id)
        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        """✅ Ensure username and password are provided during creation."""
        if not self.instance:  # Only on create
            if not data.get("username"):
                raise serializers.ValidationError({"username": "This field is required."})
            if not data.get("password"):
                raise serializers.ValidationError({"password": "This field is required."})
        return data

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        educations_data = validated_data.pop("educations", [])
        certifications_data = validated_data.pop("certifications", [])

        email = validated_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

        user = User.objects.create_user(username=username, password=password, email=email, role="DOCTOR")
        doctor = Doctor.objects.create(user=user, **validated_data)

        for edu in educations_data:
            Education.objects.create(doctor=doctor, **edu)
        for cert in certifications_data:
            Certification.objects.create(doctor=doctor, **cert)

        return doctor

    def update(self, instance, validated_data):
        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)
        educations_data = validated_data.pop("educations", None)
        certifications_data = validated_data.pop("certifications", None)

        email = validated_data.get("email")
        if email and instance.user:
            qs = User.objects.filter(email=email).exclude(id=instance.user.id)
            if qs.exists():
                raise serializers.ValidationError({"email": "A user with this email already exists."})

        if instance.user:
            if username:
                instance.user.username = username
            if password:
                instance.user.set_password(password)
            instance.user.save()

        instance = super().update(instance, validated_data)

        if educations_data is not None:
            instance.educations.all().delete()
            for edu in educations_data:
                Education.objects.create(doctor=instance, **edu)

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

    def validate_email(self, value):
        """Ensure email is unique across Users."""
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        # Ensure email is unique before creating user
        email = validated_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
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

class PatientAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientAttachment
        fields = ["id", "file", "uploaded_at"]


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(read_only=True)
    clinic = serializers.SerializerMethodField(read_only=True)

    # Read-only attachments
    attachments = PatientAttachmentSerializer(
        many=True,
        read_only=True
    )

    # Write-only multiple file upload
    # files = serializers.ListField(
    #     child=serializers.FileField(),
    #     write_only=True,
    #     required=False,
    #     allow_empty=True
    # )

    class Meta:
        model = Patient
        fields = [
            # Core
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "address",

            # Optional personal
            "email",
            "dob",
            "age",
            "gender",
            "blood_group",
            "care_of",

            # Newly added optional fields
            "guardian_name",
            "occupation",
            "daily_medication",
            "drug_allergy",
            "relative_name",
            "relationship_with_patient",
            "file_number",

            # System / relations
            "clinic",
            "attachments",  # response
            "files",        # request
        ]

        read_only_fields = [
            "id",
            "age",
            "clinic",
            "attachments",
        ]

    # -------------------------------------------------
    # 🔧 ADD THIS METHOD EXACTLY HERE (CLASS LEVEL)
    # -------------------------------------------------
    def to_internal_value(self, data):
        """
        Safely handle multipart PATCH/PUT with files.
        Avoid deepcopy of file objects.
        """

        # Only handle QueryDict (multipart/form-data)
        if isinstance(data, QueryDict):
            mutable_data = data.copy()  # QueryDict copy (safe)
            mutable_data._mutable = True

            files = data.getlist("files")

            # Keep only valid uploaded files
            valid_files = [f for f in files if hasattr(f, "read")]

            if valid_files:
                mutable_data.setlist("files", valid_files)
            else:
                mutable_data.pop("files", None)

            data = mutable_data

        return super().to_internal_value(data)

    # -------------------------
    # Computed Fields
    # -------------------------
    def get_age(self, obj):
        if not obj.dob:
            return None
        today = date.today()
        return today.year - obj.dob.year - (
            (today.month, today.day) < (obj.dob.month, obj.dob.day)
        )

    def get_clinic(self, obj):
        return obj.clinic.id if obj.clinic else None

    # -------------------------
    # Create with files
    # -------------------------
    def create(self, validated_data):
        request = self.context.get("request")
        files = validated_data.pop("files", [])

        user = request.user if request else None
        clinic = None

        if user:
            # Superadmin
            if getattr(user, "role", "").lower() == "superadmin":
                clinic_id = (
                    request.query_params.get("clinic_id")
                    or request.data.get("clinic")
                )
                if clinic_id:
                    clinic = Clinic.objects.filter(id=clinic_id).first()

            # Clinic admin / staff
            elif hasattr(user, "clinic_profile"):
                clinic = user.clinic_profile

            # Doctor
            elif hasattr(user, "doctor_profile"):
                clinic = getattr(user.doctor_profile, "clinic", None)

        if not clinic:
            raise serializers.ValidationError(
                {"clinic": "Clinic not found or unauthorized"}
            )

        validated_data["clinic"] = clinic


        # =====================================================
        # FILE NUMBER AUTO-GENERATION LOGIC  (ADD HERE 👇)
        # =====================================================
        file_number = validated_data.get("file_number")

        if not file_number:
            last_file = (
                Patient.objects
                .filter(
                    clinic=clinic,
                    file_number__regex=r'^\d+$'
                )
                .aggregate(max_no=Max("file_number"))
            )["max_no"]

            if last_file:
                next_file_number = int(last_file) + 1
            else:
                next_file_number = clinic.file_number_start

            validated_data["file_number"] = str(next_file_number)
        # =====================================================

        # Create patient
        patient = Patient.objects.create(**validated_data)

        # Save multiple attachments
        for file in files:
            PatientAttachment.objects.create(
                patient=patient,
                file=file
            )

        return patient

    # -------------------------
    # Update with files
    # -------------------------

    def update(self, instance, validated_data):
        """
        Handle PUT / PATCH updates including file uploads
        """
        files = validated_data.pop("files", [])
    
        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
    
        instance.save()
    
        # Save new attachments (append, do NOT remove old ones)
        for file in files:
            PatientAttachment.objects.create(
                patient=instance,
                file=file
            )
    
        return instance
    
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
