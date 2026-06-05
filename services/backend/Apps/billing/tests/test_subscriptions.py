from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from Apps.billing import services
from Apps.billing.models import Plan, Subscription
from Apps.brands.models import Brand
from Apps.wallets import services as wallet_services
from Apps.wallets.models import LedgerEntry


class FeeComputationTests(TestCase):
    def test_rebate_processing_fee(self):
        pro = Plan.objects.get(slug="pro")  # 15%
        self.assertEqual(
            services.rebate_processing_fee(pro, Decimal("10.00")), Decimal("1.50")
        )


class SubscriptionChargeTests(TestCase):
    def setUp(self):
        self.pro = Plan.objects.get(slug="pro")  # $99.00/mo
        self.brand = Brand.objects.create(name="Acme", slug="acme", plan=self.pro)
        self.wallet = wallet_services.get_or_create_brand_wallet(self.brand)

    def test_charge_debits_funded_wallet_and_advances_period(self):
        wallet_services.credit(
            wallet=self.wallet, amount=Decimal("200.00"),
            category=LedgerEntry.Category.FUNDING,
        )
        summary = services.charge_due_subscriptions()
        self.assertEqual(summary["charged"], 1)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("101.00"))  # 200 - 99

        sub = Subscription.objects.get(brand=self.brand)
        self.assertEqual(sub.status, Subscription.Status.ACTIVE)
        self.assertEqual(sub.total_charged, Decimal("99.00"))
        self.assertGreater(sub.next_charge_at, timezone.now())

    def test_underfunded_wallet_marks_past_due(self):
        # No funding -> cannot cover $99.
        summary = services.charge_due_subscriptions()
        self.assertEqual(summary["past_due"], 1)
        sub = Subscription.objects.get(brand=self.brand)
        self.assertEqual(sub.status, Subscription.Status.PAST_DUE)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("0.00"))

    def test_running_twice_does_not_double_charge_same_period(self):
        wallet_services.credit(
            wallet=self.wallet, amount=Decimal("500.00"),
            category=LedgerEntry.Category.FUNDING,
        )
        services.charge_due_subscriptions()
        # Immediately running again: next_charge_at is in the future, so no charge.
        services.charge_due_subscriptions()
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("401.00"))  # charged once
        self.assertEqual(
            LedgerEntry.objects.filter(
                category=LedgerEntry.Category.SUBSCRIPTION
            ).count(),
            1,
        )

    def test_free_plan_advances_without_charge(self):
        starter = Plan.objects.get(slug="starter")  # $0.00
        brand = Brand.objects.create(name="Free", slug="free", plan=starter)
        summary = services.charge_due_subscriptions()
        self.assertEqual(summary["free"], 1)
        sub = Subscription.objects.get(brand=brand)
        self.assertEqual(sub.status, Subscription.Status.ACTIVE)
