"""Money helpers. All monetary values are Decimal, quantized to cents."""

from decimal import ROUND_HALF_UP, Decimal

CENTS = Decimal("0.01")
ZERO = Decimal("0.00")

# Standard column kwargs for monetary DecimalFields.
MONEY_FIELD = {"max_digits": 14, "decimal_places": 2}


def to_money(value) -> Decimal:
    """Coerce a value to a 2dp Decimal (banker-safe, ROUND_HALF_UP)."""
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)
