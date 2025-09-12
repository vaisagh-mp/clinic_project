from django.contrib import admin
from .models import Clinic


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone_number")
    search_fields = ("name", "address", "phone_number")
