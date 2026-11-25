import csv
import math
from datetime import date, datetime, timedelta
from fractions import Fraction

WINDOW_DAYS = 28
_TRUE_VALUES = {"true", "1", "yes", "y", "t"}


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value).strip()[:10], "%Y-%m-%d").date()


def _to_int(value, default=0):
    if value is None or str(value).strip() == "":
        return default
    return int(Fraction(str(value).strip()))


def _read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    start = today - timedelta(days=WINDOW_DAYS)

    shipped = {}
    for row in _read_csv(shipments_path):
        if not (row.get("date") or "").strip():
            continue
        d = _to_date(row["date"])
        if start <= d < today:
            sku = row["sku"].strip()
            shipped[sku] = shipped.get(sku, 0) + Fraction(str(row["qty"]).strip())

    plan = []
    for row in _read_csv(inventory_path):
        if (row.get("discontinued") or "").strip().lower() in _TRUE_VALUES:
            continue
        sku = row["sku"].strip()
        effective = _to_int(row.get("stock")) + _to_int(row.get("on_order"))
        daily_avg = shipped.get(sku, Fraction(0)) / WINDOW_DAYS
        reorder_point = daily_avg * _to_int(row.get("lead_time_days")) + _to_int(row.get("safety_stock"))
        if effective > reorder_point:
            continue
        lot = _to_int(row.get("lot"), 1)
        if lot <= 0:
            lot = 1
        shortage = reorder_point - effective
        # 有効在庫 == 発注点 (不足 0) でも発注対象のため、最低 1 ロットは発注する
        qty = max(math.ceil(shortage / lot), 1) * lot
        plan.append({"sku": sku, "qty": int(qty)})

    plan.sort(key=lambda r: r["sku"])
    return plan
