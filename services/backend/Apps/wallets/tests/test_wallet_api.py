from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Apps.accounts.models import User
from Apps.billing.models import Plan
from Apps.brands.models import Brand, BrandMembership


class BrandWalletApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com", password="x", full_name="Owner"
        )
        self.outsider = User.objects.create_user(
            email="out@example.com", password="x", full_name="Out"
        )
        self.brand = Brand.objects.create(
            name="Acme", slug="acme", plan=Plan.objects.get(slug="starter")
        )
        BrandMembership.objects.create(
            brand=self.brand, user=self.owner, role=BrandMembership.Role.OWNER
        )

    def test_member_sees_zero_balance_wallet(self):
        self.client.force_authenticate(self.owner)
        resp = self.client.get(
            reverse("v1:wallets:brand-wallet", args=[self.brand.id])
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(resp.data["balance"]), Decimal("0.00"))
        self.assertEqual(resp.data["kind"], "brand")

    def test_non_member_blocked_from_wallet(self):
        self.client.force_authenticate(self.outsider)
        resp = self.client.get(
            reverse("v1:wallets:brand-wallet", args=[self.brand.id])
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_funding_increases_balance_and_records_transaction(self):
        self.client.force_authenticate(self.owner)
        resp = self.client.post(
            reverse("v1:wallets:brand-wallet-fund", args=[self.brand.id]),
            {"amount": "250.00"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(resp.data["balance"]), Decimal("250.00"))

        tx = self.client.get(
            reverse("v1:wallets:brand-wallet-transactions", args=[self.brand.id])
        )
        self.assertEqual(tx.data["count"], 1)
        self.assertEqual(tx.data["results"][0]["category"], "funding")


class CustomerWalletApiTests(APITestCase):
    def test_customer_wallet_is_created_on_first_access(self):
        user = User.objects.create_user(
            email="c@example.com", password="x", full_name="C"
        )
        self.client.force_authenticate(user)
        resp = self.client.get(reverse("v1:wallets:customer-wallet"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["kind"], "customer")
        self.assertEqual(Decimal(resp.data["balance"]), Decimal("0.00"))
