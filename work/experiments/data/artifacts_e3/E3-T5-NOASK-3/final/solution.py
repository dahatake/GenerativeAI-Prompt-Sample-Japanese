import csv
import math
from datetime import date, datetime, timedelta
from fractions import Fraction

DEMAND_WINDOW_DAYS = 30


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value.strip())
    raise TypeError(f"today must be date, datetime or 'YYYY-MM-DD' string: {value!r}")


def _parse_bool(value):
    return str(value).strip().lower() in ("true", "1", "yes")


def _load_demand(shipments_path, today):
    """Sum of shipped qty per SKU in [today - 30 days, today - 1 day]."""
    start = today - timedelta(days=DEMAND_WINDOW_DAYS)
    totals = {}
    with open(shipments_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            shipped_on = date.fromisoformat(row["date"].strip())
            if start <= shipped_on < today:
                sku = row["sku"].strip()
                totals[sku] = totals.get(sku, 0) + int(row["qty"])
    return totals


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    totals = _load_demand(shipments_path, today)

    plan = []
    with open(inventory_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if _parse_bool(row["discontinued"]):
                continue
            sku = row["sku"].strip()
            stock = int(row["stock"])
            on_order = int(row["on_order"])
            lead_time = int(row["lead_time_days"])
            safety_stock = int(row["safety_stock"])
            lot = int(row["lot"])
            if lot <= 0:
                raise ValueError(f"lot must be positive for {sku}: {lot}")

            # Fraction keeps the reorder point exact (no float rounding at ceil).
            daily_demand = Fraction(totals.get(sku, 0), DEMAND_WINDOW_DAYS)
            reorder_point = daily_demand * lead_time + safety_stock
            position = stock + on_order
            if position < reorder_point:
                shortfall = reorder_point - position
                qty = math.ceil(shortfall / lot) * lot
                plan.append({"sku": sku, "qty": qty})

    plan.sort(key=lambda item: item["sku"])
    return plan
