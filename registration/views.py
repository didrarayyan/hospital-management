from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Patient, Appointment, Doctor
from .forms import PatientRegistrationForm, AppointmentForm, DoctorForm

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient registered successfully!')
            return redirect('patient_list')
    else:
        form = PatientRegistrationForm()
    return render(request, 'registration/register_patient.html', {'form': form})

def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'SCHEDULED'
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'registration/book_appointment.html', {'form': form})

def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'CANCELLED'
    appointment.save()
    messages.success(request, 'Appointment cancelled successfully!')
    return redirect('appointment_list')

class PatientListView(ListView):
    model = Patient
    template_name = 'registration/patient_list.html'
    context_object_name = 'patients'
    ordering = ['-registration_date']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_patients'] = Patient.objects.count()
        context['new_patients_month'] = Patient.objects.filter(
            registration_date__month=timezone.now().month
        ).count()
        context['active_appointments'] = Appointment.objects.filter(
            status='SCHEDULED'
        ).count()
        return context

class PatientDetailView(DetailView):
    model = Patient
    template_name = 'registration/patient_detail.html'
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = self.object.appointments.all().order_by('-appointment_date')
        context['active_appointments'] = self.object.appointments.filter(status='SCHEDULED').count()
        return context

class PatientUpdateView(UpdateView):
    model = Patient
    form_class = PatientRegistrationForm
    template_name = 'registration/register_patient.html'
    success_url = reverse_lazy('patient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Patient information updated successfully!')
        return super().form_valid(form)

class AppointmentListView(ListView):
    model = Appointment
    template_name = 'registration/appointment_list.html'
    context_object_name = 'appointments'
    ordering = ['appointment_date']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context['total_appointments'] = Appointment.objects.count()
        context['scheduled_appointments'] = Appointment.objects.filter(status='SCHEDULED').count()
        context['today_appointments'] = Appointment.objects.filter(
            appointment_date__date=today
        ).count()
        return context

class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'registration/book_appointment.html'
    success_url = reverse_lazy('appointment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Appointment updated successfully!')
        return super().form_valid(form)

class DoctorListView(ListView):
    model = Doctor
    template_name = 'registration/doctor_list.html'
    context_object_name = 'doctors'
    ordering = ['last_name', 'first_name']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_doctors'] = Doctor.objects.count()
        context['available_doctors'] = Doctor.objects.filter(is_available=True).count()
        context['total_appointments'] = Appointment.objects.count()
        return context

class DoctorCreateView(CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'registration/doctor_form.html'
    success_url = reverse_lazy('doctor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Doctor added successfully!')
        return super().form_valid(form)

class DoctorUpdateView(UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'registration/doctor_form.html'
    success_url = reverse_lazy('doctor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Doctor information updated successfully!')
        return super().form_valid(form)

class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'registration/doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = self.object.appointments.all().order_by('appointment_date')
        context['total_appointments'] = self.object.appointments.count()
        context['scheduled_appointments'] = self.object.appointments.filter(status='SCHEDULED').count()
        return context
