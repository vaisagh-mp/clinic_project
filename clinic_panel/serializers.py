from rest_framework import serializers
from datetime import date
from .models import Appointment, Patient
from doctor_panel.models import Prescription, Consultation
from doctor_panel.serializers import PatientSerializer, DoctorSerializer, ClinicSerializer


class ClinicPrescriptionListSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    procedure = serializers.SerializerMethodField()  # ✅ add this

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
            "created_at",
        ]

    def get_patient(self, obj):
        patient = obj.consultation.patient
        if patient.dob:
            today = date.today()
            age = today.year - patient.dob.year - (
                (today.month, today.day) < (patient.dob.month, patient.dob.day)
            )
        else:
            age = None

        return {
            "id": patient.id,
            "full_name": f"{patient.first_name} {patient.last_name}",
            "phone_number": patient.phone_number,
            "dob": patient.dob,
            "age": age,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
        }

    def get_doctor(self, obj):
        doctor = obj.consultation.doctor
        return {"id": doctor.id, "name": doctor.name}

    def get_procedure(self, obj):  # ✅ this returns readable name
        if obj.procedure:
            return {
                "id": obj.procedure.id,
                "name": obj.procedure.name,
            }
        return None


class ClinicConsultationSerializer(serializers.ModelSerializer):
    prescriptions = serializers.SerializerMethodField()
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    clinic = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = [
            "id", "doctor", "patient", "clinic", "appointment",
            "notes", "advices", "temperature", "pulse", "respiratory_rate",
            "spo2", "height", "weight", "bmi", "waist",
            "complaints", "diagnosis", "investigations", "allergies",
            "next_consultation", "empty_stomach_required", "prescriptions",
        ]

    def get_clinic(self, obj):
        if hasattr(obj.doctor, "clinic"):
            return ClinicSerializer(obj.doctor.clinic).data
        return None

    def get_prescriptions(self, obj):
        prescriptions = obj.prescriptions.all()
        return ClinicPrescriptionListSerializer(prescriptions, many=True).data




class PatientHistoryAppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)

    consultation = ClinicConsultationSerializer(read_only=True)

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
            "doctor",
            "clinic",
            "patient",
            "consultation",
        ]


class PatientHistorySerializer(serializers.ModelSerializer):
    appointments = PatientHistoryAppointmentSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "dob",
            "gender",
            "blood_group",
            "address",
            "care_of",
            "appointments",
        ]
