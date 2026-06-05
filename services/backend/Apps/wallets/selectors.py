"""Read-side queries for wallets."""

from Apps.wallets.models import LedgerEntry, Wallet


def get_brand_wallet(brand) -> Wallet | None:
    return Wallet.objects.filter(brand=brand).first()


def get_customer_wallet(user) -> Wallet | None:
    return Wallet.objects.filter(user=user).first()


def ledger_for_wallet(wallet):
    return LedgerEntry.objects.filter(wallet=wallet)
