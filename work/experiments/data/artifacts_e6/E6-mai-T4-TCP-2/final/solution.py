import csv


_REQUIRED_COLUMNS = {"employee", "date", "type", "start", "end"}


def _parse_hhmm(value):
    parts = value.strip().split(":")
    if len(parts) != 2:
        raise ValueError("時刻は HH:MM 形式で指定してください")
    hour = int(parts[0])
    minute = int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("時刻の範囲が不正です")
    return hour * 60 + minute


def monthly_work_hours(path):
    """CSVの勤務・有給休暇行を従業員ごとに集計する。"""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("CSVヘッダーがありません")

        fieldnames = {name.strip() for name in reader.fieldnames if name is not None}
        missing = _REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError("必須ヘッダーがありません: " + ", ".join(sorted(missing)))

        for row in reader:
            employee = (row.get("employee") or "").strip()
            if not employee:
                continue

            shift_type = (row.get("type") or "").strip()

            if shift_type == "paid_leave":
                totals.setdefault(employee, 0.0)
                totals[employee] += 7.5
                continue

            if shift_type != "work":
                continue

            totals.setdefault(employee, 0.0)
            start_text = row.get("start") or ""
            end_text = row.get("end") or ""
            if not start_text.strip() or not end_text.strip():
                continue

            try:
                start = _parse_hhmm(start_text)
                end = _parse_hhmm(end_text)
                if end < start:
                    end += 24 * 60

                duration_minutes = end - start
                floored_minutes = (duration_minutes // 15) * 15
                totals[employee] += floored_minutes / 60.0
            except (ValueError, TypeError):
                continue

    return totals
