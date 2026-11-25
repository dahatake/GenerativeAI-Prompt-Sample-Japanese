import csv
import datetime as dt
import math
from fractions import Fraction

DEMAND_WINDOW_DAYS = 28
_TRUE_VALUES = {"true", "1", "yes", "y", "t"}


def _to_date(today):
    if isinstance(today, dt.datetime):
        return today.date()
    if isinstance(today, dt.date):
        return today
    if isinstance(today, str):
        return dt.date.fromisoformat(today.strip())
    raise TypeError(f"today must be date or 'YYYY-MM-DD' string, got {type(today).__name__}")


def _read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _demand_by_sku(shipments_path, today):
    start = today - dt.timedelta(days=DEMAND_WINDOW_DAYS)
    totals = {}
    for row in _read_rows(shipments_path):
        ship_date = dt.date.fromisoformat(row["date"].strip())
        if start <= ship_date < today:
            sku = row["sku"].strip()
            totals[sku] = totals.get(sku, 0) + int(row["qty"])
    return {sku: Fraction(total, DEMAND_WINDOW_DAYS) for sku, total in totals.items()}


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    demand = _demand_by_sku(shipments_path, today)

    plan = []
    for row in _read_rows(inventory_path):
        if row["discontinued"].strip().lower() in _TRUE_VALUES:
            continue
        sku = row["sku"].strip()
        lot = int(row["lot"])
        if lot < 1:
            raise ValueError(f"lot must be >= 1 for sku {sku}: {lot}")

        rop = demand.get(sku, Fraction(0)) * int(row["lead_time_days"]) + int(row["safety_stock"])
        position = int(row["stock"]) + int(row["on_order"])
        if position > rop:
            continue

        # When position == ROP the shortfall is 0, but an order is still required,
        # so at least one lot is ordered.
        lots = max(1, math.ceil((rop - position) / lot))
        plan.append({"sku": sku, "qty": lots * lot})

    plan.sort(key=lambda item: item["sku"])
    return plan
