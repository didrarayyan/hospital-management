from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from faker import Faker
from django.db import models
from registration.models import user, Doctor, Patient, Appointment, AuditLog
import random
from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Seeds the database with realistic hospital data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        self.stdout.write('Starting database seeding...')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        user.objects.all().delete()
        Doctor.objects.all().delete()
        Patient.objects.all().delete()
        Appointment.objects.all().delete()
        AuditLog.objects.all().delete()

        # Create Admin user
        self.stdout.write('Creating admin user...')
        admin_user = user.objects.create(
            username='admin',
            email='admin@hospital.com',
            password=make_password('admin123'),
            first_name='System',
            last_name='Administrator',
            role='ADMIN',
            is_staff=True,
            is_superuser=True,
            phone_number='+1234567890'
        )

        # Create Staff user
        staff_user = user.objects.create(
            username='staff',
            email='staff@hospital.com',
            password=make_password('staff123'),
            first_name='Staff',
            last_name='User',
            role='STAFF',
            is_staff=True,
            phone_number='+1234567891'
        )

        # Create Doctors with Specializations
        self.stdout.write('Creating doctors...')
        specializations = [
            ('CARDIOLOGY', 'Heart and cardiovascular specialists'),
            ('DERMATOLOGY', 'Skin, hair, and nail specialists'),
            ('NEUROLOGY', 'Brain and nervous system specialists'),
            ('PEDIATRICS', 'Child healthcare specialists'),
            ('ORTHOPEDICS', 'Bone and joint specialists')
        ]
        
        doctors_data = []
        schedules = [
            "Monday-Friday: 9:00 AM - 5:00 PM",
            "Monday-Saturday: 10:00 AM - 6:00 PM",
            "Tuesday-Saturday: 8:00 AM - 4:00 PM",
            "Monday-Thursday: 7:00 AM - 3:00 PM",
            "Wednesday-Sunday: 11:00 AM - 7:00 PM"
        ]

        for i in range(10):
            spec = random.choice(specializations)
            doctor_user = user.objects.create(
                username=f'doctor{i+1}',
                email=f'doctor{i+1}@hospital.com',
                password=make_password('doctor123'),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='DOCTOR',
                phone_number=fake.phone_number(),
                is_active=True
            )
            
            doctor = Doctor.objects.create(
                user=doctor_user,
                specialization=spec[0],
                schedule=random.choice(schedules),
                is_available=random.choice([True, True, False])
            )
            doctors_data.append(doctor)

        # Create Patients
        self.stdout.write('Creating patients...')
        patients_data = []
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        medical_conditions = [
            'Hypertension',
            'Type 2 Diabetes',
            'Asthma',
            'Arthritis',
            'Migraine',
            'None',
            'Allergies'
        ]
        
        for i in range(100):
            age = random.randint(18, 90)
            dob = timezone.now() - timedelta(days=age*365)
            condition = random.choice(medical_conditions)
            history = f"Medical Condition: {condition}\n"
            if condition != 'None':
                history += f"Diagnosed: {fake.date_time_between(start_date='-5y', end_date='now').strftime('%Y-%m-%d')}\n"
                history += f"Treatment: Regular medication and check-ups\n"
                history += f"Notes: {fake.text(max_nb_chars=100)}"

            patient = Patient.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=dob,
                gender=random.choice(['M', 'F']),
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address(),
                blood_group=random.choice(blood_groups),
                medical_history=history,
                emergency_contact_name=fake.name(),
                emergency_contact_phone=fake.phone_number()
            )
            patients_data.append(patient)

        # Create Appointments
        self.stdout.write('Creating appointments...')
        reasons = [
            'Regular Check-up',
            'Follow-up Visit',
            'New Symptoms',
            'Prescription Renewal',
            'Test Results Review',
            'Annual Physical',
            'Vaccination',
            'Consultation'
        ]
        
        now = timezone.now()
        
        # Past appointments (all completed or cancelled)
        for _ in range(150):
            days_offset = random.randint(-60, -1)
            appointment_date = now + timedelta(days=days_offset)
            status = random.choice(['COMPLETED', 'COMPLETED', 'COMPLETED', 'CANCELLED'])
            
            appointment_time = appointment_date.time()  # Get time component

            Appointment.objects.create(
                patient=random.choice(patients_data),
                doctor=random.choice(doctors_data),
                appointment_date=appointment_date,
                appointment_time=appointment_time,  # Add this line
                reason=random.choice(reasons),
                status=status,
                notes=fake.text(max_nb_chars=100) if status == 'COMPLETED' else ''
            )

        # Future appointments (all scheduled or pending)
        for _ in range(50):
            days_offset = random.randint(1, 30)
            appointment_date = now + timedelta(days=days_offset)
            appointment_time = appointment_date.time()  # Get time component
            
            Appointment.objects.create(
                patient=random.choice(patients_data),
                doctor=random.choice(doctors_data),
                appointment_date=appointment_date,
                appointment_time=appointment_time,  # Add this line
                reason=random.choice(reasons),
                status=random.choice(['SCHEDULED', 'PENDING']),
                notes=''
            )
        # Today's appointments
        for _ in range(10):
            hours_offset = random.randint(0, 8)
            appointment_date = now.replace(hour=9, minute=0) + timedelta(hours=hours_offset)
            appointment_time = appointment_date.time()  # Get time component
            
            Appointment.objects.create(
                patient=random.choice(patients_data),
                doctor=random.choice(doctors_data),
                appointment_date=appointment_date,
                appointment_time=appointment_time,  # Add this line
                reason=random.choice(reasons),
                status='SCHEDULED',
                notes=''
            )
        # Create Audit Logs
        self.stdout.write('Creating audit logs...')
        actions = [
            'USER_LOGIN',
            'USER_LOGOUT',
            'PATIENT_REGISTRATION',
            'APPOINTMENT_BOOKING',
            'APPOINTMENT_COMPLETION',
            'APPOINTMENT_CANCELLATION',
            'PATIENT_UPDATE',
            'DOCTOR_UPDATE'
        ]
        
        for _ in range(300):
            days_offset = random.randint(-30, 0)
            action_time = now + timedelta(days=days_offset)
            
            AuditLog.objects.create(
                user=random.choice([admin_user, staff_user] + [d.user for d in doctors_data]),
                action=random.choice(actions),
                model_name=random.choice(['Patient', 'Appointment', 'Doctor', 'user']),
                object_id=random.randint(1, 100),
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                action_time=action_time
            )

        self.stdout.write(self.style.SUCCESS(f'''
Successfully seeded the database with:
- 1 Admin user (username: admin, password: admin123)
- 1 Staff user (username: staff, password: staff123)
- {len(doctors_data)} Doctors
- {len(patients_data)} Patients
- {Appointment.objects.count()} Appointments
- {AuditLog.objects.count()} Audit Log entries
'''))