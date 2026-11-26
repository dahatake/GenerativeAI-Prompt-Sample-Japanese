import csv
import re
from datetime import datetime, timedelta, timezone


_JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Sum completed, tax-inclusive sales by calendar month in Japan time."""
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
            month = f"{local_date.year:04d}-{local_date.month:02d}"
            totals[month] = totals.get(month, 0) + int(amount)
    return dict(sorted(totals.items()))
