"""Shared domain exception base.

Errors that subclass DomainError are expected, user-facing conditions that
API views translate into HTTP 400 responses. Using a common base lets an error
raised deep in a cross-app flow (e.g. redemption triggered by receipt
verification) surface cleanly regardless of which app raised it.
"""


class DomainError(Exception):
    """Expected, user-facing domain error (mapped to HTTP 400)."""
