"""Reorder planning from inventory and shipment history (see contract.md)."""

import csv
import datetime
from fractions import Fraction

DEMAND_WINDOW_DAYS = 28

INVENTORY_COLUMNS = (
    "sku", "name", "stock", "on_order", "lead_time_days",
    "safety_stock", "lot", "discontinued",
)
SHIPMENT_COLUMNS = ("date", "sku", "qty")


def _to_date(value):
    # datetime.datetime is a subclass of datetime.date, so check it first.
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError as exc:
            raise ValueError(f"invalid date: {value!r}") from exc
    raise ValueError(f"unsupported today type: {type(value).__name__}")


def _to_int(value, column, line):
    try:
        return int(value.strip())
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"line {line}: invalid integer in {column!r}: {value!r}") from exc


def _to_bool(value, column, line):
    text = (value or "").strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError(f"line {line}: invalid boolean in {column!r}: {value!r}")


def _read_rows(path, required):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in required if c not in header]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        reader.fieldnames = header
        # Line numbers are 1-based and include the header line.
        return [(i, row) for i, row in enumerate(reader, start=2)]


def _load_inventory(path):
    items = {}
    for line, row in _read_rows(path, INVENTORY_COLUMNS):
        sku = (row["sku"] or "").strip()
        if not sku:
            raise ValueError(f"line {line}: empty sku")
        if sku in items:
            raise ValueError(f"line {line}: duplicate sku {sku!r}")
        item = {c: _to_int(row[c], c, line)
                for c in ("stock", "on_order", "lead_time_days", "safety_stock", "lot")}
        if item["lot"] <= 0:
            raise ValueError(f"line {line}: lot must be positive: {item['lot']}")
        item["discontinued"] = _to_bool(row["discontinued"], "discontinued", line)
        items[sku] = item
    return items


def _load_demand(path, start, end):
    """Sum shipment qty per sku for dates in [start, end)."""
    totals = {}
    for line, row in _read_rows(path, SHIPMENT_COLUMNS):
        try:
            date = datetime.date.fromisoformat((row["date"] or "").strip())
        except ValueError as exc:
            raise ValueError(f"line {line}: invalid date: {row['date']!r}") from exc
        sku = (row["sku"] or "").strip()
        qty = _to_int(row["qty"], "qty", line)
        if start <= date < end:
            totals[sku] = totals.get(sku, 0) + qty
    return totals


def reorder_plan(inventory_path, shipments_path, today):
    today = _to_date(today)
    window_start = today - datetime.timedelta(days=DEMAND_WINDOW_DAYS)
    inventory = _load_inventory(inventory_path)
    demand = _load_demand(shipments_path, window_start, today)

    plan = []
    for sku in sorted(inventory):
        item = inventory[sku]
        if item["discontinued"]:
            continue
        daily = Fraction(demand.get(sku, 0), DEMAND_WINDOW_DAYS)
        rop = daily * item["lead_time_days"] + item["safety_stock"]
        position = item["stock"] + item["on_order"]
        if position > rop:
            continue
        need = rop - position
        lot = item["lot"]
        lots = -(-need // lot)  # ceil for Fraction
        # Ordering is triggered at position == ROP too, so order at least one lot.
        qty = int(max(lots, 1) * lot)
        plan.append({"sku": sku, "qty": qty})
    return plan
