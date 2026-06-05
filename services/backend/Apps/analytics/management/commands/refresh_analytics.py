"""Refresh analytics snapshots (idempotent).

Run on a schedule (cron/Celery beat later):
    python manage.py refresh_analytics
"""

from django.core.management.base import BaseCommand

from Apps.analytics import services


class Command(BaseCommand):
    help = "Recompute campaign/product/platform analytics snapshots."

    def handle(self, *args, **options):
        summary = services.refresh_all()
        self.stdout.write(self.style.SUCCESS(f"Analytics refreshed: {summary}"))
