"""Small date utilities (kept dependency-free)."""

import calendar
import datetime as dt


def add_months(value: dt.datetime, months: int) -> dt.datetime:
    """Add calendar months to a datetime, clamping the day and keeping tzinfo."""
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)
