import csv
import datetime as _dt
from fractions import Fraction

WINDOW_DAYS = 28

_INVENTORY_COLUMNS = ("sku", "stock", "on_order", "lead_time_days", "safety_stock", "lot", "discontinued")
_SHIPMENT_COLUMNS = ("date", "sku", "qty")


def _parse_date(value, label):
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    if isinstance(value, str):
        try:
            return _dt.date.fromisoformat(value.strip())
        except ValueError:
            pass
    raise ValueError(f"invalid date for {label}: {value!r}")


def _parse_int(value, label, minimum=0):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"invalid integer for {label}: {value!r}") from None
    if number < minimum:
        raise ValueError(f"{label} must be >= {minimum}: {number}")
    return number


def _parse_bool(value, label):
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError(f"invalid boolean for {label}: {value!r}")


def _read_rows(path, required):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in required if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        return list(reader)


def _load_inventory(path):
    items = {}
    for line, row in enumerate(_read_rows(path, _INVENTORY_COLUMNS), start=2):
        sku = (row["sku"] or "").strip()
        if not sku:
            raise ValueError(f"{path}:{line}: empty sku")
        if sku in items:
            raise ValueError(f"{path}:{line}: duplicate sku {sku!r}")
        where = f"{path}:{line}"
        items[sku] = {
            "stock": _parse_int(row["stock"], f"{where} stock"),
            "on_order": _parse_int(row["on_order"], f"{where} on_order"),
            "lead_time_days": _parse_int(row["lead_time_days"], f"{where} lead_time_days"),
            "safety_stock": _parse_int(row["safety_stock"], f"{where} safety_stock"),
            "lot": _parse_int(row["lot"], f"{where} lot", minimum=1),
            "discontinued": _parse_bool(row["discontinued"], f"{where} discontinued"),
        }
    return items


def _window_totals(path, start, end):
    totals = {}
    for line, row in enumerate(_read_rows(path, _SHIPMENT_COLUMNS), start=2):
        where = f"{path}:{line}"
        day = _parse_date(row["date"], f"{where} date")
        qty = _parse_int(row["qty"], f"{where} qty")
        sku = (row["sku"] or "").strip()
        if start <= day < end:
            totals[sku] = totals.get(sku, 0) + qty
    return totals


def reorder_plan(inventory_path, shipments_path, today):
    """Return [{"sku", "qty"}] for items whose stock + on_order <= reorder point.

    Daily demand = shipments in [today - 28 days, today) / 28.
    Reorder point = daily demand * lead_time_days + safety_stock.
    qty = ceil((reorder point - (stock + on_order)) / lot) * lot, at least one lot.
    """
    today = _parse_date(today, "today")
    inventory = _load_inventory(inventory_path)
    totals = _window_totals(shipments_path, today - _dt.timedelta(days=WINDOW_DAYS), today)

    plan = []
    for sku in sorted(inventory):
        item = inventory[sku]
        if item["discontinued"]:
            continue
        daily_demand = Fraction(totals.get(sku, 0), WINDOW_DAYS)
        reorder_point = daily_demand * item["lead_time_days"] + item["safety_stock"]
        position = item["stock"] + item["on_order"]
        if position > reorder_point:
            continue
        shortfall = reorder_point - position
        lots = max(-(-shortfall // item["lot"]), 1)
        plan.append({"sku": sku, "qty": int(lots * item["lot"])})
    return plan
