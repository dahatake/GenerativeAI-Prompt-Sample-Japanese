from __future__ import annotations

import csv
from datetime import datetime, timedelta


def _parse_time(value: str, line: int, field: str) -> datetime:
    try:
        return datetime.strptime(value.strip(), "%H:%M")
    except ValueError:
        raise ValueError(f"line {line}: invalid {field} time {value!r}") from None


def monthly_work_hours(path) -> dict[str, float]:
    """勤怠CSVから従業員ごとの労働時間(時間)を集計する。

    - type が "work" の行のみ end - start を加算する(休憩控除なし)。
    - end < start は日跨ぎ勤務として翌日終了とみなす。
    - paid_leave などの work 以外の行は 0 時間(従業員キーは含める)。
    """
    totals: dict[str, float] = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line = reader.line_num
            if not any((v or "").strip() for v in row.values()):
                continue
            emp = (row.get("employee") or "").strip()
            if not emp:
                raise ValueError(f"line {line}: missing employee")
            totals.setdefault(emp, 0.0)
            if (row.get("type") or "").strip() != "work":
                continue
            start_s = row.get("start") or ""
            end_s = row.get("end") or ""
            if not start_s.strip() or not end_s.strip():
                raise ValueError(f"line {line}: work row requires start and end")
            start = _parse_time(start_s, line, "start")
            end = _parse_time(end_s, line, "end")
            if end == start:
                raise ValueError(f"line {line}: start equals end (ambiguous)")
            if end < start:
                end += timedelta(days=1)
            totals[emp] += (end - start).total_seconds() / 3600
    return totals
