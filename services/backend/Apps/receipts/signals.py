"""Receipt lifecycle signals.

Emitted when a receipt reaches a terminal state. The rebates app listens and
issues (or voids) the reward, keeping receipts decoupled from rebates.
"""

import django.dispatch

# kwargs: receipt
receipt_verified = django.dispatch.Signal()
receipt_rejected = django.dispatch.Signal()
