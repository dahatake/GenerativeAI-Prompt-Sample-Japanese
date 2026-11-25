import csv
import datetime as dt
import math
from collections import defaultdict
from fractions import Fraction

DEMAND_WINDOW_DAYS = 28


def _to_date(value):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        return dt.date.fromisoformat(value.strip())
    raise TypeError(f"unsupported type for today: {type(value).__name__}")


def _parse_bool(value):
    text = value.strip().lower()
    if text in ("true", "1", "yes"):
        return True
    if text in ("false", "0", "no", ""):
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def _read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    window_start = today - dt.timedelta(days=DEMAND_WINDOW_DAYS)

    shipped = defaultdict(int)
    for row in _read_rows(shipments_path):
        date = dt.date.fromisoformat(row["date"].strip())
        if window_start <= date < today:
            shipped[row["sku"].strip()] += int(row["qty"])

    plan = []
    for row in _read_rows(inventory_path):
        if _parse_bool(row["discontinued"]):
            continue
        sku = row["sku"].strip()
        lot = int(row["lot"])
        if lot <= 0:
            raise ValueError(f"lot must be positive for sku {sku}")

        daily_demand = Fraction(shipped.get(sku, 0), DEMAND_WINDOW_DAYS)
        reorder_point = daily_demand * int(row["lead_time_days"]) + int(row["safety_stock"])
        position = int(row["stock"]) + int(row["on_order"])

        if position <= reorder_point:
            lots = max(1, math.ceil((reorder_point - position) / lot))
            plan.append({"sku": sku, "qty": lots * lot})

    plan.sort(key=lambda item: item["sku"])
    return plan
