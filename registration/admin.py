from django.contrib import admin
from .models import Patient, Appointment, Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'specialization', 'phone_number', 'email')
    search_fields = ('first_name', 'last_name', 'specialization')
    list_filter = ('specialization',)
    ordering = ('last_name', 'first_name')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'email', 'registration_date')
    search_fields = ('first_name', 'last_name', 'phone_number')
    list_filter = ('gender', 'registration_date')
    date_hierarchy = 'registration_date'
    ordering = ('-registration_date',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Medical Information', {
            'fields': ('medical_history',)
        }),
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name')
    date_hierarchy = 'appointment_date'
    ordering = ('appointment_date',)
    raw_id_fields = ('patient', 'doctor')
    list_per_page = 20