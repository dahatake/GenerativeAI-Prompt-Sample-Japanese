import csv
from collections import defaultdict
from datetime import date, datetime, timedelta

REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")


def _parse_time(value, line_no, field):
    try:
        return datetime.strptime(value.strip(), "%H:%M")
    except (AttributeError, ValueError):
        raise ValueError(f"line {line_no}: invalid {field} time: {value!r}") from None


def monthly_work_hours(path):
    """Return {employee_id: worked hours (float)} for a single-month shift CSV.

    Only rows with type == "work" count (end - start, no break deduction).
    A shift whose end is earlier than its start ends on the next day and is
    attributed to its start date. Employees with only non-work rows map to 0.0.
    Raises ValueError for missing columns, multiple months, or bad work rows.
    """
    totals = defaultdict(float)
    month = None

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise ValueError(f"missing columns: {missing}")
        reader.fieldnames = header

        for line_no, row in enumerate(reader, start=2):
            employee = (row.get("employee") or "").strip()
            if not employee:
                raise ValueError(f"line {line_no}: empty employee")
            try:
                day = date.fromisoformat((row.get("date") or "").strip())
            except ValueError:
                raise ValueError(f"line {line_no}: invalid date: {row.get('date')!r}") from None

            row_month = (day.year, day.month)
            if month is None:
                month = row_month
            elif row_month != month:
                raise ValueError(
                    f"line {line_no}: multiple months in file "
                    f"({month[0]:04d}-{month[1]:02d} and {day:%Y-%m})"
                )

            totals[employee] += 0.0
            if (row.get("type") or "").strip() != "work":
                continue

            start = _parse_time(row.get("start"), line_no, "start")
            end = _parse_time(row.get("end"), line_no, "end")
            if end == start:
                raise ValueError(f"line {line_no}: start equals end (ambiguous 0h/24h shift)")
            if end < start:
                end += timedelta(days=1)
            totals[employee] += (end - start).total_seconds() / 3600

    return dict(totals)
