"""Connect receipt lifecycle signals to reward issuance."""

from django.dispatch import receiver

from Apps.receipts.signals import receipt_rejected, receipt_verified


@receiver(receipt_verified)
def on_receipt_verified(sender, receipt, **kwargs):
    from Apps.rebates.services import issue_reward

    issue_reward(receipt)


@receiver(receipt_rejected)
def on_receipt_rejected(sender, receipt, **kwargs):
    from Apps.rebates.services import void_reservation_on_rejection

    void_reservation_on_rejection(receipt)
