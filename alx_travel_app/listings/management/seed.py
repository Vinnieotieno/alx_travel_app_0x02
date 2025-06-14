from django.core.management.base import BaseCommand
from listings.models import Listing
import random

class Command(BaseCommand):
    help = 'Seed the database with sample listings.'

    def handle(self, *args, **kwargs):
        sample_titles = ['Cozy Cabin', 'Beach House', 'Modern Apartment', 'Luxury Villa']
        sample_locations = ['Nairobi', 'Mombasa', 'Kampala', 'Zanzibar']

        for _ in range(10):
            Listing.objects.create(
                title=random.choice(sample_titles),
                description="A wonderful place to stay.",
                location=random.choice(sample_locations),
                price=random.randint(50, 500)
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded 10 listings."))
