"""勤怠 CSV から従業員ごとの月間労働時間を集計する。"""

import csv
import re
from datetime import datetime

REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")

BREAK_THRESHOLD_MINUTES = 6 * 60  # 拘束時間がこれを「超える」場合に休憩を控除
BREAK_MINUTES = 60
PAID_LEAVE_MINUTES = 450  # 所定労働時間 7.5h
ROUNDING_UNIT_MINUTES = 15  # シフトごとに 15 分単位で切り捨て
MINUTES_PER_DAY = 24 * 60

_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


def _parse_time(value, line_no):
    m = _TIME_RE.match(value)
    if not m:
        raise ValueError(f"line {line_no}: invalid time {value!r}")
    hour, minute = int(m.group(1)), int(m.group(2))
    if hour > 23 or minute > 59:
        raise ValueError(f"line {line_no}: invalid time {value!r}")
    return hour * 60 + minute


def _shift_minutes(start, end, line_no):
    start_min = _parse_time(start, line_no)
    end_min = _parse_time(end, line_no)
    if start_min == end_min:
        raise ValueError(f"line {line_no}: start and end are equal ({start})")
    span = end_min - start_min
    if span < 0:
        span += MINUTES_PER_DAY  # 翌日終了の夜勤
    if span > BREAK_THRESHOLD_MINUTES:
        span -= BREAK_MINUTES
    return span - span % ROUNDING_UNIT_MINUTES


def monthly_work_hours(path):
    """勤怠 CSV を読み、{従業員ID: 労働時間(時間, float)} を返す。"""
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return {}
        header = [name.strip() for name in reader.fieldnames]
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        reader.fieldnames = header

        for row in reader:
            line_no = reader.line_num
            values = {c: (row.get(c) or "").strip() for c in REQUIRED_COLUMNS}

            employee = values["employee"]
            if not employee:
                raise ValueError(f"line {line_no}: employee is empty")
            try:
                datetime.strptime(values["date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"line {line_no}: invalid date {values['date']!r}"
                ) from None

            kind = values["type"]
            if kind == "work":
                if not values["start"] or not values["end"]:
                    raise ValueError(f"line {line_no}: work row requires start and end")
                minutes = _shift_minutes(values["start"], values["end"], line_no)
            elif kind == "paid_leave":
                minutes = PAID_LEAVE_MINUTES
            else:
                raise ValueError(f"line {line_no}: unknown type {kind!r}")

            totals[employee] = totals.get(employee, 0) + minutes

    return {emp: minutes / 60.0 for emp, minutes in totals.items()}
