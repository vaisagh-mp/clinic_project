from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CLINIC', 'Clinic'),
        ('DOCTOR', 'Doctor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
