import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9), "JST")

REQUIRED_COLUMNS = ("ordered_at", "amount_incl_tax", "status")
INCLUDED_STATUS = "completed"
KNOWN_STATUSES = {"completed", "cancelled"}


def _parse_ordered_at(value: str, line_no: int) -> datetime:
    try:
        dt = datetime.fromisoformat(value.strip())
    except ValueError as e:
        raise ValueError(f"line {line_no}: invalid ordered_at {value!r}") from e
    if dt.tzinfo is None:
        # A naive timestamp would make the month boundary ambiguous.
        raise ValueError(f"line {line_no}: ordered_at has no timezone {value!r}")
    return dt


def _parse_amount(value: str, line_no: int) -> int:
    try:
        return int(value.strip())
    except ValueError as e:
        raise ValueError(f"line {line_no}: invalid amount_incl_tax {value!r}") from e


def monthly_sales(path: str | os.PathLike) -> dict[str, int]:
    """Sum tax-included sales of completed orders per JST calendar month.

    Returns {"YYYY-MM": amount}; months without any completed order are omitted.
    Negative amounts (refunds) are netted. Malformed rows raise ValueError.
    """
    totals: dict[str, int] = defaultdict(int)
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        for row in reader:
            line_no = reader.line_num
            status = (row["status"] or "").strip()
            if status not in KNOWN_STATUSES:
                raise ValueError(f"line {line_no}: unknown status {status!r}")
            ordered_at = _parse_ordered_at(row["ordered_at"] or "", line_no)
            amount = _parse_amount(row["amount_incl_tax"] or "", line_no)
            if status != INCLUDED_STATUS:
                continue
            month = ordered_at.astimezone(JST).strftime("%Y-%m")
            totals[month] += amount
    return dict(sorted(totals.items()))
