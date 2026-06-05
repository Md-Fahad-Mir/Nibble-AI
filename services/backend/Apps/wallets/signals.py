"""Wallet-side signal receivers."""

from django.dispatch import receiver

from Apps.accounts.signals import email_verified


@receiver(email_verified)
def credit_referral_bonus_on_verification(sender, user, **kwargs):
    # Import here to avoid app-loading order issues.
    from Apps.wallets.services import maybe_credit_referral_bonus

    maybe_credit_referral_bonus(user)
