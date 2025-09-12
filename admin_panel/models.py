from django.db import models
from django.utils import timezone
from accounts.models import User

class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 

class Clinic(BaseModel):
    CLINIC_TYPES = [
        ("GENERAL", "General"),
        ("MULTISPECIALTY", "Multispecialty"),
        ("DENTAL", "Dental"),
        ("EYE", "Eye"),
        ("PEDIATRIC", "Pediatric"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("SUSPENDED", "Suspended"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=50, choices=CLINIC_TYPES, default="GENERAL")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="clinic_profile"
    )

    def __str__(self):
        return self.name
