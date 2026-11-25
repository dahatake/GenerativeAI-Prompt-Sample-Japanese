import csv
import math
from datetime import date, datetime, timedelta

LOOKBACK_DAYS = 28


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()


def _to_bool(value):
    return str(value).strip().lower() in ("true", "1", "yes", "y", "t")


def _to_int(value, default=0):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def _read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    window_start = today - timedelta(days=LOOKBACK_DAYS)

    # Demand = shipments in the LOOKBACK_DAYS full days before today (today excluded).
    shipped = {}
    for row in _read_csv(shipments_path):
        try:
            d = _to_date(row["date"])
        except (KeyError, ValueError):
            continue
        if window_start <= d < today:
            sku = (row.get("sku") or "").strip()
            shipped[sku] = shipped.get(sku, 0) + _to_int(row.get("qty"))

    plan = []
    for row in _read_csv(inventory_path):
        sku = (row.get("sku") or "").strip()
        if not sku or _to_bool(row.get("discontinued", "")):
            continue

        daily_demand = max(shipped.get(sku, 0), 0) / LOOKBACK_DAYS
        lead_time = max(_to_int(row.get("lead_time_days")), 0)
        safety = max(_to_int(row.get("safety_stock")), 0)
        lot = _to_int(row.get("lot"), 1)
        if lot <= 0:
            lot = 1

        reorder_point = daily_demand * lead_time + safety
        position = _to_int(row.get("stock")) + _to_int(row.get("on_order"))

        if position <= reorder_point:
            shortfall = math.ceil(reorder_point - position)
            qty = max(math.ceil(shortfall / lot), 1) * lot
            plan.append({"sku": sku, "qty": qty})

    plan.sort(key=lambda x: x["sku"])
    return plan
