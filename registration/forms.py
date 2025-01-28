from django import forms
from django.utils import timezone
from .models import Patient, Appointment, Doctor, user as User

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 
                 'phone_number', 'email', 'address', 'medical_history', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter full address'}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter medical history'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M'
        )
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'reason', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for appointment'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.filter(is_available=True)
        self.fields['patient'].queryset = Patient.objects.all().order_by('first_name')

    def clean_appointment_date(self):
        date = self.cleaned_data['appointment_date']
        if date < timezone.now():
            raise forms.ValidationError("Appointment date cannot be in the past")
        return date

class DoctorForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}))

    class Meta:
        model = Doctor
        fields = ['specialization', 'schedule', 'is_available']
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'schedule': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter work schedule'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        doctor = super().save(commit=False)
        if commit:
            user_data = {
                'first_name': self.cleaned_data['first_name'],
                'last_name': self.cleaned_data['last_name'],
                'email': self.cleaned_data['email'],
                'phone_number': self.cleaned_data['phone_number'],
                'role': 'DOCTOR'
            }
            if doctor.user_id:
                User.objects.filter(id=doctor.user_id).update(**user_data)
            else:
                user = User.objects.create(**user_data)
                doctor.user = user
            doctor.save()
        return doctor

class OTPAuthForm(forms.Form):
    otp_token = forms.CharField(
        label='OTP Token',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP token',
            'autocomplete': 'off'
        })
    )

    def clean_otp_token(self):
        token = self.cleaned_data['otp_token']
        if not token.isdigit():
            raise forms.ValidationError("OTP token must contain only numbers")
        return token

class SystemSettingsForm(forms.Form):
    site_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    maintenance_mode = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    session_timeout = forms.IntegerField(
        min_value=300,
        max_value=86400,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    enable_2fa = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    allowed_login_attempts = forms.IntegerField(
        min_value=3,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
