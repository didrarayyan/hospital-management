from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, FormView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.db import models
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import Patient, Appointment, Doctor, user as User, AuditLog
from .forms import (
    PatientRegistrationForm, 
    AppointmentForm, 
    DoctorForm, 
    SystemSettingsForm, 
    OTPAuthForm,
    SecuritySettingsForm
)
from .decorators import role_required, two_factor_required, audit_log

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'registration/dashboard.html'
    model = Patient
    context_object_name = 'recent_patients'
    
    def get_queryset(self):
        if self.request.user.is_doctor:
            return Patient.objects.filter(
                appointments__doctor=self.request.user.doctor
            ).distinct().order_by('-created_at')[:5]
        return Patient.objects.all().order_by('-created_at')[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        if self.request.user.is_doctor:
            doctor = self.request.user.doctor
            context.update({
                'total_patients': Patient.objects.filter(appointments__doctor=doctor).distinct().count(),
                'active_appointments': Appointment.objects.filter(
                    doctor=doctor,
                    status='SCHEDULED',
                    appointment_date__gte=today
                ).count(),
                'today_appointments': Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date__year=today.year,
                    appointment_date__month=today.month,
                    appointment_date__day=today.day
                ).count(),
                'monthly_appointments': Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date__month=today.month
                ).count(),
                'recent_appointments': Appointment.objects.filter(
                    doctor=doctor
                ).select_related('patient').order_by('-created_at')[:5]
            })
        else:
            context.update({
                'total_patients': Patient.objects.count(),
                'active_appointments': Appointment.objects.filter(
                    status='SCHEDULED',
                    appointment_date__gte=today
                ).count(),
                'available_doctors': Doctor.objects.filter(is_available=True).count(),
                'today_appointments': Appointment.objects.filter(
                    appointment_date__year=today.year,
                    appointment_date__month=today.month,
                    appointment_date__day=today.day
                ).count(),
                'recent_appointments': Appointment.objects.select_related(
                    'patient', 'doctor'
                ).order_by('-created_at')[:5],
                'recent_activities': AuditLog.objects.select_related('user')[:10]
            })
        return context

class TwoFactorSetupView(LoginRequiredMixin, FormView):
    template_name = 'registration/2fa_setup.html'
    form_class = OTPAuthForm
    success_url = reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.two_factor_enabled:
            device = TOTPDevice.objects.create(user=self.request.user, name='default')
            context['qr_code'] = device.config_url
        return context
    
    def form_valid(self, form):
        user = self.request.user
        user.two_factor_enabled = True
        user.save()
        messages.success(self.request, '2FA has been enabled successfully.')
        return super().form_valid(form)

@login_required
@role_required(['ADMIN', 'STAFF'])
@audit_log('register_patient')
def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f'Patient {patient.get_full_name()} registered successfully!')
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientRegistrationForm()
    return render(request, 'registration/register_patient.html', {'form': form})

@login_required
@role_required(['ADMIN', 'DOCTOR', 'STAFF'])
@audit_log('book_appointment')
@two_factor_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'SCHEDULED'
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm()
    return render(request, 'registration/book_appointment.html', {'form': form})

@login_required
@role_required(['ADMIN', 'DOCTOR'])
@audit_log('cancel_appointment')
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.status == 'COMPLETED':
        messages.error(request, 'Cannot cancel completed appointments.')
        return redirect('appointment_detail', pk=pk)
    
    appointment.status = 'CANCELLED'
    appointment.save()
    messages.success(request, 'Appointment cancelled successfully!')
    return redirect('appointment_list')

