"""sales.csv の売上を月次(日本時間)・税抜で集計する。"""
from __future__ import annotations

import csv
import re
import warnings
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterator

# JST は夏時間がないため固定オフセットで扱う(tzdata 不要)
JST = timezone(timedelta(hours=9), "JST")
REQUIRED_COLUMNS = ("order_id", "ordered_at", "amount_incl_tax", "status")
COUNTED_STATUS = "completed"
KNOWN_STATUSES = {"completed", "cancelled"}
_INT_RE = re.compile(r"-?\d+")


def _parse_utc(value: str, line_no: int) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        raise ValueError(f"line {line_no}: invalid ordered_at {value!r}") from None
    if dt.tzinfo is None:
        raise ValueError(f"line {line_no}: ordered_at has no timezone {value!r}")
    return dt


def _parse_amount(value: str, line_no: int) -> int:
    text = value.strip()
    if not _INT_RE.fullmatch(text):
        raise ValueError(f"line {line_no}: amount_incl_tax is not an integer {value!r}")
    return int(text)


def to_tax_excluded(amount_incl_tax: int) -> int:
    """税込(10%)→税抜。整数演算で ÷1.1 し、0 方向に切り捨てる。"""
    q = abs(amount_incl_tax) * 10 // 11
    return q if amount_incl_tax >= 0 else -q


def _month_range(first: str, last: str) -> Iterator[str]:
    y, m = map(int, first.split("-"))
    ly, lm = map(int, last.split("-"))
    while (y, m) <= (ly, lm):
        yield f"{y:04d}-{m:02d}"
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def monthly_sales(path: str) -> Dict[str, int]:
    """月次の税抜売上 {"YYYY-MM": int} を返す。

    - 月は ordered_at(UTC)を日本時間に変換して判定
    - status == "completed" のみ集計(マイナス金額もそのまま計上)
    - 金額は行ごとに税抜へ換算してから合計
    - 最初の月〜最後の月の間で注文のない月は 0 を入れる
    """
    totals: Dict[str, int] = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return {}
        header = [h.strip() for h in reader.fieldnames]
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise ValueError(f"missing columns: {missing}")
        reader.fieldnames = header
        for row in reader:
            line_no = reader.line_num
            if None in row:
                raise ValueError(f"line {line_no}: too many fields")
            values = [row[c] for c in REQUIRED_COLUMNS]
            if all(v is None or not v.strip() for v in values):
                continue  # 空白だけの行
            if any(v is None for v in values):
                raise ValueError(f"line {line_no}: too few fields")
            status = row["status"].strip()
            if not status:
                raise ValueError(f"line {line_no}: empty status")
            ordered_at = _parse_utc(row["ordered_at"], line_no)
            amount = _parse_amount(row["amount_incl_tax"], line_no)
            if status != COUNTED_STATUS:
                if status not in KNOWN_STATUSES:
                    warnings.warn(f"line {line_no}: unknown status {status!r} skipped")
                continue
            month = ordered_at.astimezone(JST).strftime("%Y-%m")
            totals[month] = totals.get(month, 0) + to_tax_excluded(amount)
    if not totals:
        return {}
    return {m: totals.get(m, 0) for m in _month_range(min(totals), max(totals))}


if __name__ == "__main__":
    import sys
    print(monthly_sales(sys.argv[1] if len(sys.argv) > 1 else "sales.csv"))
