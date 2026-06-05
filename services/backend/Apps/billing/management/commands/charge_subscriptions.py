"""Charge due brand subscriptions.

Run manually or via cron until Celery Beat is introduced (~M12):
    python manage.py charge_subscriptions
"""

from django.core.management.base import BaseCommand

from Apps.billing import services


class Command(BaseCommand):
    help = "Charge all brand subscriptions whose billing period is due."

    def handle(self, *args, **options):
        summary = services.charge_due_subscriptions()
        self.stdout.write(
            self.style.SUCCESS(
                "Subscriptions processed — "
                f"charged: {summary['charged']}, "
                f"past_due: {summary['past_due']}, "
                f"free: {summary['free']}"
            )
        )
