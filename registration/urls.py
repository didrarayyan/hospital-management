from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Authentication & Security
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='two_factor_setup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/security/', views.SecuritySettingsView.as_view(), name='security_settings'),
    
    # Patient Management
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/register/', views.register_patient, name='register_patient'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_edit'),
    
    # Doctor Management
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctors/add/', views.DoctorCreateView.as_view(), name='doctor_add'),
    path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctors/<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='doctor_edit'),
    
    # Appointment Management
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_edit'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    
    # Reports
    path('reports/appointments/', views.AppointmentReportView.as_view(), name='appointment_report'),
    path('reports/patients/', views.PatientReportView.as_view(), name='patient_report'),
    path('reports/doctors/', views.DoctorReportView.as_view(), name='doctor_report'),
    
    # System Settings
    path('settings/', views.SystemSettingsView.as_view(), name='system_settings'),
]
