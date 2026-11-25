import csv
def reorder_plan(inventory_path, shipments_path, today):
    tot = {}
    with open(shipments_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            tot[r["sku"]] = tot.get(r["sku"], 0) + int(r["qty"])
    out = []
    with open(inventory_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            avg = tot.get(r["sku"], 0) / 30
            rop = avg * int(r["lead_time_days"]) + int(r["safety_stock"])
            if int(r["stock"]) < rop:
                out.append({"sku": r["sku"], "qty": int(rop - int(r["stock"]))})
    return out
