import csv
from datetime import date
import re


def _clock_minutes(text):
    if not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", text):
        raise ValueError(f"Invalid time: {text!r} (expected HH:MM)")
    hours, minutes = map(int, text.split(":"))
    return hours * 60 + minutes


def monthly_work_hours(path):
    """Sum work and paid leave hours by employee for one month."""
    totals = {}
    month = None
    required = {"employee", "date", "type", "start", "end"}
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source, strict=True)
        fields = rows.fieldnames
        if fields is None:
            return {}
        if not required.issubset(fields) or len(fields) != len(set(fields)):
            raise ValueError("CSV must have unique headers including employee, date, type, start, end")
        for row in rows:
            try:
                if None in row or any(row[field] is None for field in required):
                    raise ValueError("Inconsistent CSV columns")
                employee = row["employee"].strip()
                kind = row["type"].strip()
                if not employee or not kind:
                    raise ValueError("Employee and type are required")
                day_text = row["date"].strip()
                day = date.fromisoformat(day_text)
                if day.isoformat() != day_text:
                    raise ValueError("Expected date in YYYY-MM-DD format")
                row_month = (day.year, day.month)
                if month is not None and row_month != month:
                    raise ValueError("CSV contains more than one month")
                month = row_month
                totals.setdefault(employee, 0)
                if kind == "work":
                    start = _clock_minutes(row["start"].strip())
                    end = _clock_minutes(row["end"].strip())
                    minutes = (end - start) % (24 * 60)
                    if minutes > 6 * 60:
                        minutes -= 60
                    totals[employee] += (minutes // 15) * 15
                elif kind == "paid_leave":
                    totals[employee] += 450
            except ValueError as exc:
                raise ValueError(f"CSV line {rows.line_num}: {exc}") from exc
    return {employee: minutes / 60 for employee, minutes in totals.items()}
