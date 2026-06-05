"""Read-side queries for platform oversight (admin only, cross-brand)."""

from Apps.campaigns.models import Campaign
from Apps.common.models import AuditLog
from Apps.receipts.models import FraudFlag
from Apps.reviews.models import Review
from Apps.wallets.models import LedgerEntry

LIST_LIMIT = 200


def all_campaigns(*, status: str = ""):
    qs = Campaign.objects.select_related("brand", "product").all()
    if status:
        qs = qs.filter(status=status)
    return qs


def all_fraud_flags(*, resolved: str = ""):
    qs = FraudFlag.objects.select_related("user", "brand").all()
    if resolved in ("true", "false"):
        qs = qs.filter(resolved=(resolved == "true"))
    return qs[:LIST_LIMIT]


def all_users(*, suspended: str = "", flagged: str = ""):
    from Apps.accounts.models import User

    qs = User.objects.filter(is_deleted=False)
    if suspended == "true":
        qs = qs.filter(is_active=False)
    if flagged == "true":
        qs = qs.filter(fraud_flags__isnull=False).distinct()
    return qs[:LIST_LIMIT]


def all_transactions(*, category: str = ""):
    qs = LedgerEntry.objects.select_related("wallet").all()
    if category:
        qs = qs.filter(category=category)
    return qs[:LIST_LIMIT]


def held_reviews():
    return Review.objects.filter(status=Review.Status.HELD).select_related(
        "product", "review_campaign", "user"
    )


def audit_logs(*, target_type: str = "", actor_id: str = ""):
    qs = AuditLog.objects.all()
    if target_type:
        qs = qs.filter(target_type=target_type)
    if actor_id:
        qs = qs.filter(actor_id=actor_id)
    return qs[:LIST_LIMIT]
