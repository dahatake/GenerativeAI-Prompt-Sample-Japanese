import csv
import math
from datetime import date, datetime, timedelta

LOOKBACK_DAYS = 30


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value).strip()[:10], "%Y-%m-%d").date()


def _to_bool(value):
    return str(value).strip().lower() in ("true", "1", "yes", "y")


def _to_num(value, default=0.0):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    window_start = today - timedelta(days=LOOKBACK_DAYS)

    # Total shipped per SKU in [today - 30 days, today) — today's partial data is excluded.
    shipped = {}
    with open(shipments_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                d = _to_date(row["date"])
            except (KeyError, ValueError):
                continue
            if window_start <= d < today:
                sku = row["sku"].strip()
                shipped[sku] = shipped.get(sku, 0.0) + _to_num(row.get("qty"))

    plan = []
    with open(inventory_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sku = row["sku"].strip()
            if _to_bool(row.get("discontinued", "false")):
                continue
            stock = _to_num(row.get("stock"))
            on_order = _to_num(row.get("on_order"))
            lead_time = _to_num(row.get("lead_time_days"))
            safety = _to_num(row.get("safety_stock"))
            lot = int(_to_num(row.get("lot"), 1)) or 1
            if lot < 1:
                lot = 1

            daily_demand = max(shipped.get(sku, 0.0), 0.0) / LOOKBACK_DAYS
            reorder_point = daily_demand * lead_time + safety
            position = stock + on_order
            if position > reorder_point:
                continue
            shortage = reorder_point - position
            lots = max(1, math.ceil(shortage / lot - 1e-9))
            plan.append({"sku": sku, "qty": lots * lot})

    plan.sort(key=lambda r: r["sku"])
    return plan


if __name__ == "__main__":
    import sys

    print(reorder_plan("inventory.csv", "shipments.csv", sys.argv[1] if len(sys.argv) > 1 else date.today()))
