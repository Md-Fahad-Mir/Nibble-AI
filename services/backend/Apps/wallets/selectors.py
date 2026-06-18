"""Read-side queries for wallets."""

from Apps.wallets.models import LedgerEntry, Wallet


def get_brand_wallet(brand) -> Wallet | None:
    return Wallet.objects.filter(brand=brand).first()


def get_customer_wallet(user) -> Wallet | None:
    return Wallet.objects.filter(user=user).first()


def ledger_for_wallet(wallet):
    return LedgerEntry.objects.filter(wallet=wallet)


def customer_statement(user, *, ledger_cap: int = 500) -> list[dict]:
    """Merged, newest-first statement: posted ledger entries (completed) +
    open withdrawal holds (pending/approved/processing/flagged).

    The ledger is the bulk and is capped to its most recent ``ledger_cap``
    entries; open withdrawals are few. For the full ledger use
    ``/wallet/transactions/``.
    """
    # Local import avoids a wallets<->payouts import cycle.
    from Apps.payouts.models import WithdrawalRequest

    wallet = Wallet.objects.filter(user=user).first()
    items: list[dict] = []

    if wallet is not None:
        for e in ledger_for_wallet(wallet).order_by("-created_at")[:ledger_cap]:
            items.append(
                {
                    "id": str(e.id),
                    "kind": "ledger",
                    "description": e.description or e.get_category_display(),
                    "amount": e.signed_amount,
                    "status": "completed",
                    "created_at": e.created_at,
                }
            )

    open_statuses = (
        WithdrawalRequest.Status.PENDING,
        WithdrawalRequest.Status.APPROVED,
        WithdrawalRequest.Status.PROCESSING,
        WithdrawalRequest.Status.FLAGGED,
    )
    for w in WithdrawalRequest.objects.filter(
        user=user, status__in=open_statuses
    ).order_by("-created_at"):
        items.append(
            {
                "id": str(w.id),
                "kind": "withdrawal",
                "description": f"Withdrawal to {w.provider}",
                "amount": -w.amount,
                "status": w.status,
                "created_at": w.created_at,
            }
        )

    items.sort(key=lambda i: i["created_at"], reverse=True)
    return items
