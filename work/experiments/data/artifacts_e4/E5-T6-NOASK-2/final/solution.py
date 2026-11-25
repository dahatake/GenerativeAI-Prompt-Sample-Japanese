"""Monthly invoice generation from the CSV files in a data directory.

Business rules (see contract.md):
- Month assignment and price lookup use the order date in JST (UTC+9).
- Billable statuses: completed, shipped. returned / cancelled are excluded.
- Discount: gold tier 10%, standard 0%.
- Tax: food 8% (reduced rate), general 10%.
- Per tax-rate group: discount = floor(group_subtotal * discount_rate),
  tax = floor((group_subtotal - discount) * tax_rate). Invoice values are sums.
"""

import csv
import os
import re
import sys
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
EXCLUDED_STATUSES = {"returned", "cancelled"}
DISCOUNT_PERCENT = {"gold": 10, "standard": 0}
TAX_PERCENT = {"food": 8, "general": 10}
MONTH_RE = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")
CSV_FIELDS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _parse_ordered_at(value):
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"ordered_at has no timezone: {value!r}")
    return dt


def _unit_price(price_history, sku, order_date):
    candidates = [p for p in price_history.get(sku, []) if p[0] <= order_date]
    if not candidates:
        raise ValueError(f"no price for sku {sku} on {order_date}")
    return max(candidates, key=lambda p: p[0])[1]


def make_invoices(data_dir, month):
    if not isinstance(month, str) or not MONTH_RE.match(month):
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")

    customers = {r["customer_id"]: r for r in _read_csv(data_dir, "customers.csv")}
    products = {r["sku"]: r for r in _read_csv(data_dir, "products.csv")}
    price_history = {}
    for r in _read_csv(data_dir, "prices.csv"):
        effective = datetime.strptime(r["effective_from"], "%Y-%m-%d").date()
        price_history.setdefault(r["sku"], []).append((effective, int(r["unit_price"])))

    lines_by_customer = {}
    for r in _read_csv(data_dir, "orders.csv"):
        status = r["status"].strip()
        if status not in BILLABLE_STATUSES | EXCLUDED_STATUSES:
            raise ValueError(f"unknown status {status!r} in order {r['order_id']}")
        customer_id, sku = r["customer_id"], r["sku"]
        if customer_id not in customers:
            raise ValueError(f"unknown customer {customer_id} in order {r['order_id']}")
        if sku not in products:
            raise ValueError(f"unknown sku {sku} in order {r['order_id']}")

        ordered_at = _parse_ordered_at(r["ordered_at"])
        local_date = ordered_at.astimezone(JST).date()
        if local_date.strftime("%Y-%m") != month or status not in BILLABLE_STATUSES:
            continue

        qty = int(r["qty"])
        unit_price = _unit_price(price_history, sku, local_date)
        line = {
            "order_id": r["order_id"],
            "sku": sku,
            "qty": qty,
            "unit_price": unit_price,
            "amount": unit_price * qty,
        }
        lines_by_customer.setdefault(customer_id, []).append((ordered_at, line))

    yyyymm = month.replace("-", "")
    invoices = []
    for customer_id in sorted(lines_by_customer):
        entries = sorted(lines_by_customer[customer_id], key=lambda e: (e[0], e[1]["order_id"]))
        lines = [line for _, line in entries]

        tier = customers[customer_id]["tier"].strip()
        if tier not in DISCOUNT_PERCENT:
            raise ValueError(f"unknown tier {tier!r} for customer {customer_id}")
        discount_pct = DISCOUNT_PERCENT[tier]

        group_subtotals = {}
        for line in lines:
            category = products[line["sku"]]["category"].strip()
            if category not in TAX_PERCENT:
                raise ValueError(f"unknown category {category!r} for sku {line['sku']}")
            rate = TAX_PERCENT[category]
            group_subtotals[rate] = group_subtotals.get(rate, 0) + line["amount"]

        subtotal = discount = tax = 0
        for rate, group_subtotal in group_subtotals.items():
            group_discount = group_subtotal * discount_pct // 100
            subtotal += group_subtotal
            discount += group_discount
            tax += (group_subtotal - group_discount) * rate // 100

        invoices.append({
            "invoice_id": f"INV-{yyyymm}-{customer_id}",
            "customer_id": customer_id,
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
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    write_invoices_csv(invoices, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
