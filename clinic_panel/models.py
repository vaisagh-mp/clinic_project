from django.db import models
from django.conf import settings 
from django.utils.crypto import get_random_string
from django.utils import timezone
from accounts.models import User
from admin_panel.models import Clinic


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 


class ClinicTiming(BaseModel):
    DAYS_OF_WEEK = [
        ("MONDAY", "Monday"),
        ("TUESDAY", "Tuesday"),
        ("WEDNESDAY", "Wednesday"),
        ("THURSDAY", "Thursday"),
        ("FRIDAY", "Friday"),
        ("SATURDAY", "Saturday"),
        ("SUNDAY", "Sunday"),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="timings")
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.clinic.name} - {self.day}"


class ClinicAward(BaseModel):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="awards")
    title = models.CharField(max_length=200)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.title} ({self.year})"
    
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('O+', 'O+'), ('O-', 'O-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
]

class Doctor(BaseModel):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="doctors")
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DOCTOR'},
        related_name="doctor_profile"
    )

    # Personal Information
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    name = models.CharField(max_length=200, default="Unknown Doctor")
    username = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)
    medical_license_number = models.CharField(max_length=100, blank=True, null=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True,
    null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,blank=True,
    null=True)
    address = models.TextField(blank=True, null=True)

    specialization = models.CharField(max_length=200, blank=True,
    null=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

# ---------------- Educational Information ----------------
class Education(BaseModel):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="educations")
    degree = models.CharField(max_length=200)
    university = models.CharField(max_length=200)
    from_year = models.IntegerField()
    to_year = models.IntegerField()

    def __str__(self):
        return f"{self.degree} ({self.university})"

# ---------------- Certifications ----------------
class Certification(BaseModel):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=200)
    from_year = models.IntegerField()

    def __str__(self):
        return self.name



# ---------------- Patient ----------------


class Patient(BaseModel):

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    
    # Personal Information
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=20, default="")
    email = models.EmailField(default="")
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, default='O+')
    address = models.TextField(default="")
    care_of = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Guardian / Reference person for the patient"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    


class Appointment(BaseModel):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    appointment_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        default='' 
    )
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")

    appointment_date = models.DateField(default=timezone.now)
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True, null=True)

    # FIX: Use settings.AUTH_USER_MODEL instead of 'auth.User'
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            # Generate unique ID like APT-0001
            self.appointment_id = f"APT-{get_random_string(length=6).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.appointment_date} at {self.appointment_time}"
    