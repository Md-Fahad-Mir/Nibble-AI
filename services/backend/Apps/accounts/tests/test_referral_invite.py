"""Contract tests for the referral-invite endpoint (Phase-1 batch 2)."""

from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Apps.accounts.models import User


class ReferralInviteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="me@example.com", password="x", full_name="Me", is_email_verified=True
        )
        self.client.force_authenticate(self.user)
        self.url = reverse("v1:accounts:users:referral-invite")

    def test_email_invite_sends_mail(self):
        resp = self.client.post(
            self.url, {"full_name": "Jane Doe", "contact": "jane@example.com"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(resp.data["channel"], "email")
        self.assertEqual(len(mail.outbox), 1)
        # The invite carries the inviter's referral code.
        self.assertIn(self.user.referral_code, mail.outbox[0].body)

    def test_phone_invite_is_gated(self):
        resp = self.client.post(
            self.url, {"full_name": "Jane Doe", "contact": "+15551234567"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_cannot_invite_self(self):
        resp = self.client.post(
            self.url, {"full_name": "Me", "contact": "me@example.com"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_user_is_not_revealed_but_returns_202(self):
        User.objects.create_user(
            email="friend@example.com", password="x", full_name="Friend"
        )
        resp = self.client.post(
            self.url, {"full_name": "Friend", "contact": "friend@example.com"},
            format="json",
        )
        # Uniform success (no enumeration); no email sent to an existing user.
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(len(mail.outbox), 0)

    def test_requires_auth(self):
        self.client.force_authenticate(None)
        resp = self.client.post(
            self.url, {"full_name": "Jane", "contact": "jane@example.com"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
