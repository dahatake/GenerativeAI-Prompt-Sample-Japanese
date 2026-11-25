import csv
import os
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
TAX_RATE_DIVISOR = Decimal("1.1")
EXCLUDED_STATUSES = {"cancelled"}
REQUIRED_COLUMNS = ("ordered_at", "amount_incl_tax", "status")


def _to_jst_month(ordered_at: str) -> tuple[int, int]:
    dt = datetime.fromisoformat(ordered_at.strip())
    if dt.tzinfo is None:
        raise ValueError(f"ordered_at has no timezone: {ordered_at!r}")
    local = dt.astimezone(JST)
    return local.year, local.month


def _excl_tax(amount_incl_tax: str) -> int:
    # Per-row conversion; ties round away from zero (ROUND_HALF_UP on Decimal).
    value = Decimal(int(amount_incl_tax.strip())) / TAX_RATE_DIVISOR
    return int(value.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _month_range(start: tuple[int, int], end: tuple[int, int]):
    year, month = start
    while (year, month) <= end:
        yield year, month
        month += 1
        if month > 12:
            year, month = year + 1, 1


def monthly_sales(path: str | os.PathLike) -> dict[str, int]:
    """Return tax-excluded sales per JST month as {"YYYY-MM": int}.

    Cancelled orders are excluded; months without sales between the first
    and last sales month are filled with 0.
    """
    totals: dict[tuple[int, int], int] = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if reader.fieldnames is not None and missing:
            raise ValueError(f"missing columns: {missing}")
        for line_no, row in enumerate(reader, start=2):
            try:
                if row["status"].strip().lower() in EXCLUDED_STATUSES:
                    continue
                key = _to_jst_month(row["ordered_at"])
                amount = _excl_tax(row["amount_incl_tax"])
            except (ValueError, AttributeError, ArithmeticError) as e:
                raise ValueError(f"invalid row at line {line_no}: {row}") from e
            totals[key] = totals.get(key, 0) + amount

    if not totals:
        return {}
    return {
        f"{y:04d}-{m:02d}": totals.get((y, m), 0)
        for y, m in _month_range(min(totals), max(totals))
    }
