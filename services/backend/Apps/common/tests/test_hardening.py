"""Hardening guarantees: idempotency on money-in, plan-based data access,
and auth throttling."""

from decimal import Decimal

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.throttling import SimpleRateThrottle

from Apps.accounts.models import User
from Apps.billing.models import Plan
from Apps.brands.models import Brand, BrandMembership
from Apps.wallets import services as wallet_services
from Apps.wallets.models import LedgerEntry


def _brand(plan="starter"):
    owner = User.objects.create_user(email="owner@example.com", password="x", full_name="O")
    brand = Brand.objects.create(name="Acme", slug="acme", plan=Plan.objects.get(slug=plan))
    BrandMembership.objects.create(brand=brand, user=owner, role=BrandMembership.Role.OWNER)
    return owner, brand


class FundingIdempotencyTests(APITestCase):
    def test_same_idempotency_key_funds_once(self):
        owner, brand = _brand()
        self.client.force_authenticate(owner)
        url = reverse("v1:wallets:brand-wallet-fund", args=[brand.id])
        payload = {"amount": "100.00", "idempotency_key": "fund-abc"}

        first = self.client.post(url, payload, format="json")
        second = self.client.post(url, payload, format="json")  # retry

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        wallet = wallet_services.get_or_create_brand_wallet(brand)
        # Credited only once despite two identical requests.
        self.assertEqual(wallet.balance, Decimal("100.00"))
        self.assertEqual(
            LedgerEntry.objects.filter(
                wallet=wallet, category=LedgerEntry.Category.FUNDING
            ).count(),
            1,
        )

    def test_no_key_allows_repeated_funding(self):
        owner, brand = _brand()
        self.client.force_authenticate(owner)
        url = reverse("v1:wallets:brand-wallet-fund", args=[brand.id])
        self.client.post(url, {"amount": "10.00"}, format="json")
        self.client.post(url, {"amount": "10.00"}, format="json")
        wallet = wallet_services.get_or_create_brand_wallet(brand)
        self.assertEqual(wallet.balance, Decimal("20.00"))


class PlanDataAccessSweepTests(APITestCase):
    """Starter → anonymized customer data; Pro/Scale → full."""

    def test_data_access_level_by_plan(self):
        from Apps.brands.customers import brand_customers

        for plan_slug, expected in [("starter", "anonymized"), ("pro", "full"), ("scale", "full")]:
            owner = User.objects.create_user(
                email=f"o-{plan_slug}@example.com", password="x", full_name="O"
            )
            brand = Brand.objects.create(
                name="B", slug=f"b-{plan_slug}", plan=Plan.objects.get(slug=plan_slug)
            )
            BrandMembership.objects.create(
                brand=brand, user=owner, role=BrandMembership.Role.OWNER
            )
            self.assertEqual(brand_customers(brand)["data_access_level"], expected)


class AuthThrottleTests(APITestCase):
    """DRF binds THROTTLE_RATES as a class attribute at import, so override_settings
    won't change it — patch the class attribute directly."""

    def setUp(self):
        cache.clear()
        self._orig_rates = SimpleRateThrottle.THROTTLE_RATES
        SimpleRateThrottle.THROTTLE_RATES = {**self._orig_rates, "auth": "3/min"}

    def tearDown(self):
        SimpleRateThrottle.THROTTLE_RATES = self._orig_rates
        cache.clear()

    def test_login_endpoint_is_rate_limited(self):
        User.objects.create_user(email="c@example.com", password="Sup3rSecret!", full_name="C")
        url = reverse("v1:accounts:auth:login")
        body = {"email": "c@example.com", "password": "wrong"}

        statuses = [self.client.post(url, body, format="json").status_code for _ in range(5)]
        # The 4th+ request within the window is throttled (429).
        self.assertIn(status.HTTP_429_TOO_MANY_REQUESTS, statuses)
