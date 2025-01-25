from django.urls import path
from . import views

urlpatterns = [
    # Patient URLs
    path('', views.PatientListView.as_view(), name='patient_list'),
    path('register/', views.register_patient, name='register_patient'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_edit'),
    
    # Appointment URLs
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_edit'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    
    # Doctor URLs
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctors/add/', views.DoctorCreateView.as_view(), name='doctor_add'),
    path('doctors/<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='doctor_edit'),
    path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
]
