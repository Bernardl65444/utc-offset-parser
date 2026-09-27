# UTC Offset Parser

Parses human-written UTC offset strings like `GMT-5`, `+0530`, and `UTC+02:00` into Python `datetime.timezone` objects. Standard library only.

```python
from utc_offset_parser import parse_utc_offset, ParseError

try:
    tz = parse_utc_offset("GMT-05:30")
except ParseError:
    # handle bad input
    raise

# tz is a datetime.timezone
offset = tz.utcoffset(None)  # datetime.timedelta(-1 day, 18:30:00)
```

## Why

Configuration files and logs are full of offsets written by humans in inconsistent shapes: `UTC+02:00`, `GMT-5`, `+0530`. `datetime.strptime` with `%z` handles some of these but not the `UTC`/`GMT` prefixes, and its error messages are opaque. This library exists to accept that narrow family of strings and return a real `timezone` object, with a single `ParseError` for anything it does not recognise.

## Decisions and edges

- The sign is **mandatory**. `02:00` is rejected; use `+02:00`.
- Hours must be two digits. `+2:00` is rejected; use `+02:00`.
- `+24:00` is rejected even though ISO 8601 permits it. Python's `timedelta` would silently normalise it to the next day, which is almost never what the caller means.
- Bare `Z` and bare `UTC` (no offset) are **rejected**. The function is called `parse_utc_offset`; if you want UTC, pass `timezone.utc` directly. Silently returning UTC for missing input hides bugs.
- The returned `timezone` carries the original input string as its `tzname`, so it round-trips in logs.
