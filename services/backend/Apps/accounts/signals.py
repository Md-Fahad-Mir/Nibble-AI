"""Domain signals emitted by the accounts app.

Decoupling via signals keeps `accounts` (a low-level app) from importing
higher-level apps like `wallets`; receivers live in the consuming app.
"""

import django.dispatch

# Sent the first time a user's email becomes verified. kwargs: user
email_verified = django.dispatch.Signal()
