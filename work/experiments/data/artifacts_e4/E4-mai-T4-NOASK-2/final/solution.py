import csv


def _minutes(time_text):
    if not isinstance(time_text, str):
        return None
    parts = time_text.strip().split(":")
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return hour * 60 + minute


def monthly_work_hours(path):
    """Return total work hours for each employee in a CSV file."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                shift_type = (row.get("type") or "").strip().lower()
                employee = (row.get("employee") or "").strip()
            except AttributeError:
                continue

            if shift_type != "work" or not employee:
                continue

            start = _minutes(row.get("start"))
            end = _minutes(row.get("end"))
            if start is None or end is None:
                continue

            elapsed = end - start
            if elapsed <= 0:
                elapsed += 24 * 60

            totals[employee] = totals.get(employee, 0.0) + elapsed / 60.0

    return totals
