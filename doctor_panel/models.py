from django.db import models
from django.utils import timezone
from clinic_panel.models import Patient, Doctor, Appointment
from billing.models import Procedure

class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 

class Consultation(BaseModel):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultation"
    )

    # General notes
    notes = models.TextField(blank=True, null=True)

    # Vitals
    temperature = models.CharField(max_length=10, blank=True, null=True)
    pulse = models.CharField(max_length=10, blank=True, null=True)
    respiratory_rate = models.CharField(max_length=10, blank=True, null=True)
    spo2 = models.CharField(max_length=10, blank=True, null=True)
    height = models.CharField(max_length=10, blank=True, null=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    bmi = models.CharField(max_length=10, blank=True, null=True)
    waist = models.CharField(max_length=10, blank=True, null=True)
    blood_pressure = models.CharField(max_length=20, blank=True, null=True)
    heart_rate = models.CharField(max_length=10, blank=True, null=True)

    # Complaint, Diagnosis, Advice, Investigation
    complaints = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    advices = models.TextField(blank=True, null=True)
    investigations = models.TextField(blank=True, null=True)

    allergies = models.TextField(blank=True, null=True, help_text="Mention any drug/food/environmental allergies")

    # Follow up
    next_consultation = models.DateField(blank=True, null=True)
    empty_stomach_required = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doctor} -> {self.patient} ({self.created_at.date()})"
    
class Prescription(BaseModel):
    FREQUENCY_CHOICES = [
        ('1-0-0', '1-0-0 (Morning only)'),
        ('0-1-0', '0-1-0 (Afternoon only)'),
        ('0-0-1', '0-0-1 (Night only)'),
        ('1-0-1', '1-0-1 (Morning & Night)'),
        ('1-1-1', '1-1-1 (Morning, Afternoon & Night)'),
        ('0-1-1', '0-1-1 (Afternoon & Night)'),
        ('1-1-0', '1-1-0 (Morning & Afternoon)'),
    ]

    TIMING_CHOICES = [
        ('BEFORE_MEAL', 'Before Meal'),
        ('AFTER_MEAL', 'After Meal'),
        ('ANYTIME', 'Anytime'),
    ]

    consultation = models.ForeignKey("Consultation", on_delete=models.CASCADE, related_name="prescriptions")

    # Either medicine or procedure
    medicine_name = models.CharField(max_length=100, blank=True, null=True)
    procedure = models.ForeignKey(Procedure, on_delete=models.SET_NULL, blank=True, null=True)
    dosage = models.CharField(max_length=50, blank=True, null=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    timings = models.CharField(max_length=20, choices=TIMING_CHOICES, blank=True, null=True)

    def __str__(self):
        if self.procedure:
            return f"{self.procedure.name}"
        return f"{self.medicine_name} - {self.frequency}, {self.get_timings_display() if self.timings else ''}"

