"""Date-range resolution shared by report scripts.

Defaults are always computed from the real clock here, in code -- never left
for a skill/LLM to infer "today" or "the start of the year" on its own.
"""

import re
from datetime import date, datetime
from typing import Optional, Tuple

_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def default_date_range(today: Optional[date] = None) -> Tuple[date, date]:
    """(January 1st of today's year, today).

    `today` exists only so callers can pass a fixed date for testing;
    production callers should omit it and let it resolve from datetime.now().
    """
    if today is None:
        today = datetime.now().date()
    return date(today.year, 1, 1), today


def _parse_date(value: str, label: str) -> date:
    if not _DATE_RE.match(value):
        raise ValueError(f"{label} must be in YYYY-MM-DD format, got: {value!r}")
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as e:
        raise ValueError(f"{label} is not a valid calendar date: {value!r} ({e})")


def resolve_date_range(
    start_str: Optional[str],
    end_str: Optional[str],
    today: Optional[date] = None,
) -> Tuple[date, date]:
    """Parse YYYY-MM-DD strings where given; default_date_range() fills in
    whichever side is missing. Raises ValueError if the range is invalid."""
    default_start, default_end = default_date_range(today)
    start = _parse_date(start_str, "--start-date") if start_str else default_start
    end = _parse_date(end_str, "--end-date") if end_str else default_end
    if start > end:
        raise ValueError(
            f"start date {start.isoformat()} is after end date {end.isoformat()}"
        )
    return start, end
