from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from Apps.accounts.models import User, VerificationCode
from Apps.wallets import services
from Apps.wallets.models import LedgerEntry


class ReferralBonusTests(APITestCase):
    def test_inviter_is_paid_once_when_referred_user_verifies_email(self):
        inviter = User.objects.create_user(
            email="inviter@example.com", password="x", full_name="Inviter"
        )
        # Register a referred user via the API so a verification code is issued.
        self.client.post(
            reverse("v1:accounts:auth:register"),
            {
                "full_name": "Invitee",
                "email": "invitee@example.com",
                "password": "Sup3rSecret!",
                "accept_terms": True,
                "referral_code": inviter.referral_code,
            },
            format="json",
        )
        from Apps.accounts.models import PendingUser
        pending = PendingUser.objects.get(email="invitee@example.com")
        code = pending.verification_code

        # First verification pays the inviter.
        self.client.post(
            reverse("v1:accounts:auth:verify-email"),
            {"email": "invitee@example.com", "code": code},
            format="json",
        )

        inviter_wallet = services.get_or_create_customer_wallet(inviter)
        self.assertEqual(inviter_wallet.balance, Decimal("5.00"))
        self.assertEqual(
            LedgerEntry.objects.filter(
                wallet=inviter_wallet,
                category=LedgerEntry.Category.REFERRAL_BONUS,
            ).count(),
            1,
        )

    def test_no_bonus_without_referrer(self):
        user = User.objects.create_user(
            email="solo@example.com", password="x", full_name="Solo"
        )
        result = services.maybe_credit_referral_bonus(user)
        self.assertIsNone(result)
