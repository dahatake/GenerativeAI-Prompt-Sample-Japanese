import csv
from datetime import datetime, timedelta, timezone

# JST has no DST, so a fixed offset avoids depending on tzdata being installed.
JST = timezone(timedelta(hours=9), "JST")


def _parse_timestamp(value):
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"timestamp without timezone: {value!r}")
    return dt


def monthly_sales(path):
    """Return net completed sales (tax-included) per JST month as {"YYYY-MM": int}."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            try:
                if row["status"].strip() != "completed":
                    continue
                month = _parse_timestamp(row["ordered_at"]).astimezone(JST).strftime("%Y-%m")
                amount = int(row["amount_incl_tax"].strip())
            except (KeyError, AttributeError, ValueError) as e:
                raise ValueError(f"{path}: invalid row at line {line_no}: {row!r}") from e
            totals[month] = totals.get(month, 0) + amount
    return {k: totals[k] for k in sorted(totals)}
