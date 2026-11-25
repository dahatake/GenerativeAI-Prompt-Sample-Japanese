import csv
import datetime as dt
import math
from fractions import Fraction

WINDOW_DAYS = 30


def _to_date(value):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value).strip())


def _parse_bool(value):
    v = str(value).strip().lower()
    if v in ("true", "1", "yes"):
        return True
    if v in ("false", "0", "no", ""):
        return False
    raise ValueError(f"invalid boolean: {value!r}")


def _non_negative_int(row, key):
    value = int(str(row[key]).strip())
    if value < 0:
        raise ValueError(f"{key} must be >= 0: {value}")
    return value


def _read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    window_start = today - dt.timedelta(days=WINDOW_DAYS)

    items = []
    for row in _read_csv(inventory_path):
        lot = _non_negative_int(row, "lot")
        if lot == 0:
            raise ValueError(f"lot must be > 0: sku={row['sku']}")
        items.append({
            "sku": row["sku"].strip(),
            "stock": _non_negative_int(row, "stock"),
            "on_order": _non_negative_int(row, "on_order"),
            "lead_time_days": _non_negative_int(row, "lead_time_days"),
            "safety_stock": _non_negative_int(row, "safety_stock"),
            "lot": lot,
            "discontinued": _parse_bool(row["discontinued"]),
        })

    demand = {item["sku"]: 0 for item in items}
    for row in _read_csv(shipments_path):
        sku = row["sku"].strip()
        ship_date = _to_date(row["date"])
        qty = _non_negative_int(row, "qty")
        # Window is [today-30, today-1]; today and future rows are excluded.
        if sku in demand and window_start <= ship_date < today:
            demand[sku] += qty

    plan = []
    for item in items:
        if item["discontinued"]:
            continue
        daily = Fraction(demand[item["sku"]], WINDOW_DAYS)
        reorder_point = daily * item["lead_time_days"] + item["safety_stock"]
        position = item["stock"] + item["on_order"]
        if position < reorder_point:
            lots = math.ceil((reorder_point - position) / item["lot"])
            plan.append({"sku": item["sku"], "qty": lots * item["lot"]})

    return sorted(plan, key=lambda p: p["sku"])
