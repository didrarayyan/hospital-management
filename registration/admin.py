from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, Appointment, Doctor, AuditLog, user

@admin.register(user)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'two_factor_enabled']
    list_filter = ['role', 'is_active', 'two_factor_enabled']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'specialization', 'is_available', 'get_appointment_count']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']
    ordering = ['user__last_name', 'user__first_name']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Doctor Name'
    
    def get_appointment_count(self, obj):
        return obj.appointments.count()
    get_appointment_count.short_description = 'Total Appointments'

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'email', 'registration_date', 'get_photo']
    search_fields = ['first_name', 'last_name', 'phone_number']
    list_filter = ['gender', 'registration_date']
    date_hierarchy = 'registration_date'
    ordering = ('-registration_date',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'photo')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Medical Information', {
            'fields': ('medical_history',)
        }),
    )
    
    def get_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "No photo"
    get_photo.short_description = 'Photo'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'doctor']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__user__first_name']
    date_hierarchy = 'appointment_date'
    ordering = ('appointment_date',)
    raw_id_fields = ('patient', 'doctor')
    list_per_page = 20
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'appointment_date', 'status')
        }),
        ('Additional Information', {
            'fields': ('reason', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'action_time', 'ip_address']
    list_filter = ['action', 'model_name', 'action_time']
    search_fields = ['user__username', 'action', 'model_name']
    date_hierarchy = 'action_time'
    ordering = ('-action_time',)
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'action_time', 'ip_address', 'user_agent']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
