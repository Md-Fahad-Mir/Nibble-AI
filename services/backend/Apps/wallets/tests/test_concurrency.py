"""Concurrency safety test for the ledger.

Real row-locking (SELECT ... FOR UPDATE) only exists on Postgres, so this test
is skipped on SQLite. It runs in CI / on the developer's Postgres.
"""

import threading
from decimal import Decimal
from unittest import skipUnless

from django.db import connection
from django.test import TransactionTestCase

from Apps.accounts.models import User
from Apps.wallets import services
from Apps.wallets.models import LedgerEntry


@skipUnless(
    connection.vendor == "postgresql",
    "Row-level locking requires PostgreSQL.",
)
class ConcurrentDebitTests(TransactionTestCase):
    def test_concurrent_debits_do_not_oversell(self):
        user = User.objects.create_user(
            email="race@example.com", password="x", full_name="Race"
        )
        wallet = services.get_or_create_customer_wallet(user)
        services.credit(
            wallet=wallet, amount=Decimal("100.00"),
            category=LedgerEntry.Category.FUNDING,
        )

        results = []

        def try_debit():
            try:
                services.debit(
                    wallet=wallet, amount=Decimal("80.00"),
                    category=LedgerEntry.Category.PAYOUT,
                )
                results.append("ok")
            except services.InsufficientFunds:
                results.append("rejected")
            finally:
                connection.close()

        threads = [threading.Thread(target=try_debit) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        wallet.refresh_from_db()
        # Exactly one debit of 80 should succeed; the other must be rejected.
        self.assertEqual(results.count("ok"), 1)
        self.assertEqual(results.count("rejected"), 1)
        self.assertEqual(wallet.balance, Decimal("20.00"))
