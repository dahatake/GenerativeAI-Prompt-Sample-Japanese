"""Monthly invoice generation from CSV data (see contract.md for the agreed rules)."""

import csv
import os
import re
import sys
from datetime import datetime, timedelta, timezone

# JST has no DST, so a fixed offset avoids depending on the tzdata package on Windows.
JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
TAX_RATE_PERCENT = {"general": 10, "food": 8}
DISCOUNT_RATE_PERCENT = {"gold": 5, "standard": 0}
MONTH_RE = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")
SUMMARY_FIELDS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _to_jst(ordered_at):
    dt = datetime.fromisoformat(ordered_at.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"ordered_at has no timezone: {ordered_at!r}")
    return dt.astimezone(JST)


def _unit_price(price_table, sku, order_date):
    candidates = [(eff, price) for eff, price in price_table.get(sku, []) if eff <= order_date]
    if not candidates:
        raise ValueError(f"no price for sku {sku!r} on {order_date}")
    return max(candidates)[1]


def make_invoices(data_dir, month):
    if not isinstance(month, str) or not MONTH_RE.match(month):
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")

    customers = {r["customer_id"]: r for r in _read_csv(data_dir, "customers.csv")}
    categories = {r["sku"]: r["category"] for r in _read_csv(data_dir, "products.csv")}
    price_table = {}
    for r in _read_csv(data_dir, "prices.csv"):
        eff = datetime.strptime(r["effective_from"], "%Y-%m-%d").date()
        price_table.setdefault(r["sku"], []).append((eff, int(r["unit_price"])))

    lines_by_customer = {}
    for r in _read_csv(data_dir, "orders.csv"):
        if r["status"] not in BILLABLE_STATUSES:
            continue
        ordered = _to_jst(r["ordered_at"])
        if ordered.strftime("%Y-%m") != month:
            continue
        customer_id, sku = r["customer_id"], r["sku"]
        if customer_id not in customers:
            raise ValueError(f"unknown customer_id {customer_id!r} in order {r['order_id']}")
        if sku not in categories:
            raise ValueError(f"unknown sku {sku!r} in order {r['order_id']}")
        qty = int(r["qty"])
        unit_price = _unit_price(price_table, sku, ordered.date())
        line = {
            "order_id": r["order_id"],
            "sku": sku,
            "qty": qty,
            "unit_price": unit_price,
            "amount": qty * unit_price,
        }
        lines_by_customer.setdefault(customer_id, []).append((ordered, line))

    yyyymm = month.replace("-", "")
    invoices = []
    for customer_id in sorted(lines_by_customer):
        entries = sorted(lines_by_customer[customer_id], key=lambda e: (e[0], e[1]["order_id"]))
        lines = [line for _, line in entries]

        by_rate = {}
        for line in lines:
            rate = TAX_RATE_PERCENT[categories[line["sku"]]]
            by_rate[rate] = by_rate.get(rate, 0) + line["amount"]
        subtotal = sum(by_rate.values())

        tier = customers[customer_id]["tier"]
        if tier not in DISCOUNT_RATE_PERCENT:
            raise ValueError(f"unknown tier {tier!r} for customer {customer_id}")
        discount = subtotal * DISCOUNT_RATE_PERCENT[tier] // 100

        # Allocate the discount proportionally per tax rate; the remainder goes to the highest rate.
        allocated = {}
        rates = sorted(by_rate)
        for rate in rates[:-1]:
            allocated[rate] = discount * by_rate[rate] // subtotal if subtotal else 0
        allocated[rates[-1]] = discount - sum(allocated.values())

        tax = sum((by_rate[rate] - allocated[rate]) * rate // 100 for rate in rates)
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


def write_summary_csv(invoices, out_path):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(invoices)


def main(argv):
    if len(argv) != 4:
        print("usage: python solution.py <data_dir> <YYYY-MM> <out.csv>", file=sys.stderr)
        return 2
    _, data_dir, month, out_path = argv
    try:
        invoices = make_invoices(data_dir, month)
    except (ValueError, OSError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    write_summary_csv(invoices, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
