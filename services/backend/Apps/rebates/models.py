"""Rebate redemption records.

When a receipt is verified the reward is issued: the reservation's escrow hold
is captured (brand pays the reward), the customer wallet is credited, and the
brand is debited the processing fee. ``Redemption`` is the business record;
``RewardIssuance`` records the exact ledger movements for audit.
"""

from django.conf import settings
from django.db import models

from Apps.common.models import BaseModel
from Apps.common.money import MONEY_FIELD


class Redemption(BaseModel):
    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"

    reservation = models.OneToOneField(
        "reservations.Reservation", on_delete=models.PROTECT, related_name="redemption"
    )
    receipt = models.ForeignKey(
        "receipts.Receipt", on_delete=models.PROTECT, related_name="redemptions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="redemptions"
    )
    brand = models.ForeignKey(
        "brands.Brand", on_delete=models.CASCADE, related_name="redemptions"
    )
    campaign = models.ForeignKey(
        "campaigns.Campaign", on_delete=models.PROTECT, related_name="redemptions"
    )

    reward_amount = models.DecimalField(**MONEY_FIELD)
    fee_amount = models.DecimalField(**MONEY_FIELD)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ISSUED
    )
    issued_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["brand", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Redemption {self.id} ({self.reward_amount})"


class RewardIssuance(BaseModel):
    """The financial execution of a redemption — pointers to ledger entries."""

    redemption = models.OneToOneField(
        Redemption, on_delete=models.CASCADE, related_name="issuance"
    )
    brand_reward_entry = models.ForeignKey(
        "wallets.LedgerEntry", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+",
    )
    customer_credit_entry = models.ForeignKey(
        "wallets.LedgerEntry", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+",
    )
    brand_fee_entry = models.ForeignKey(
        "wallets.LedgerEntry", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+",
    )
    hold = models.ForeignKey(
        "wallets.Hold", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+",
    )
    reward_amount = models.DecimalField(**MONEY_FIELD)
    fee_amount = models.DecimalField(**MONEY_FIELD)

    def __str__(self):
        return f"Issuance for {self.redemption_id}"
