import csv
from datetime import datetime
from typing import Dict, Union


def _parse_clock(value: str) -> Union[int, None]:
    """Return minutes from midnight, or None for a missing/invalid clock value."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%H:%M")
    except ValueError:
        return None
    return parsed.hour * 60 + parsed.minute


def monthly_work_hours(path: str) -> Dict[str, float]:
    """Aggregate monthly shift hours by employee from a shift CSV."""
    minutes_by_employee: Dict[str, int] = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            employee = (row.get("employee") or "").strip()
            if not employee:
                continue

            shift_type = (row.get("type") or "").strip().lower()

            if shift_type == "paid_leave":
                minutes_by_employee.setdefault(employee, 0)
                minutes_by_employee[employee] += 450
                continue

            if shift_type != "work":
                continue

            start = _parse_clock(row.get("start"))
            end = _parse_clock(row.get("end"))
            if start is None or end is None:
                continue

            if end < start:
                duration = (24 * 60 - start) + end
            elif end > start:
                duration = end - start
            else:
                duration = 0

            if duration > 360:
                duration -= 60

            duration = (duration // 15) * 15
            minutes_by_employee.setdefault(employee, 0)
            minutes_by_employee[employee] += duration

    return {
        employee: minutes / 60.0
        for employee, minutes in minutes_by_employee.items()
    }
