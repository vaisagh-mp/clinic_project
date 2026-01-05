from rest_framework import serializers
from .models import Consultation, Prescription
from clinic_panel.models import Doctor, Patient
from admin_panel.serializers import PatientSerializer, DoctorSerializer, ClinicSerializer, Appointment, PatientAttachmentSerializer
from datetime import date

class DoctorAppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    has_consultation = serializers.SerializerMethodField()
    consultation = serializers.SerializerMethodField()  # includes latest consultation
    allergies = serializers.SerializerMethodField()
    last_visited = serializers.SerializerMethodField()
    appointment_id = serializers.SerializerMethodField()

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
            "consultation",
            "allergies",
            "last_visited",
        ]

    def get_appointment_id(self, obj):
        return obj.appointment_id or f"APT-{obj.id}"

    def get_has_consultation(self, obj):
        return Consultation.objects.filter(appointment=obj).exists()

    def get_consultation(self, obj):
        if not obj.patient:
            return None

        # Get all consultations for the patient ordered by creation date descending
        consultations = Consultation.objects.filter(patient=obj.patient).order_by("-created_at")
        if not consultations.exists():
            return None

        # Start with the latest consultation
        latest = consultations.first()

        # Prepare fields with "carry forward" logic
        def get_field(field_name):
            # Return first non-empty value from latest to oldest consultation
            for c in consultations:
                value = getattr(c, field_name, None)
                if value:
                    if field_name == "investigations":
                        # Make sure investigations is always a list
                        import json
                        try:
                            return json.loads(value)
                        except Exception:
                            return [value]
                    return value
            return None

        return {
            "complaints": get_field("complaints") or "",
            "diagnosis": get_field("diagnosis") or "",
            "advices": get_field("advices") or "",
            "investigations": get_field("investigations") or [],
            "notes": get_field("notes") or "",
            "allergies": get_field("allergies") or "",
            "created_at": latest.created_at,
        }

    def get_allergies(self, obj):
        # Reuse the consultation logic for consistency
        consultation_data = self.get_consultation(obj)
        if consultation_data:
            return consultation_data.get("allergies", None)
        return None

    def get_last_visited(self, obj):
        if not obj.patient:
            return None

        latest_consultation = Consultation.objects.filter(patient=obj.patient).order_by("-created_at").first()
        if latest_consultation:
            return latest_consultation.created_at.date().isoformat()
        return None



class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ["medicine_name", "procedure", "dosage", "frequency", "timings", "duration"]
        read_only_fields = ["consultation"]

class PrescriptionListSerializer(serializers.ModelSerializer):
    procedure = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    clinic = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            "id",
            "medicine_name",
            "procedure",
            "dosage",
            "frequency",
            "timings",
            "duration",
            "consultation_id",
            "patient",
            "doctor",
            "clinic",
            "created_at",
        ]

    def _calculate_age(self, dob):
        if not dob:
            return None
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def get_procedure(self, obj):
        return obj.procedure.name if obj.procedure else None

    def get_patient(self, obj):
        patient = obj.consultation.patient
        return {
            "patient_id": patient.id,
            "full_name": f"{patient.first_name} {patient.last_name}",
            "phone_number": patient.phone_number,
            "dob": patient.dob,
            "age": self._calculate_age(patient.dob),
            "gender": patient.gender,
            "blood_group": patient.blood_group,
        }

    def get_doctor(self, obj):
        doctor = obj.consultation.doctor
        return {"id": doctor.id, "name": doctor.name}

    def get_clinic(self, obj):
        # Try doctor.clinic first
        doctor_clinic = getattr(obj.consultation.doctor, "clinic", None)
        if doctor_clinic:
            return {"id": doctor_clinic.id, "name": doctor_clinic.name}
        # Optional: fallback to appointment.clinic if Appointment has a clinic
        if obj.consultation.appointment and hasattr(obj.consultation.appointment, "clinic"):
            appt_clinic = obj.consultation.appointment.clinic
            if appt_clinic:
                return {"id": appt_clinic.id, "name": appt_clinic.name}
        return None

class ConsultationSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionListSerializer(many=True, read_only=True)
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    referred_to = DoctorSerializer(read_only=True)
    clinic = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = [
            # -------------------------
            # Core
            # -------------------------
            "id",
            "doctor",
            "patient",
            "clinic",
            "appointment",

            # -------------------------
            # General Notes
            # -------------------------
            "notes",

            # -------------------------
            # Vitals
            # -------------------------
            "temperature",
            "pulse",
            "respiratory_rate",
            "spo2",
            "height",
            "weight",
            "bmi",
            "waist",
            "blood_pressure",
            "heart_rate",

            # -------------------------
            # Clinical Information
            # -------------------------
            "complaints",
            "findings",
            "diagnosis",
            "investigations",

            # -------------------------
            # Treatment
            # -------------------------
            "treatment_plan",
            "treatment_done",
            "advices",

            # -------------------------
            # Allergies
            # -------------------------
            "allergies",

            # -------------------------
            # Referral
            # -------------------------
            "referred_to",
            "referral_notes",

            # -------------------------
            # Follow-up
            # -------------------------
            "next_consultation",
            "empty_stomach_required",

            # -------------------------
            # Prescriptions
            # -------------------------
            "prescriptions",
        ]

    def get_clinic(self, obj):
        # Try doctor.clinic first
        doctor_clinic = getattr(obj.doctor, "clinic", None)
        if doctor_clinic:
            return {"id": doctor_clinic.id, "name": doctor_clinic.name}
        # Optional: fallback to appointment.clinic
        if obj.appointment and hasattr(obj.appointment, "clinic"):
            appt_clinic = obj.appointment.clinic
            if appt_clinic:
                return {"id": appt_clinic.id, "name": appt_clinic.name}
        return None


class DoctorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "specialization"]


class AppointmentMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "appointment_id",
            "appointment_date",
            "appointment_time",
            "status",
            "reason",
        ]


class PrescriptionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            "id",
            "medicine_name",
            "dosage",
            "frequency",
            "timings",
            "duration",
        ]



class ConsultationMiniSerializer(serializers.ModelSerializer):
    doctor = DoctorMiniSerializer(read_only=True)
    prescriptions = PrescriptionMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Consultation
        fields = [
            "id",
            "doctor",
            "notes",
            "complaints",
            "diagnosis",
            "investigations",
            "advices",
            "allergies",
            "next_consultation",
            "created_at",
            "prescriptions",
        ]


class DoctorPatientAppointmentHistorySerializer(serializers.ModelSerializer):
    appointment = AppointmentMiniSerializer(source="*", read_only=True)
    consultation = ConsultationMiniSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "appointment",
            "consultation",
        ]

class DoctorPatientHistorySerializer(serializers.ModelSerializer):
    attachments = PatientAttachmentSerializer(many=True, read_only=True)
    consultations = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            # Patient core
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "dob",
            "gender",
            "blood_group",
            "file_number",

            # Medical context
            "daily_medication",
            "drug_allergy",

            # Files
            "attachments",

            # History
            "consultations",
        ]

    def get_consultations(self, obj):
        doctor = self.context["doctor"]

        appointments = (
            obj.appointments
            .filter(consultation__doctor=doctor)
            .select_related("consultation", "consultation__doctor")
            .prefetch_related("consultation__prescriptions")
        )

        return DoctorPatientAppointmentHistorySerializer(
            appointments,
            many=True
        ).data

