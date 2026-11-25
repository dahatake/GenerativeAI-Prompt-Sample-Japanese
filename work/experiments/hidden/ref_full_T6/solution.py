"""Reference implementation for T6 (full spec). MUTATIONS selects single-requirement violations for mutation testing."""
import csv, math, os, sys
from datetime import datetime, timedelta, timezone

MUTATIONS = set()
JST = timezone(timedelta(hours=9))


def _read(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _local(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc) if "M1_utc" in MUTATIONS else dt.astimezone(JST)


def _price(prices, sku, day):
    rows = sorted((r for r in prices if r["sku"] == sku), key=lambda r: r["effective_from"])
    if "M3_latest" in MUTATIONS:
        return int(rows[-1]["unit_price"])
    if "M3_first" in MUTATIONS:
        return int(rows[0]["unit_price"])
    valid = [r for r in rows if r["effective_from"] <= day]
    return int(valid[-1]["unit_price"])


def _billable(status):
    if "M2_completed_only" in MUTATIONS:
        return status == "completed"
    if "M2_not_cancelled" in MUTATIONS:
        return status != "cancelled"
    return status in ("completed", "shipped")


def make_invoices(data_dir, month):
    customers = _read(data_dir, "customers.csv")
    products = {r["sku"]: r for r in _read(data_dir, "products.csv")}
    prices = _read(data_dir, "prices.csv")
    tier = {r["customer_id"]: r["tier"] for r in customers}
    by_cust = {}
    for o in _read(data_dir, "orders.csv"):
        if not _billable(o["status"]):
            continue
        t = _local(o["ordered_at"])
        if t.strftime("%Y-%m") != month:
            continue
        price = _price(prices, o["sku"], t.strftime("%Y-%m-%d"))
        by_cust.setdefault(o["customer_id"], []).append((t, o, price, int(o["qty"])))
    if "M9_zero_invoices" in MUTATIONS:
        for c in tier:
            by_cust.setdefault(c, [])
    if "M8_csv_order" in MUTATIONS:
        order = [r["customer_id"] for r in customers if r["customer_id"] in by_cust]
    elif "M8_first_order" in MUTATIONS:
        far = datetime.max.replace(tzinfo=JST)
        order = sorted(by_cust, key=lambda c: min((x[0] for x in by_cust[c]), default=far))
    else:
        order = sorted(by_cust)
    invoices = []
    for n, cid in enumerate(order, 1):
        items = by_cust[cid]
        if "M10_file_order" not in MUTATIONS:
            items = sorted(items, key=lambda x: x[0])
        lines, groups = [], {}
        for t, o, price, qty in items:
            amount = price * qty
            lines.append({"order_id": o["order_id"], "sku": o["sku"], "qty": qty, "unit_price": price, "amount": amount})
            pct = 10 if ("M4_flat10" in MUTATIONS or products[o["sku"]]["category"] != "food") else 8
            groups.setdefault(pct, []).append(amount)
        subtotal = sum(l["amount"] for l in lines)
        discount = tax = 0
        gold = tier.get(cid) == "gold" and "M5_no_discount" not in MUTATIONS
        after_tax = "M5_after_tax" in MUTATIONS
        for pct, amounts in groups.items():
            g = sum(amounts)
            d = 0
            if gold and not after_tax:
                d = round(g * 0.05) if "M6_round" in MUTATIONS else g * 5 // 100
            discount += d
            if "M7_per_line" in MUTATIONS:
                tax += sum(a * pct // 100 for a in amounts) - (d * pct // 100)
            elif "M7_round" in MUTATIONS:
                tax += round((g - d) * pct / 100)
            else:
                tax += (g - d) * pct // 100
        if gold and after_tax:
            discount = (subtotal + tax) * 5 // 100
        total = subtotal - discount + tax
        invoices.append({"invoice_id": f"INV-{month.replace('-', '')}-{n:04d}", "customer_id": cid, "lines": lines,
                         "subtotal": subtotal, "discount": discount, "tax": tax, "total": total})
    return invoices


if __name__ == "__main__":
    import json
    print(json.dumps(make_invoices(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=1))
