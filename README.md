# Hospital Management System

A robust Django-based hospital management system that handles patient registration, doctor profiles, and appointment scheduling.

## Features

- Patient Management
  - Registration
  - Medical History
  - Contact Information

- Doctor Management
  - Specialization Categories
  - Availability Status
  - Schedule Management
  - Profile Details

- Appointment System
  - Book Appointments
  - Track Status
  - View History

## Tech Stack

- Django
- PostgreSQL
- Bootstrap 5
- Font Awesome

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
pip install django psycopg2-binary Faker
```
4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
5. Create superuser
```bash
python manage.py createsuperuser
```
6. Generate sample data
```bash
python manage.py generate_doctors
```
7. Run the development server
```bash
python manage.py runserver
```
## Usage

- Access admin interface: http://127.0.0.1:8000/admin/
- View doctors list: http://127.0.0.1:8000/doctors/
- Book appointments: http://127.0.0.1:8000/book-appointment/
- Register patients: http://127.0.0.1:8000/register/

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Developed by Didra Rayyan H
License
MIT