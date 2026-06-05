"""Expire review sessions past their 7-day window and release their holds."""

from django.core.management.base import BaseCommand

from Apps.reviews import services


class Command(BaseCommand):
    help = "Expire due review sessions and release their escrow holds."

    def handle(self, *args, **options):
        count = services.expire_due_sessions()
        self.stdout.write(self.style.SUCCESS(f"Expired {count} review session(s)."))
