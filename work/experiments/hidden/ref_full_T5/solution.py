import csv, math
from datetime import date, timedelta
def _d(x):
    return x if isinstance(x, date) else date.fromisoformat(str(x))
def reorder_plan(inventory_path, shipments_path, today):
    today = _d(today)
    start = today - timedelta(days=28)
    tot = {}
    with open(shipments_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r["date"])
            if start <= d < today:
                tot[r["sku"]] = tot.get(r["sku"], 0) + int(r["qty"])
    out = []
    with open(inventory_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["discontinued"].strip().lower() == "true":
                continue
            avg = tot.get(r["sku"], 0) / 28
            rop = avg * int(r["lead_time_days"]) + int(r["safety_stock"])
            eff = int(r["stock"]) + int(r["on_order"])
            if eff <= rop:
                lot = int(r["lot"])
                qty = math.ceil((rop - eff) / lot - 1e-9) * lot
                out.append({"sku": r["sku"], "qty": int(qty)})
    return sorted(out, key=lambda x: x["sku"])
