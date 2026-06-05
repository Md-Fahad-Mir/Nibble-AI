"""Generate review opportunities when a receipt is verified."""

from django.dispatch import receiver

from Apps.receipts.signals import receipt_verified


@receiver(receipt_verified)
def on_receipt_verified(sender, receipt, **kwargs):
    from Apps.reviews.services import generate_opportunities

    generate_opportunities(receipt)
