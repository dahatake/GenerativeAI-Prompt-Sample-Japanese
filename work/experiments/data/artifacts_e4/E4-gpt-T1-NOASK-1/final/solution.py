import csv
import re
from datetime import datetime, timedelta, timezone


_REQUIRED_COLUMNS = {"ordered_at", "amount_incl_tax", "status"}
_UTC_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_INTEGER = re.compile(r"[+-]?[0-9]+")
_JST = timezone(timedelta(hours=9))


def monthly_sales(path) -> dict[str, int]:
    """Sum completed sales by JST calendar month, retaining signed amounts."""
    totals: dict[str, int] = {}
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source, strict=True)
        try:
            missing = _REQUIRED_COLUMNS.difference(rows.fieldnames or ())
            if missing:
                raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")

            for row in rows:
                line = rows.line_num
                timestamp = row["ordered_at"] or ""
                amount = row["amount_incl_tax"] or ""
                status = row["status"]
                if not _UTC_TIMESTAMP.fullmatch(timestamp):
                    raise ValueError(f"Line {line}: invalid ordered_at")
                try:
                    ordered_at = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                    local_date = ordered_at.replace(tzinfo=timezone.utc).astimezone(_JST)
                except (ValueError, OverflowError) as error:
                    raise ValueError(f"Line {line}: invalid ordered_at") from error
                if not _INTEGER.fullmatch(amount):
                    raise ValueError(f"Line {line}: invalid amount_incl_tax")
                value = int(amount)
                if status not in ("completed", "cancelled"):
                    raise ValueError(f"Line {line}: invalid status")
                if status == "completed":
                    month = f"{local_date.year:04d}-{local_date.month:02d}"
                    totals[month] = totals.get(month, 0) + value
        except csv.Error as error:
            raise ValueError(f"Line {rows.line_num}: invalid CSV") from error
    return totals
