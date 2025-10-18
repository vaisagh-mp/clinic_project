from rest_framework import serializers
from .models import Consultation, Prescription
from admin_panel.serializers import PatientSerializer, DoctorSerializer, ClinicSerializer, Appointment
from datetime import date

class DoctorAppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    has_consultation = serializers.SerializerMethodField()
    consultation = serializers.SerializerMethodField()  # 👈 includes latest consultation if current is None
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
        return bool(Consultation.objects.filter(appointment=obj).exists())

    def get_consultation(self, obj):
        consultation = getattr(obj, "consultation", None)
    
        if not consultation and obj.patient:
            consultation = (
                Consultation.objects.filter(patient=obj.patient)
                .order_by("-created_at")
                .first()
            )
    
        if consultation:
            # Convert TextField string to Python list
            investigations = consultation.investigations
            if investigations:
                import json
                try:
                    investigations = json.loads(investigations)
                except Exception:
                    # If it's not valid JSON, wrap as a list
                    investigations = [investigations]
            else:
                investigations = []
    
            return {
                "complaints": consultation.complaints,
                "diagnosis": consultation.diagnosis,
                "advices": consultation.advices,
                "investigations": investigations,  # this is now always an array
                "created_at": consultation.created_at,
            }
        return None


    def get_allergies(self, obj):
        """
        Return allergies from the latest consultation for this patient
        """
        if not obj.patient:
            return None

        latest_consultation = (
            Consultation.objects.filter(patient=obj.patient)
            .order_by("-created_at")
            .first()
        )
        if latest_consultation and latest_consultation.allergies:
            return latest_consultation.allergies
        return None

    def get_last_visited(self, obj):
        """Return the latest consultation date for this patient."""
        if not obj.patient:
            return None

        latest_consultation = (
            Consultation.objects.filter(patient=obj.patient)
            .order_by("-created_at")
            .first()
        )
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
