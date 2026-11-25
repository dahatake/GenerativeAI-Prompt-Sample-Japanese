"""Monthly invoice generation from customers/products/prices/orders CSV files."""

import csv
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
TAX_RATE_PERCENT = {"general": 10, "food": 8}
DISCOUNT_RATE_PERCENT = {"gold": 5, "standard": 0}
CSV_FIELDS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _parse_month(month):
    m = re.fullmatch(r"(\d{4})-(\d{2})", month) if isinstance(month, str) else None
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")
    return int(m.group(1)), int(m.group(2))


def _to_jst(ordered_at):
    dt = datetime.fromisoformat(ordered_at.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"ordered_at has no timezone: {ordered_at!r}")
    return dt.astimezone(JST)


def _unit_price(price_history, sku, order_date):
    candidates = [p for p in price_history.get(sku, []) if p[0] <= order_date]
    if not candidates:
        raise ValueError(f"no effective price for {sku} on {order_date.isoformat()}")
    return max(candidates)[1]


def make_invoices(data_dir, month):
    year, mon = _parse_month(month)

    tiers = {r["customer_id"]: r["tier"] for r in _read_csv(data_dir, "customers.csv")}
    categories = {r["sku"]: r["category"] for r in _read_csv(data_dir, "products.csv")}
    price_history = {}
    for r in _read_csv(data_dir, "prices.csv"):
        price_history.setdefault(r["sku"], []).append(
            (date.fromisoformat(r["effective_from"]), int(r["unit_price"]))
        )

    by_customer = {}
    for r in _read_csv(data_dir, "orders.csv"):
        if r["status"] not in BILLABLE_STATUSES:
            continue
        ordered = _to_jst(r["ordered_at"])
        if (ordered.year, ordered.month) != (year, mon):
            continue
        cid, sku = r["customer_id"], r["sku"]
        if cid not in tiers:
            raise ValueError(f"unknown customer_id {cid!r} in order {r['order_id']}")
        if sku not in categories:
            raise ValueError(f"unknown sku {sku!r} in order {r['order_id']}")
        qty = int(r["qty"])
        unit_price = _unit_price(price_history, sku, ordered.date())
        line = {
            "order_id": r["order_id"],
            "sku": sku,
            "qty": qty,
            "unit_price": unit_price,
            "amount": qty * unit_price,
        }
        by_customer.setdefault(cid, []).append((ordered, r["order_id"], line))

    invoices = []
    for seq, cid in enumerate(sorted(by_customer), start=1):
        entries = sorted(by_customer[cid], key=lambda e: (e[0], e[1]))
        lines = [e[2] for e in entries]

        group_subtotals = {}
        for line in lines:
            cat = categories[line["sku"]]
            group_subtotals[cat] = group_subtotals.get(cat, 0) + line["amount"]

        tier = tiers[cid]
        if tier not in DISCOUNT_RATE_PERCENT:
            raise ValueError(f"unknown tier {tier!r} for customer {cid}")
        discount_pct = DISCOUNT_RATE_PERCENT[tier]

        discount = tax = 0
        for cat, group_subtotal in group_subtotals.items():
            if cat not in TAX_RATE_PERCENT:
                raise ValueError(f"unknown category {cat!r}")
            group_discount = group_subtotal * discount_pct // 100
            discount += group_discount
            tax += (group_subtotal - group_discount) * TAX_RATE_PERCENT[cat] // 100

        subtotal = sum(line["amount"] for line in lines)
        invoices.append({
            "invoice_id": f"INV-{year:04d}{mon:02d}-{seq:04d}",
            "customer_id": cid,
            "lines": lines,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": subtotal - discount + tax,
        })
    return invoices


def write_invoices_csv(invoices, out_path):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(invoices)


def main(argv):
    if len(argv) != 4:
        print("usage: python solution.py <data_dir> <YYYY-MM> <out.csv>", file=sys.stderr)
        return 2
    _, data_dir, month, out_path = argv
    try:
        invoices = make_invoices(data_dir, month)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    write_invoices_csv(invoices, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
