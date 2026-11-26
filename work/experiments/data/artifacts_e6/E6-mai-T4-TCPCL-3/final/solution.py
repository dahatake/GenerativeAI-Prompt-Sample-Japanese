import csv
import re


_TIME_RE = re.compile(r"^(\d{2}):(\d{2})$")
_REQUIRED_COLUMNS = {"employee", "date", "type", "start", "end"}


def _parse_time(value):
    if value is None:
        return None
    value = value.strip()
    match = _TIME_RE.fullmatch(value)
    if not match:
        return None
    hour, minute = map(int, match.groups())
    if hour > 23 or minute > 59:
        return None
    return hour * 60 + minute


def monthly_work_hours(path):
    """従業員ごとの月間労働時間を時間単位のfloatで集計する。"""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("CSV header is missing")

        fieldnames = {name.strip() for name in reader.fieldnames if name is not None}
        missing = _REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError("Missing required CSV columns: " + ", ".join(sorted(missing)))

        for row in reader:
            employee = (row.get("employee") or "").strip()
            shift_type = (row.get("type") or "").strip()

            if not employee:
                continue

            if shift_type == "paid_leave":
                totals[employee] = totals.get(employee, 0.0) + 7.5
                continue

            if shift_type != "work":
                continue

            start = _parse_time(row.get("start"))
            end = _parse_time(row.get("end"))
            if start is None or end is None:
                continue

            duration = end - start
            if duration < 0:
                duration += 24 * 60

            rounded_duration = (duration // 15) * 15
            totals[employee] = totals.get(employee, 0.0) + rounded_duration / 60.0

    return totals