@method_decorator(role_required(['ADMIN', 'DOCTOR', 'STAFF']), name='dispatch')
class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'registration/patient_list.html'
    context_object_name = 'patients'
    ordering = ['-registration_date']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(email__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        context.update({
            'total_patients': Patient.objects.count(),
            'new_patients_month': Patient.objects.filter(
                registration_date__month=timezone.now().month
            ).count(),
            'active_appointments': Appointment.objects.filter(
                status='SCHEDULED',
                appointment_date=today
            ).count(),
            'search_query': self.request.GET.get('search', '')
        })
        return context

class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'registration/patient_detail.html'
    context_object_name = 'patient'

    @method_decorator(role_required(['ADMIN', 'DOCTOR', 'NURSE']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'appointments': self.object.appointments.all().order_by('-appointment_date'),
            'active_appointments': self.object.appointments.filter(status='SCHEDULED').count(),
            'medical_history': self.object.medical_history.all().order_by('-date'),
            'recent_visits': self.object.appointments.filter(
                status='COMPLETED'
            ).order_by('-appointment_date')[:5]
        })
        return context

class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientRegistrationForm
    template_name = 'registration/register_patient.html'

    @method_decorator(role_required(['ADMIN', 'DOCTOR']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Patient {self.object.get_full_name()} updated successfully!')
        return response

class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'registration/appointment_list.html'
    context_object_name = 'appointments'
    ordering = ['appointment_date']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context.update({
            'total_appointments': Appointment.objects.count(),
            'scheduled_appointments': Appointment.objects.filter(status='SCHEDULED').count(),
            'today_appointments': Appointment.objects.filter(
                appointment_date=today
            ).count(),
            'recent_appointments': Appointment.objects.select_related(
                'patient', 'doctor'
            ).order_by('-created_at')[:5]
        })
        return context

class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'registration/appointment_detail.html'
    context_object_name = 'appointment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_cancel'] = self.object.status == 'SCHEDULED'
        return context

class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'registration/book_appointment.html'
    success_url = reverse_lazy('appointment_list')

    @method_decorator(role_required(['ADMIN', 'DOCTOR']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Appointment updated successfully!')
        return super().form_valid(form)

@method_decorator(role_required(['ADMIN', 'DOCTOR']), name='dispatch') 
class DoctorListView(LoginRequiredMixin, ListView):
    model = Doctor
    template_name = 'registration/doctor_list.html'
    context_object_name = 'doctors'
    ordering = ['user__last_name', 'user__first_name']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        specialization = self.request.GET.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        return queryset.select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'specializations': Doctor.SPECIALIZATION_CHOICES,
            'total_doctors': Doctor.objects.count(),
            'available_doctors': Doctor.objects.filter(is_available=True).count(),
            'selected_specialization': self.request.GET.get('specialization', '')
        })
        return context

class DoctorCreateView(LoginRequiredMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'registration/doctor_form.html'
    success_url = reverse_lazy('doctor_list')
    
    @method_decorator(role_required(['ADMIN']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Doctor added successfully!')
        return super().form_valid(form)

class DoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'registration/doctor_form.html'
    success_url = reverse_lazy('doctor_list')
    
    @method_decorator(role_required(['ADMIN']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Doctor information updated successfully!')
        return super().form_valid(form)

class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = Doctor
    template_name = 'registration/doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'appointments': self.object.appointments.all().order_by('appointment_date'),
            'total_appointments': self.object.appointments.count(),
            'scheduled_appointments': self.object.appointments.filter(status='SCHEDULED').count()
        })
        return context

class SystemSettingsView(LoginRequiredMixin, FormView):
    template_name = 'registration/system_settings.html'
    form_class = SystemSettingsForm
    success_url = reverse_lazy('dashboard')

    @method_decorator(role_required(['ADMIN']))
    @method_decorator(two_factor_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_count': User.objects.count(),
            'two_factor_enabled_count': User.objects.filter(two_factor_enabled=True).count(),
            'audit_logs': AuditLog.objects.select_related('user')[:50],
            'system_statistics': self.get_system_statistics()
        })
        return context

    def get_system_statistics(self):
        return {
            'total_appointments': Appointment.objects.count(),
            'completed_appointments': Appointment.objects.filter(status='COMPLETED').count(),
            'active_patients': Patient.objects.filter(
                appointments__status='SCHEDULED'
            ).distinct().count(),
            'doctor_availability': Doctor.objects.filter(is_available=True).count()
        }

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'System settings updated successfully!')
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'registration/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'appointments': Appointment.objects.filter(
                doctor=self.request.user.doctor if hasattr(self.request.user, 'doctor') 
                else None
            ).order_by('-created_at')[:5],
            'recent_activities': AuditLog.objects.filter(
                user=self.request.user
            ).order_by('-action_time')[:10]
        })
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'registration/profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def get_form_class(self):
        if hasattr(self.request.user, 'doctor'):
            return DoctorForm
        return PatientRegistrationForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response

