# Hospital Management System

A robust Django-based hospital management system that handles patient registration, doctor profiles, and appointment scheduling with an enhanced modern dashboard UI.

## Features

- Dashboard
  - Real-time Statistics Overview
  - Quick Action Buttons
  - Recent Activities Feed
  - Today's Appointments Counter
  - Active Appointments Tracker
  - Available Doctors Status

- Patient Management
  - Registration with Photo Upload
  - Medical History Tracking
  - Contact Information
  - Appointment History
  - Search Functionality
  - Pagination Support

- Doctor Management
  - Specialization Categories
  - Real-time Availability Status
  - Schedule Management
  - Profile Details
  - Patient Load Tracking
  - Appointment Overview

- Appointment System
  - Book Appointments
  - Track Status (Scheduled/Completed/Cancelled)
  - View History
  - Quick Actions
  - Date and Time Selection
  - Conflict Prevention

- Security Features
  - Role-based Access Control
  - Two-Factor Authentication
  - Session Management
  - Audit Logging
  - Secure Password Handling

- Modern UI/UX
  - Responsive Design
  - Bootstrap 5 Components
  - Interactive Data Tables
  - Status Indicators
  - Clean Navigation
  - Mobile-Friendly Interface

## Tech Stack

- Django 5.1
- PostgreSQL
- Bootstrap 5
- SCSS/Sass
- Font Awesome
- JavaScript
- Django OTP
- Widget Tweaks

## Installation

1. Clone the repository
```bash
git clone https://github.com/didrarayyan/hospital-management.git
```
2. Create virtual environment
```bash
python -m venv env
source env/bin/activate
```
3. Install dependencies
```bash
pip install django psycopg2-binary Faker pillow django-sass-processor libsass django-compressor
```
4. Configure PostgreSQL database
```bash
sudo -u postgres psql
CREATE DATABASE hospital_db;
CREATE USER hospital_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hospital_db TO hospital_user;
```
5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
6. Create superuser
```bash
python manage.py createsuperuser
```
7. Generate sample data
```bash
python manage.py generate_doctors
```
8. Run the development server
```bash
python manage.py runserver
```
## Usage

- Access dashboard: http://127.0.0.1:8000/
- View patients list: http://127.0.0.1:8000/patients/
- View doctors list: http://127.0.0.1:8000/doctors/
- View appointments: http://127.0.0.1:8000/appointments/
- Register patients: http://127.0.0.1:8000/register-patient/
- Book appointments: http://127.0.0.1:8000/book-appointment/

## Features Highlights

- Enhanced UI with modern dashboard
- Real-time statistics tracking
- Photo upload capability
- Appointment status tracking
- Recent activities feed
- Quick action buttons
- Interactive data tables
- Responsive design

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT

Developed by Didra Rayyan H