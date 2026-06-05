from decimal import Decimal

from django.test import TestCase

from Apps.accounts.models import User
from Apps.wallets import services
from Apps.wallets.models import Hold, LedgerEntry, Wallet


class WalletServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="c@example.com", password="x", full_name="C"
        )
        self.wallet = services.get_or_create_customer_wallet(self.user)

    def _balance(self):
        self.wallet.refresh_from_db()
        return self.wallet.balance

    def test_credit_increases_balance_and_appends_ledger(self):
        services.credit(
            wallet=self.wallet, amount=Decimal("10.00"),
            category=LedgerEntry.Category.ADJUSTMENT,
        )
        self.assertEqual(self._balance(), Decimal("10.00"))
        entry = LedgerEntry.objects.get()
        self.assertEqual(entry.entry_type, LedgerEntry.EntryType.CREDIT)
        self.assertEqual(entry.balance_after, Decimal("10.00"))

    def test_balance_equals_sum_of_ledger(self):
        services.credit(wallet=self.wallet, amount=Decimal("25.00"),
                        category=LedgerEntry.Category.FUNDING)
        services.debit(wallet=self.wallet, amount=Decimal("7.50"),
                       category=LedgerEntry.Category.PAYOUT)
        services.credit(wallet=self.wallet, amount=Decimal("2.25"),
                        category=LedgerEntry.Category.ADJUSTMENT)
        ledger_sum = sum(
            (e.signed_amount for e in self.wallet.ledger_entries.all()),
            Decimal("0.00"),
        )
        self.assertEqual(self._balance(), ledger_sum)
        self.assertEqual(self._balance(), Decimal("19.75"))

    def test_debit_rejects_overdraw(self):
        services.credit(wallet=self.wallet, amount=Decimal("5.00"),
                        category=LedgerEntry.Category.FUNDING)
        with self.assertRaises(services.InsufficientFunds):
            services.debit(wallet=self.wallet, amount=Decimal("5.01"),
                           category=LedgerEntry.Category.PAYOUT)
        self.assertEqual(self._balance(), Decimal("5.00"))

    def test_positive_amount_enforced(self):
        with self.assertRaises(services.WalletError):
            services.credit(wallet=self.wallet, amount=Decimal("0.00"),
                            category=LedgerEntry.Category.FUNDING)

    def test_hold_reserves_available_without_changing_balance(self):
        services.credit(wallet=self.wallet, amount=Decimal("100.00"),
                        category=LedgerEntry.Category.FUNDING)
        services.place_hold(wallet=self.wallet, amount=Decimal("30.00"))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("100.00"))
        self.assertEqual(self.wallet.held_amount(), Decimal("30.00"))
        self.assertEqual(self.wallet.available(), Decimal("70.00"))

    def test_hold_cannot_exceed_available(self):
        services.credit(wallet=self.wallet, amount=Decimal("50.00"),
                        category=LedgerEntry.Category.FUNDING)
        services.place_hold(wallet=self.wallet, amount=Decimal("40.00"))
        with self.assertRaises(services.InsufficientFunds):
            services.place_hold(wallet=self.wallet, amount=Decimal("11.00"))

    def test_capture_hold_debits_and_marks_captured(self):
        services.credit(wallet=self.wallet, amount=Decimal("100.00"),
                        category=LedgerEntry.Category.FUNDING)
        hold = services.place_hold(wallet=self.wallet, amount=Decimal("40.00"))
        services.capture_hold(hold=hold, category=LedgerEntry.Category.REBATE_REWARD)
        hold.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(hold.status, Hold.Status.CAPTURED)
        self.assertEqual(self.wallet.balance, Decimal("60.00"))
        self.assertEqual(self.wallet.held_amount(), Decimal("0.00"))

    def test_release_hold_frees_available_and_keeps_balance(self):
        services.credit(wallet=self.wallet, amount=Decimal("100.00"),
                        category=LedgerEntry.Category.FUNDING)
        hold = services.place_hold(wallet=self.wallet, amount=Decimal("40.00"))
        services.release_hold(hold=hold)
        hold.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(hold.status, Hold.Status.RELEASED)
        self.assertEqual(self.wallet.balance, Decimal("100.00"))
        self.assertEqual(self.wallet.available(), Decimal("100.00"))

    def test_idempotent_credit_does_not_double_post(self):
        for _ in range(2):
            services.credit(
                wallet=self.wallet, amount=Decimal("15.00"),
                category=LedgerEntry.Category.FUNDING,
                idempotency_key="fund-abc",
            )
        self.assertEqual(LedgerEntry.objects.count(), 1)
        self.assertEqual(self._balance(), Decimal("15.00"))

    def test_ledger_entries_are_immutable(self):
        services.credit(wallet=self.wallet, amount=Decimal("1.00"),
                        category=LedgerEntry.Category.FUNDING)
        entry = LedgerEntry.objects.get()
        entry.amount = Decimal("999.00")
        with self.assertRaises(ValueError):
            entry.save()
        with self.assertRaises(ValueError):
            entry.delete()

    def test_wallet_requires_exactly_one_owner(self):
        # Sanity: customer wallet has a user and no brand.
        self.assertIsNotNone(self.wallet.user_id)
        self.assertIsNone(self.wallet.brand_id)
        self.assertEqual(self.wallet.kind, Wallet.Kind.CUSTOMER)
