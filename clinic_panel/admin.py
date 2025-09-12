from django.contrib import admin
from .models import Doctor, Patient, Appointment


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "clinic", "specialization")
    search_fields = ("user__username", "specialization")
    list_filter = ("clinic",)


class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'email', 'dob', 'gender', 'blood_group', 'clinic')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email')
    list_filter = ('clinic', 'gender', 'blood_group')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'clinic', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('clinic', 'doctor', 'status', 'appointment_date')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__name')
    date_hierarchy = 'appointment_date'
    ordering = ('-appointment_date', '-appointment_time')
    readonly_fields = ('created_by',)

    fieldsets = (
        ('Appointment Details', {
            'fields': ('clinic', 'doctor', 'patient', 'appointment_date', 'appointment_time', 'status')
        }),
        ('Additional Info', {
            'fields': ('reason', 'notes', 'created_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Patient, PatientAdmin)