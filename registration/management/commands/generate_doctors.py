from django.core.management.base import BaseCommand
from registration.models import Doctor
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generates sample doctors'

    def handle(self, *args, **kwargs):
        fake = Faker()
        specializations = [choice[0] for choice in Doctor.SPECIALIZATION_CHOICES]
        
        for _ in range(50):
            # Generate a shorter phone number format
            phone = f"+1{fake.msisdn()[3:12]}"  # This ensures phone number is 10 digits + country code
            
            Doctor.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                specialization=random.choice(specializations),
                phone_number=phone,
                email=fake.email(),
                schedule=f"Monday-Friday: {random.randint(8,10)}:00 AM - {random.randint(4,6)}:00 PM",
                is_available=random.choice([True, False])
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated 50 sample doctors'))
