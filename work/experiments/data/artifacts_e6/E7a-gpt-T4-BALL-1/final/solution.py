import csv
import re
from datetime import date


def _clock_minutes(value):
    if not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value):
        raise ValueError(f"Expected a time in HH:MM format, got {value!r}")
    hours, minutes = map(int, value.split(":"))
    return hours * 60 + minutes


def monthly_work_hours(path):
    """Return credited hours per employee for the single month in the CSV."""
    required_fields = {"employee", "date", "type", "start", "end"}
    month = None
    totals = {}

    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        try:
            fields = reader.fieldnames
            if fields is None:
                return {}
            if not required_fields.issubset(fields) or len(set(fields)) != len(fields):
                raise ValueError("Expected unique CSV headers including employee, date, type, start, end")

            for row in reader:
                if None in row or None in row.values():
                    raise ValueError("Row does not match the number of CSV headers")
                employee = row["employee"].strip()
                if not employee:
                    raise ValueError("Employee ID is empty")

                date_text = row["date"].strip()
                work_date = date.fromisoformat(date_text)
                if work_date.isoformat() != date_text:
                    raise ValueError("Expected a date in YYYY-MM-DD format")
                row_month = (work_date.year, work_date.month)
                if month is None:
                    month = row_month
                elif row_month != month:
                    raise ValueError("CSV contains rows from more than one calendar month")

                totals.setdefault(employee, 0)
                shift_type = row["type"].strip()
                if shift_type == "paid_leave":
                    totals[employee] += 450
                    continue
                if shift_type != "work":
                    raise ValueError(f"Unsupported shift type: {shift_type!r}")

                start = _clock_minutes(row["start"].strip())
                end = _clock_minutes(row["end"].strip())
                # A shift ending before it starts finishes on the next day.
                minutes = (end - start) % (24 * 60)
                if minutes > 6 * 60:
                    minutes -= 60
                totals[employee] += minutes - minutes % 15
        except (csv.Error, ValueError) as error:
            raise ValueError(f"CSV line {reader.line_num}: {error}") from error

    return {employee: minutes / 60 for employee, minutes in totals.items()}
