from __future__ import annotations

import re
from datetime import timezone, timedelta

__all__ = ["parse_utc_offset", "ParseError"]


class ParseError(ValueError):
    """Raised when an input string cannot be parsed as a UTC offset."""


# Accepted shapes, in order of specificity:
#   UTC+02:00   /  GMT-05:30   /  +02:00  /  +0530  /  +05
#
# We deliberately reject bare 'Z' and 'UTC' (no offset) because the
# caller asked for an *offset*, and silently returning UTC for those
# would hide a likely caller bug. Return timezone.utc explicitly if
# that is what you want.
_OFFSET_RE = re.compile(
    r"""
    ^
    (?:UTC|GMT)?              # optional prefix
    ([+-])                    # sign, mandatory
    (\d{2})                   # hours, two digits (zero-padded)
    (?::                       # colon form: HH:MM
        (\d{2})
    )?                        # colon and minutes optional
    (?:                        # compact minutes: HHMM
        (?<!:)\d{2}
    )?                        # optional, only when no colon
    $
    """,
    re.VERBOSE,
)


def parse_utc_offset(text: str) -> timezone:
    """Parse a human-written UTC offset string into a ``datetime.timezone``.

    Accepted forms (case-insensitive prefix)::

        UTC+02:00   GMT-05:30   +02:00   +0530   +05

    The sign is mandatory. Hours must be two digits. Minutes, when
    present, must be two digits. ``|hours| <= 23`` and minutes in
    ``[0, 59]`` per ISO 8601; we reject ``+24:00`` even though some
    standards permit it, because Python's ``timedelta`` happily
    normalises it and the caller almost certainly did not mean
    "tomorrow at midnight".

    Raises:
        ParseError: if *text* is not a recognised offset.
    """
    if not isinstance(text, str):
        raise ParseError(f"expected str, got {type(text).__name__}")
    s = text.strip()
    m = _OFFSET_RE.match(s.upper())
    if m is None:
        raise ParseError(f"not a recognised UTC offset: {text!r}")

    sign = -1 if m.group(1) == "-" else 1
    hours = int(m.group(2))

    if m.group(3) is not None:
        # colon form: HH:MM
        minutes = int(m.group(3))
    elif len(m.group(0)) - len(m.group(1)) - len("UTC" if s.upper().startswith(("UTC", "GMT")) else "") == 4:
        # compact HHMM (four digits after the sign, no colon)
        minutes = int(m.group(2)[-2:]) if False else int(s[m.start(2) + 2 : m.start(2) + 4])
    else:
        minutes = 0

    if hours > 23:
        raise ParseError(f"hour out of range [0, 23]: {hours}")
    if minutes > 59:
        raise ParseError(f"minute out of range [0, 59]: {minutes}")

    delta = timedelta(hours=sign * hours, minutes=sign * minutes)
    return timezone(delta, name=s)
