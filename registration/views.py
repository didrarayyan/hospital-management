from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Patient, Appointment, Doctor
from .forms import PatientRegistrationForm, AppointmentForm, DoctorForm

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
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
            form.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'registration/book_appointment.html', {'form': form})

class PatientListView(ListView):
    model = Patient
    template_name = 'registration/patient_list.html'
    context_object_name = 'patients'
    ordering = ['-registration_date']

class AppointmentListView(ListView):
    model = Appointment
    template_name = 'registration/appointment_list.html'
    context_object_name = 'appointments'
    ordering = ['appointment_date']

class DoctorListView(ListView):
    model = Doctor
    template_name = 'registration/doctor_list.html'
    context_object_name = 'doctors'
    ordering = ['last_name', 'first_name']

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
        return context
