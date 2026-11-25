import csv
import datetime as dt
import math
from collections import defaultdict
from fractions import Fraction

WINDOW_DAYS = 28


def _to_date(value):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value).strip())


def _read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    window_start = today - dt.timedelta(days=WINDOW_DAYS)

    shipped = defaultdict(int)
    for row in _read_csv(shipments_path):
        ship_date = _to_date(row["date"])
        if window_start <= ship_date < today:
            shipped[row["sku"].strip()] += int(row["qty"])

    plan = []
    for row in _read_csv(inventory_path):
        if row["discontinued"].strip().lower() == "true":
            continue
        sku = row["sku"].strip()
        lot = int(row["lot"])
        position = int(row["stock"]) + int(row["on_order"])
        daily_demand = Fraction(shipped.get(sku, 0), WINDOW_DAYS)
        reorder_point = daily_demand * int(row["lead_time_days"]) + int(row["safety_stock"])
        if position > reorder_point:
            continue
        # Being exactly at the reorder point still triggers an order: at least one lot.
        lots = max(1, math.ceil((reorder_point - position) / lot))
        plan.append({"sku": sku, "qty": lots * lot})

    plan.sort(key=lambda item: item["sku"])
    return plan
