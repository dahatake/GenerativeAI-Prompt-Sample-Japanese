import csv


def _minutes(time_text):
    if time_text is None:
        return None
    text = time_text.strip()
    if not text:
        return None
    parts = text.split(":")
    if len(parts) != 2:
        raise ValueError("Invalid time format: {0}".format(time_text))
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        raise ValueError("Invalid time format: {0}".format(time_text))
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("Invalid time format: {0}".format(time_text))
    return hour * 60 + minute


def monthly_work_hours(path):
    """Return each employee's approved monthly work hours as a float dict."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            employee = (row.get("employee") or "").strip()
            if not employee:
                continue

            shift_type = (row.get("type") or "").strip()
            if shift_type == "paid_leave":
                totals[employee] = totals.get(employee, 0.0) + 7.5
                continue
            if shift_type != "work":
                continue

            start_text = row.get("start")
            end_text = row.get("end")
            if start_text is None or end_text is None:
                continue
            if not start_text.strip() or not end_text.strip():
                continue

            start = _minutes(start_text)
            end = _minutes(end_text)

            if end < start:
                end += 24 * 60

            elapsed = end - start
            net_minutes = elapsed - 60 if elapsed > 6 * 60 else elapsed
            if net_minutes < 0:
                net_minutes = 0
            net_minutes = (net_minutes // 15) * 15
            totals[employee] = totals.get(employee, 0.0) + net_minutes / 60.0

    return totals
