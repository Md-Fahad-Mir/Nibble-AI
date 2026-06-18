"""Notification delivery for verification codes.

In dev, EMAIL_BACKEND is the console backend, so emails print to the runserver
output. SMS has no provider yet (no Celery/Twilio per the M0 decision); phone
codes are logged so they can be read during local development. Both functions
are the seam where real email/SMS providers get plugged in later.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_email_code(*, to_email: str, code: str, purpose_label: str) -> None:
    subject = f"NibblAI: your {purpose_label} code"
    body = (
        f"Your {purpose_label} code is: {code}\n\n"
        "It expires shortly. If you didn't request this, you can ignore it."
    )
    send_mail(
        subject,
        body,
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@nibblai.app"),
        [to_email],
        fail_silently=False,
    )


def send_sms_code(*, to_phone: str, code: str, purpose_label: str) -> None:
    # TODO(integration): replace with Twilio Verify when SMS is wired up.
    logger.info("SMS %s code for %s: %s", purpose_label, to_phone, code)


def send_referral_invite(
    *, to_email: str, friend_name: str, inviter_name: str, referral_code: str
) -> None:
    """Email a friend an invite carrying the inviter's referral code."""
    base_url = getattr(settings, "PUBLIC_BASE_URL", "http://localhost:8000")
    signup_url = f"{base_url}/signup?ref={referral_code}"
    greeting = f"Hi {friend_name}," if friend_name else "Hi,"
    subject = f"{inviter_name} invited you to NibblAI"
    body = (
        f"{greeting}\n\n"
        f"{inviter_name} thinks you'll love NibblAI — upload receipts, earn cash.\n\n"
        f"Sign up with their referral code {referral_code}:\n{signup_url}\n"
    )
    send_mail(
        subject,
        body,
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@nibblai.app"),
        [to_email],
        fail_silently=False,
    )
