"""Publish 1–2★ reviews whose 30-day moderation hold has elapsed."""

from django.core.management.base import BaseCommand

from Apps.reviews import services


class Command(BaseCommand):
    help = "Publish held (1–2★) reviews past their 30-day hold window."

    def handle(self, *args, **options):
        count = services.release_held_reviews()
        self.stdout.write(self.style.SUCCESS(f"Released {count} held review(s)."))
