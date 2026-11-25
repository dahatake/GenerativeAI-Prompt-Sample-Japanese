import csv
from datetime import date, datetime


def _minutes(value: str) -> int:
    clock = datetime.strptime(value, "%H:%M")
    return clock.hour * 60 + clock.minute


def monthly_work_hours(path) -> dict[str, float]:
    """Return the hours worked by each employee in a single-month shift CSV."""
    totals = {}
    month = None
    required = {"employee", "date", "type", "start", "end"}
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source, strict=True)
        if rows.fieldnames is None:
            return {}
        if not required.issubset(rows.fieldnames):
            raise ValueError(f"Missing CSV columns: {', '.join(sorted(required - set(rows.fieldnames)))}")

        for row in rows:
            try:
                if None in row or any(row[column] is None for column in required):
                    raise ValueError("Wrong number of CSV fields")
                employee = row["employee"].strip()
                kind = row["type"].strip()
                if not employee or not kind:
                    raise ValueError("Employee and shift type must not be blank")
                shift_date = date.fromisoformat(row["date"].strip())
                shift_month = (shift_date.year, shift_date.month)
                if month is not None and shift_month != month:
                    raise ValueError("Expected shifts from a single calendar month")
                month = shift_month

                totals.setdefault(employee, 0)
                if kind == "work":
                    start = _minutes(row["start"].strip())
                    end = _minutes(row["end"].strip())
                    duration = end - start
                    totals[employee] += duration if duration >= 0 else duration + 24 * 60
            except ValueError as error:
                raise ValueError(f"CSV line {rows.line_num}: {error}") from error

    return {employee: minutes / 60 for employee, minutes in totals.items()}
