import csv
import math
from datetime import date, datetime, timedelta

LOOKBACK_DAYS = 30
_TRUE_VALUES = {"true", "1", "yes", "y", "t"}


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value).strip()[:10])


def _read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            if any(row.values()):
                yield row


def _num(value, default=0.0):
    try:
        return float(value) if value != "" else default
    except ValueError:
        return default


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    window_start = today - timedelta(days=LOOKBACK_DAYS)

    shipped = {}
    first_date = None
    for row in _read_rows(shipments_path):
        try:
            d = _to_date(row["date"])
        except (KeyError, ValueError):
            continue
        if d >= today:
            continue
        if first_date is None or d < first_date:
            first_date = d
        if d >= window_start:
            shipped[row.get("sku", "")] = shipped.get(row.get("sku", ""), 0.0) + _num(row.get("qty"))

    # If history is shorter than the lookback window, average over the observed span only.
    days = LOOKBACK_DAYS
    if first_date is not None and first_date > window_start:
        days = max((today - first_date).days, 1)

    plan = []
    for row in _read_rows(inventory_path):
        sku = row.get("sku", "")
        if not sku or row.get("discontinued", "").lower() in _TRUE_VALUES:
            continue
        daily = shipped.get(sku, 0.0) / days
        reorder_point = daily * _num(row.get("lead_time_days")) + _num(row.get("safety_stock"))
        position = _num(row.get("stock")) + _num(row.get("on_order"))
        if position > reorder_point:
            continue
        lot = int(_num(row.get("lot"), 1)) or 1
        if lot < 1:
            lot = 1
        shortage = reorder_point - position
        lots = max(1, math.ceil(round(shortage, 9) / lot))
        plan.append({"sku": sku, "qty": lots * lot})

    plan.sort(key=lambda x: x["sku"])
    return plan
