from django.contrib import admin
from .models import Consultation, Prescription


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "created_at")
    search_fields = ("doctor__user__username", "patient__name")
    list_filter = ("doctor", "patient", "created_at")

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("medicine_name", "dosage", "frequency", "duration", "timings", "consultation")
    list_filter = ("frequency", "timings")
    search_fields = ("medicine_name", "dosage", "duration")
    autocomplete_fields = ("consultation",) 
