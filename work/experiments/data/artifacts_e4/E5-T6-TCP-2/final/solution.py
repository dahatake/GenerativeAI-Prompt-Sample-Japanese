import csv
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
# (numerator, denominator) for integer-only arithmetic
TAX_RATES = {"food": (8, 100)}
DEFAULT_TAX_RATE = (10, 100)
DISCOUNT_RATES = {"gold": (5, 100)}
CSV_FIELDS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _to_jst(ordered_at):
    text = ordered_at.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"ordered_at has no timezone: {ordered_at!r}")
    return dt.astimezone(JST)


def _parse_month(month):
    if not isinstance(month, str) or not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")
    if not 1 <= int(month[5:]) <= 12:
        raise ValueError(f"invalid month: {month!r}")
    return month


def make_invoices(data_dir, month):
    month = _parse_month(month)

    tiers = {r["customer_id"]: r["tier"] for r in _read_csv(data_dir, "customers.csv")}
    categories = {r["sku"]: r["category"] for r in _read_csv(data_dir, "products.csv")}
    prices = defaultdict(list)
    for r in _read_csv(data_dir, "prices.csv"):
        prices[r["sku"]].append((r["effective_from"], int(r["unit_price"])))

    lines_by_customer = defaultdict(list)
    for r in _read_csv(data_dir, "orders.csv"):
        if r["status"] not in BILLABLE_STATUSES:
            continue
        ordered_at = _to_jst(r["ordered_at"])
        if ordered_at.strftime("%Y-%m") != month:
            continue
        customer_id, sku = r["customer_id"], r["sku"]
        if customer_id not in tiers:
            raise ValueError(f"unknown customer_id {customer_id!r} in order {r['order_id']}")
        if sku not in categories:
            raise ValueError(f"unknown sku {sku!r} in order {r['order_id']}")
        order_date = ordered_at.date().isoformat()
        candidates = [p for p in prices[sku] if p[0] <= order_date]
        if not candidates:
            raise ValueError(f"no price for sku {sku!r} on {order_date} (order {r['order_id']})")
        unit_price = max(candidates)[1]
        qty = int(r["qty"])
        lines_by_customer[customer_id].append(
            (
                ordered_at,
                r["order_id"],
                categories[sku],
                {
                    "order_id": r["order_id"],
                    "sku": sku,
                    "qty": qty,
                    "unit_price": unit_price,
                    "amount": qty * unit_price,
                },
            )
        )

    invoices = []
    yyyymm = month.replace("-", "")
    for seq, customer_id in enumerate(sorted(lines_by_customer), start=1):
        entries = sorted(lines_by_customer[customer_id], key=lambda e: (e[0], e[1]))
        category_subtotals = defaultdict(int)
        for _, _, category, line in entries:
            category_subtotals[TAX_RATES.get(category, DEFAULT_TAX_RATE)] += line["amount"]

        disc_num, disc_den = DISCOUNT_RATES.get(tiers[customer_id], (0, 1))
        subtotal = discount = tax = 0
        for (tax_num, tax_den), group_subtotal in category_subtotals.items():
            group_discount = group_subtotal * disc_num // disc_den
            subtotal += group_subtotal
            discount += group_discount
            tax += (group_subtotal - group_discount) * tax_num // tax_den

        invoices.append(
            {
                "invoice_id": f"INV-{yyyymm}-{seq:04d}",
                "customer_id": customer_id,
                "lines": [e[3] for e in entries],
                "subtotal": subtotal,
                "discount": discount,
                "tax": tax,
                "total": subtotal - discount + tax,
            }
        )
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
    write_invoices_csv(make_invoices(data_dir, month), out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
