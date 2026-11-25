import csv


def _minutes(time_text):
    hour_text, minute_text = time_text.strip().split(":")
    hour = int(hour_text)
    minute = int(minute_text)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("Invalid time: {}".format(time_text))
    return hour * 60 + minute


def _shift_hours(start_text, end_text):
    start = _minutes(start_text)
    end = _minutes(end_text)
    duration = end - start
    if duration < 0:
        duration += 24 * 60

    if duration > 6 * 60:
        duration -= 60

    duration -= duration % 15
    return float(duration) / 60.0


def monthly_work_hours(path):
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            return totals

        required = {"employee", "type", "start", "end"}
        missing = required.difference(reader.fieldnames)
        if missing:
            raise ValueError("Missing required CSV columns: {}".format(
                ", ".join(sorted(missing))))

        for row in reader:
            employee = row["employee"]
            if employee is None:
                continue
            employee = employee.strip()
            if not employee:
                continue

            shift_type = (row["type"] or "").strip()
            if shift_type == "paid_leave":
                totals[employee] = totals.get(employee, 0.0) + 7.5
            elif shift_type == "work":
                start = (row["start"] or "").strip()
                end = (row["end"] or "").strip()
                if not start or not end:
                    continue
                totals[employee] = totals.get(employee, 0.0) + _shift_hours(start, end)

    return totals
