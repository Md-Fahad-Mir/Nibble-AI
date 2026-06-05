"""Expire reservations past their 7-day window and release their wallet holds.

Run manually or via cron until Celery Beat is introduced (~M12):
    python manage.py expire_reservations
"""

from django.core.management.base import BaseCommand

from Apps.reservations import services


class Command(BaseCommand):
    help = "Expire due reservations and release their escrow holds."

    def handle(self, *args, **options):
        count = services.expire_due_reservations()
        self.stdout.write(self.style.SUCCESS(f"Expired {count} reservation(s)."))
