"""発注計画の計算。

仕様（contract.md で合意済み）:
- 日平均需要 = today の前日までの直近28日間（today-28日 <= date < today）の出荷合計 / 28
- 発注点 ROP = 日平均需要 * lead_time_days + safety_stock
- 在庫ポジション IP = stock + on_order
- discontinued=true の品目は対象外
- IP <= ROP なら発注。qty = max(ceil((ROP - IP) / lot), 1) * lot
- 戻り値は qty > 0 の品目だけを sku 昇順で返す
- shipments にあって inventory に無い sku は無視する。不正データは ValueError を出す
"""

import csv
import datetime
import math
from fractions import Fraction

WINDOW_DAYS = 28

_INVENTORY_COLUMNS = ("sku", "stock", "on_order", "lead_time_days", "safety_stock", "lot", "discontinued")
_SHIPMENT_COLUMNS = ("date", "sku", "qty")


def _to_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError as e:
            raise ValueError(f"invalid date: {value!r}") from e
    raise ValueError(f"invalid date type: {type(value).__name__}")


def _to_int(value, field, line, minimum=0):
    try:
        n = int((value or "").strip())
    except ValueError as e:
        raise ValueError(f"line {line}: {field} is not an integer: {value!r}") from e
    if n < minimum:
        raise ValueError(f"line {line}: {field} must be >= {minimum}: {n}")
    return n


def _read_rows(path, required):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in required if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        # Header is line 1, so data rows start at line 2.
        return [(i, row) for i, row in enumerate(reader, start=2)]


def _load_inventory(path):
    items = {}
    for line, row in _read_rows(path, _INVENTORY_COLUMNS):
        sku = (row["sku"] or "").strip()
        if not sku:
            raise ValueError(f"line {line}: sku is empty")
        if sku in items:
            raise ValueError(f"line {line}: duplicate sku {sku!r}")
        flag = (row["discontinued"] or "").strip().lower()
        if flag not in ("true", "false"):
            raise ValueError(f"line {line}: discontinued must be true/false: {row['discontinued']!r}")
        items[sku] = {
            "stock": _to_int(row["stock"], "stock", line),
            "on_order": _to_int(row["on_order"], "on_order", line),
            "lead_time_days": _to_int(row["lead_time_days"], "lead_time_days", line),
            "safety_stock": _to_int(row["safety_stock"], "safety_stock", line),
            "lot": _to_int(row["lot"], "lot", line, minimum=1),
            "discontinued": flag == "true",
        }
    return items


def _demand_in_window(path, start, end):
    totals = {}
    for line, row in _read_rows(path, _SHIPMENT_COLUMNS):
        try:
            d = _to_date(row["date"] or "")
        except ValueError as e:
            raise ValueError(f"line {line}: {e}") from e
        sku = (row["sku"] or "").strip()
        if not sku:
            raise ValueError(f"line {line}: sku is empty")
        qty = _to_int(row["qty"], "qty", line)
        if start <= d < end:
            totals[sku] = totals.get(sku, 0) + qty
    return totals


def reorder_plan(inventory_path, shipments_path, today):
    end = _to_date(today)
    start = end - datetime.timedelta(days=WINDOW_DAYS)
    inventory = _load_inventory(inventory_path)
    demand = _demand_in_window(shipments_path, start, end)

    plan = []
    for sku in sorted(inventory):
        item = inventory[sku]
        if item["discontinued"]:
            continue
        daily = Fraction(demand.get(sku, 0), WINDOW_DAYS)
        rop = daily * item["lead_time_days"] + item["safety_stock"]
        position = item["stock"] + item["on_order"]
        if position > rop:
            continue
        lots = max(math.ceil((rop - position) / item["lot"]), 1)
        plan.append({"sku": sku, "qty": int(lots * item["lot"])})
    return plan
