"""Billing logic: per-plan fee computation and subscription charging.

Design note: the *Plan* is the single source of truth for fees (a separate
FeeSchedule model would only invite drift). These helpers are the seam other
milestones call to compute what to charge.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from Apps.billing.models import Plan, Subscription
from Apps.common.dates import add_months
from Apps.common.money import ZERO, to_money
from Apps.wallets import services as wallet_services
from Apps.wallets.models import LedgerEntry


# ---------------------------------------------------------------------------
# Fee computation (used by rebates/reviews in later milestones)
# ---------------------------------------------------------------------------
def rebate_processing_fee(plan: Plan, reward_amount) -> Decimal:
    reward_amount = to_money(reward_amount)
    return to_money(reward_amount * plan.rebate_fee_percent / 100)


def review_fee(plan: Plan) -> Decimal:
    return to_money(plan.review_fee)


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------
def ensure_subscription(brand) -> Subscription | None:
    """Create an ACTIVE subscription for a brand that has a plan (idempotent)."""
    if brand.plan_id is None:
        return None
    now = timezone.now()
    subscription, _ = Subscription.objects.get_or_create(
        brand=brand,
        defaults={
            "plan": brand.plan,
            "status": Subscription.Status.ACTIVE,
            "current_period_start": now,
            "current_period_end": add_months(now, 1),
            "next_charge_at": now,  # charge on the next run
        },
    )
    return subscription


def ensure_all_subscriptions() -> int:
    from Apps.brands.models import Brand

    count = 0
    for brand in Brand.objects.filter(
        status=Brand.Status.ACTIVE, plan__isnull=False
    ):
        if ensure_subscription(brand) is not None:
            count += 1
    return count


@transaction.atomic
def _charge_one(subscription: Subscription, now) -> str:
    plan = subscription.plan
    amount = to_money(plan.monthly_price)

    # Free plan: nothing to charge, just roll the period forward.
    if amount <= ZERO:
        _advance_period(subscription, now, charged=ZERO)
        return "free"

    wallet = wallet_services.get_or_create_brand_wallet(subscription.brand)
    period_key = subscription.current_period_start.date().isoformat()
    try:
        wallet_services.debit(
            wallet=wallet,
            amount=amount,
            category=LedgerEntry.Category.SUBSCRIPTION,
            reference_type="subscription",
            reference_id=subscription.id,
            description=f"{plan.name} subscription",
            idempotency_key=f"subscription:{subscription.id}:{period_key}",
        )
    except wallet_services.InsufficientFunds:
        subscription.status = Subscription.Status.PAST_DUE
        subscription.save(update_fields=["status", "updated_at"])
        return "past_due"

    _advance_period(subscription, now, charged=amount)
    return "charged"


def _advance_period(subscription: Subscription, now, *, charged) -> None:
    subscription.status = Subscription.Status.ACTIVE
    subscription.last_charged_at = now
    subscription.total_charged = to_money(subscription.total_charged + charged)
    subscription.current_period_start = subscription.next_charge_at
    subscription.current_period_end = add_months(subscription.next_charge_at, 1)
    subscription.next_charge_at = add_months(subscription.next_charge_at, 1)
    subscription.save(
        update_fields=[
            "status",
            "last_charged_at",
            "total_charged",
            "current_period_start",
            "current_period_end",
            "next_charge_at",
            "updated_at",
        ]
    )


def charge_due_subscriptions(now=None) -> dict:
    """Charge every subscription whose next_charge_at has passed.

    Idempotent per billing period via the wallet debit's idempotency key.
    Returns a summary count by outcome.
    """
    # Ensure subscriptions exist *before* sampling `now`, so a freshly-created
    # subscription (next_charge_at set to its own creation time) reads as due.
    ensure_all_subscriptions()
    now = now or timezone.now()

    summary = {"charged": 0, "past_due": 0, "free": 0}
    due = Subscription.objects.filter(
        status__in=[Subscription.Status.ACTIVE, Subscription.Status.PAST_DUE],
        next_charge_at__lte=now,
    ).select_related("brand", "plan")
    for subscription in due:
        outcome = _charge_one(subscription, now)
        summary[outcome] += 1
    return summary
