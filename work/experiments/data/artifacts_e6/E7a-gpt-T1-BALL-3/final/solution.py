import csv
import re
from datetime import datetime, timedelta, timezone


_JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Return consecutive JST months of completed sales, excluding tax."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source, strict=True)
        fields = rows.fieldnames
        if fields is None:
            return {}
        required = {"ordered_at", "amount_incl_tax", "status"}
        if not required.issubset(fields):
            raise ValueError("CSV requires ordered_at, amount_incl_tax, and status columns")
        for row in rows:
            if row["status"] != "completed":
                continue
            timestamp = row["ordered_at"] or ""
            if timestamp.endswith("Z"):
                timestamp = timestamp[:-1] + "+00:00"
            try:
                ordered_at = datetime.fromisoformat(timestamp)
                if ordered_at.utcoffset() is None:
                    raise ValueError("missing UTC offset")
                local_date = ordered_at.astimezone(_JST)
            except (ValueError, OverflowError) as error:
                raise ValueError(f"line {rows.line_num}: invalid ordered_at") from error

            amount = (row["amount_incl_tax"] or "").strip()
            if re.fullmatch(r"[+-]?[0-9]+", amount) is None:
                raise ValueError(f"line {rows.line_num}: invalid amount_incl_tax")
            month_index = local_date.year * 12 + local_date.month - 1
            totals[month_index] = totals.get(month_index, 0) + int(amount)

    if not totals:
        return {}

    result = {}
    for month_index in range(min(totals), max(totals) + 1):
        year, month = divmod(month_index, 12)
        gross = totals.get(month_index, 0)
        # Divide by 1.1 exactly, truncating toward zero.
        net = abs(gross) * 10 // 11
        result[f"{year:04d}-{month + 1:02d}"] = net if gross >= 0 else -net
    return result
