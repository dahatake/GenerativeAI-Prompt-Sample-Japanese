import csv
import datetime as _dt
from fractions import Fraction

WINDOW_DAYS = 28

_INVENTORY_INT_COLUMNS = ("stock", "on_order", "lead_time_days", "safety_stock", "lot")
_INVENTORY_COLUMNS = ("sku",) + _INVENTORY_INT_COLUMNS + ("discontinued",)
_SHIPMENT_COLUMNS = ("date", "sku", "qty")
_TRUE_VALUES = {"true", "1", "yes"}
_FALSE_VALUES = {"false", "0", "no", ""}


def _to_date(value):
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    if isinstance(value, str):
        try:
            return _dt.date.fromisoformat(value.strip())
        except ValueError as exc:
            raise ValueError(f"invalid date: {value!r}") from exc
    raise ValueError(f"unsupported date type: {type(value).__name__}")


def _non_negative_int(value, column, line):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"line {line}: {column} must be an integer, got {value!r}") from exc
    if number < 0:
        raise ValueError(f"line {line}: {column} must be >= 0, got {number}")
    return number


def _parse_bool(value, line):
    text = (value or "").strip().lower()
    if text in _TRUE_VALUES:
        return True
    if text in _FALSE_VALUES:
        return False
    raise ValueError(f"line {line}: invalid discontinued value {value!r}")


def _read_rows(path, required):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in required if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        return [(reader.line_num, row) for row in reader]


def _load_inventory(path):
    items = {}
    for line, row in _read_rows(path, _INVENTORY_COLUMNS):
        sku = (row["sku"] or "").strip()
        if not sku:
            raise ValueError(f"line {line}: empty sku")
        if sku in items:
            raise ValueError(f"line {line}: duplicate sku {sku!r}")
        item = {c: _non_negative_int(row[c], c, line) for c in _INVENTORY_INT_COLUMNS}
        if item["lot"] <= 0:
            raise ValueError(f"line {line}: lot must be > 0")
        item["discontinued"] = _parse_bool(row["discontinued"], line)
        items[sku] = item
    return items


def _load_demand(path, skus, start, end):
    """Sum shipped qty per sku for start <= date < end."""
    totals = dict.fromkeys(skus, 0)
    for line, row in _read_rows(path, _SHIPMENT_COLUMNS):
        try:
            day = _to_date(row["date"])
        except ValueError as exc:
            raise ValueError(f"line {line}: {exc}") from exc
        qty = _non_negative_int(row["qty"], "qty", line)
        sku = (row["sku"] or "").strip()
        if sku in totals and start <= day < end:
            totals[sku] += qty
    return totals


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    inventory = _load_inventory(inventory_path)
    demand = _load_demand(
        shipments_path, inventory, today - _dt.timedelta(days=WINDOW_DAYS), today
    )

    plan = []
    for sku in sorted(inventory):
        item = inventory[sku]
        if item["discontinued"]:
            continue
        daily = Fraction(demand[sku], WINDOW_DAYS)
        reorder_point = daily * item["lead_time_days"] + item["safety_stock"]
        position = item["stock"] + item["on_order"]
        if position > reorder_point:
            continue
        lot = item["lot"]
        shortfall = reorder_point - position
        lots = max(1, -(-shortfall.numerator // (shortfall.denominator * lot)))
        plan.append({"sku": sku, "qty": int(lots * lot)})
    return plan