class SecuritySettingsView(LoginRequiredMixin, FormView):
    template_name = 'registration/security_settings.html'
    form_class = SecuritySettingsForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Security settings updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['two_factor_enabled'] = hasattr(self.request.user, 'totpdevice')
        return context
    
    class AppointmentReportView(LoginRequiredMixin, TemplateView):
        template_name = 'registration/reports/appointment_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'appointments': Appointment.objects.all().select_related('patient', 'doctor'),
            'total_appointments': Appointment.objects.count(),
            'completed_appointments': Appointment.objects.filter(status='COMPLETED').count(),
            'scheduled_appointments': Appointment.objects.filter(status='SCHEDULED').count(),
            'cancelled_appointments': Appointment.objects.filter(status='CANCELLED').count()
        })
        return context

class PatientReportView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/reports/patient_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'patients': Patient.objects.all().select_related('appointments'),
            'total_patients': Patient.objects.count(),
            'active_patients': Patient.objects.filter(appointments__status='SCHEDULED').distinct().count(),
            'new_patients_month': Patient.objects.filter(
                registration_date__month=timezone.now().month
            ).count(),
            'patients_by_gender': Patient.objects.values('gender').annotate(count=models.Count('id')),
            'patients_by_blood_group': Patient.objects.values('blood_group').annotate(count=models.Count('id'))
        })
        return context

class DoctorReportView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/reports/doctor_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'doctors': Doctor.objects.all().select_related('user'),
            'total_doctors': Doctor.objects.count(),
            'available_doctors': Doctor.objects.filter(is_available=True).count(),
            'doctors_by_specialization': Doctor.objects.values('specialization').annotate(count=models.Count('id')),
            'appointment_stats': Doctor.objects.annotate(
                total_appointments=models.Count('appointments'),
                completed_appointments=models.Count('appointments', filter=models.Q(appointments__status='COMPLETED')),
                scheduled_appointments=models.Count('appointments', filter=models.Q(appointments__status='SCHEDULED'))
            )
        })
        return context

class AppointmentReportView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/reports/appointment_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'appointments': Appointment.objects.all().select_related('patient', 'doctor'),
            'total_appointments': Appointment.objects.count(),
            'completed_appointments': Appointment.objects.filter(status='COMPLETED').count(),
            'scheduled_appointments': Appointment.objects.filter(status='SCHEDULED').count(),
            'cancelled_appointments': Appointment.objects.filter(status='CANCELLED').count()
        })
        return context

class PatientReportView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/reports/patient_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'patients': Patient.objects.all(),
            'total_patients': Patient.objects.count(),
            'active_patients': Patient.objects.filter(appointments__status='SCHEDULED').distinct().count(),
            'new_patients_month': Patient.objects.filter(
                registration_date__month=timezone.now().month
            ).count(),
            'patients_by_gender': Patient.objects.values('gender').annotate(count=models.Count('id')),
            'patients_by_blood_group': Patient.objects.values('blood_group').annotate(count=models.Count('id'))
        })
        return context

class DoctorReportView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/reports/doctor_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'doctors': Doctor.objects.all().select_related('user'),
            'total_doctors': Doctor.objects.count(),
            'available_doctors': Doctor.objects.filter(is_available=True).count(),
            'doctors_by_specialization': Doctor.objects.values('specialization').annotate(count=models.Count('id')),
            'appointment_stats': Doctor.objects.annotate(
                total_appointments=models.Count('appointments'),
                completed_appointments=models.Count('appointments', filter=models.Q(appointments__status='COMPLETED')),
                scheduled_appointments=models.Count('appointments', filter=models.Q(appointments__status='SCHEDULED'))
            )
        })
        return context
