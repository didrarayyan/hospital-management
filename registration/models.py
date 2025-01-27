from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('CARDIOLOGY', 'Cardiology'),
        ('DERMATOLOGY', 'Dermatology'),
        ('NEUROLOGY', 'Neurology'),
        ('PEDIATRICS', 'Pediatrics'),
        ('ORTHOPEDICS', 'Orthopedics'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    schedule = models.TextField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialization}"
    
    def get_full_name(self):
        return f"Dr. {self.first_name} {self.last_name}"
    
    def get_total_appointments(self):
        return self.appointments.count()
    
    def get_scheduled_appointments(self):
        return self.appointments.filter(status='SCHEDULED').count()
    
    def get_today_appointments(self):
        today = timezone.now().date()
        return self.appointments.filter(appointment_date__date=today).count()

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    date_of_birth = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Gender")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, verbose_name="Phone Number")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(verbose_name="Address")
    registration_date = models.DateTimeField(auto_now_add=True)
    medical_history = models.TextField(blank=True, verbose_name="Medical History")
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True, verbose_name="Patient Photo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-registration_date']
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_active_appointments(self):
        return self.appointments.filter(status='SCHEDULED').count()
    
    def get_total_appointments(self):
        return self.appointments.count()
    
    def get_age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('PENDING', 'Pending'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField(verbose_name="Appointment Date")
    reason = models.TextField(verbose_name="Reason for Visit")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True, verbose_name="Additional Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date']
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
    
    def __str__(self):
        return f"{self.patient} - {self.appointment_date}"
    
    def is_upcoming(self):
        return self.appointment_date > timezone.now()
    
    def get_status_color(self):
        status_colors = {
            'SCHEDULED': 'primary',
            'COMPLETED': 'success',
            'CANCELLED': 'danger',
            'PENDING': 'warning'
        }
        return status_colors.get(self.status, 'secondary')
