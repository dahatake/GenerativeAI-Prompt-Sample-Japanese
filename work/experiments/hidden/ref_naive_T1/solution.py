import csv
def monthly_sales(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = r["ordered_at"][:7]
            out[k] = out.get(k, 0) + int(r["amount_incl_tax"])
    return out
