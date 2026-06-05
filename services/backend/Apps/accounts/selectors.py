"""Read-side queries for the accounts app."""

from Apps.accounts.models import User


def get_active_user_by_email(email: str) -> User | None:
    return User.objects.filter(
        email__iexact=email, is_active=True, is_deleted=False
    ).first()


def get_user_by_referral_code(code: str) -> User | None:
    return User.objects.filter(referral_code=code, is_deleted=False).first()
