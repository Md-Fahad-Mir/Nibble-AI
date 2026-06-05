"""Run all notification generators (reminders + re-engagement + new offers).

Run on a schedule (cron/Celery beat later):
    python manage.py send_notifications
"""

from django.core.management.base import BaseCommand

from Apps.notifications import services


class Command(BaseCommand):
    help = "Generate reminder, re-engagement, and new-offer notifications."

    def handle(self, *args, **options):
        summary = services.run_all_generators()
        self.stdout.write(self.style.SUCCESS(f"Notifications sent: {summary}"))
