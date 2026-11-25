import csv


def _minutes(value):
    hour_text, minute_text = value.strip().split(':', 1)
    hour = int(hour_text)
    minute = int(minute_text)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("invalid time")
    return hour * 60 + minute


def monthly_work_hours(path):
    """Return total work hours per employee for all rows in a shift CSV."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            employee = (row.get("employee") or "").strip()
            if not employee:
                continue

            shift_type = (row.get("type") or "").strip().lower()
            if shift_type == "paid_leave":
                totals.setdefault(employee, 0.0)
                totals[employee] += 7.5
                continue
            if shift_type != "work":
                continue

            start_text = (row.get("start") or "").strip()
            end_text = (row.get("end") or "").strip()
            if not start_text or not end_text:
                continue

            try:
                start = _minutes(start_text)
                end = _minutes(end_text)
            except (AttributeError, TypeError, ValueError):
                continue

            duration = end - start
            if duration < 0:
                duration += 24 * 60

            duration = (duration // 15) * 15
            if duration:
                totals.setdefault(employee, 0.0)
                totals[employee] += duration / 60.0

    return totals
