import csv
import re


_TIME_PATTERN = re.compile(r"^(\d{2}):(\d{2})$")


def _minutes(time_text):
    match = _TIME_PATTERN.fullmatch(time_text.strip())
    if not match:
        raise ValueError("Invalid time format; expected HH:MM")

    hours = int(match.group(1))
    minutes = int(match.group(2))
    if hours > 23 or minutes > 59:
        raise ValueError("Invalid time; expected HH:MM in 24-hour format")
    return hours * 60 + minutes


def monthly_work_hours(path):
    """Aggregate work hours per employee from a shifts CSV."""
    totals_minutes = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"employee", "type", "start", "end"}
        if reader.fieldnames is None:
            raise ValueError("CSV header is missing")

        missing = required.difference(reader.fieldnames)
        if missing:
            raise ValueError("Missing required CSV column(s): " + ", ".join(sorted(missing)))

        for row_number, row in enumerate(reader, start=2):
            shift_type = (row.get("type") or "").strip().lower()
            if shift_type != "work":
                continue

            employee = (row.get("employee") or "").strip()
            if not employee:
                raise ValueError("Missing employee at CSV row {}".format(row_number))

            start_text = row.get("start") or ""
            end_text = row.get("end") or ""
            if not start_text.strip() or not end_text.strip():
                raise ValueError("Missing start or end at CSV row {}".format(row_number))

            try:
                start = _minutes(start_text)
                end = _minutes(end_text)
            except ValueError as exc:
                raise ValueError("Invalid work shift at CSV row {}: {}".format(row_number, exc)) from exc

            elapsed = end - start
            if elapsed < 0:
                elapsed += 24 * 60

            totals_minutes[employee] = totals_minutes.get(employee, 0) + elapsed

    return {employee: minutes / 60.0 for employee, minutes in totals_minutes.items()}

