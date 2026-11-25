import csv
from datetime import datetime


def _parse_time(value, row_no):
    try:
        return datetime.strptime(value.strip(), "%H:%M")
    except (ValueError, AttributeError):
        raise ValueError(f"行 {row_no}: 時刻の形式が不正です: {value!r}")


def monthly_work_hours(path):
    """勤怠CSVから従業員ごとの労働時間(時間, float)を集計して返す。

    - type == "work" の行のみ end - start を加算（日跨ぎは end に24時間加算）
    - work 以外（paid_leave 等）は 0 時間（従業員キーは 0.0 で出力）
    - 休憩控除・丸め・月での按分は行わない
    - work 行で時刻欠損・形式不正の場合は ValueError
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row_no, row in enumerate(reader, start=2):
            emp = (row.get("employee") or "").strip()
            if not emp:
                raise ValueError(f"行 {row_no}: employee が空です")
            totals.setdefault(emp, 0.0)
            if (row.get("type") or "").strip() != "work":
                continue
            start = _parse_time(row.get("start") or "", row_no)
            end = _parse_time(row.get("end") or "", row_no)
            minutes = (end - start).total_seconds() / 60
            if minutes < 0:
                minutes += 24 * 60
            totals[emp] += minutes / 60
    return totals
