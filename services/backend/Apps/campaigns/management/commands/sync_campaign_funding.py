"""Pause underfunded campaigns and resume them once the wallet is funded.

Run manually or via cron until Celery Beat is introduced (~M12):
    python manage.py sync_campaign_funding
"""

from django.core.management.base import BaseCommand

from Apps.brands.models import Brand
from Apps.campaigns import services


class Command(BaseCommand):
    help = "Sync campaign active/paused state with brand wallet funding."

    def handle(self, *args, **options):
        paused = resumed = 0
        for brand in Brand.objects.filter(status=Brand.Status.ACTIVE):
            summary = services.sync_funding_state(brand)
            paused += summary["paused"]
            resumed += summary["resumed"]
        self.stdout.write(
            self.style.SUCCESS(
                f"Funding sync complete — paused: {paused}, resumed: {resumed}"
            )
        )
