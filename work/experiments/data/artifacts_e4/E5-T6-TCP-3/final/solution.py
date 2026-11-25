"""Monthly invoice generation from customers/products/prices/orders CSV files."""

import csv
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
DISCOUNT_PERCENT_BY_TIER = {"gold": 5}
TAX_PERCENT_BY_CATEGORY = {"food": 8}
DEFAULT_TAX_PERCENT = 10
SUMMARY_FIELDS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]
_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _parse_ordered_at(value):
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(JST)


def _unit_price(price_history, sku, order_date):
    candidates = [p for eff, p in price_history.get(sku, []) if eff <= order_date]
    if not candidates:
        raise ValueError(f"no price for sku {sku!r} on {order_date.isoformat()}")
    # price_history is sorted by effective_from, so the last candidate is the latest.
    return candidates[-1]


def make_invoices(data_dir, month):
    if not isinstance(month, str) or not _MONTH_RE.match(month):
        raise ValueError(f"month must be 'YYYY-MM', got {month!r}")

    tiers = {r["customer_id"]: r["tier"] for r in _read_csv(data_dir, "customers.csv")}
    categories = {r["sku"]: r["category"] for r in _read_csv(data_dir, "products.csv")}
    price_history = defaultdict(list)
    for r in _read_csv(data_dir, "prices.csv"):
        price_history[r["sku"]].append(
            (date.fromisoformat(r["effective_from"]), int(r["unit_price"]))
        )
    for history in price_history.values():
        history.sort(key=lambda x: x[0])

    lines_by_customer = defaultdict(list)
    for r in _read_csv(data_dir, "orders.csv"):
        if r["status"] not in BILLABLE_STATUSES:
            continue
        ordered_at = _parse_ordered_at(r["ordered_at"])
        if ordered_at.strftime("%Y-%m") != month:
            continue
        customer_id, sku = r["customer_id"], r["sku"]
        if customer_id not in tiers:
            raise ValueError(f"unknown customer_id {customer_id!r} in order {r['order_id']}")
        if sku not in categories:
            raise ValueError(f"unknown sku {sku!r} in order {r['order_id']}")
        qty = int(r["qty"])
        unit_price = _unit_price(price_history, sku, ordered_at.date())
        lines_by_customer[customer_id].append(
            (
                ordered_at,
                {
                    "order_id": r["order_id"],
                    "sku": sku,
                    "qty": qty,
                    "unit_price": unit_price,
                    "amount": unit_price * qty,
                },
            )
        )

    yyyymm = month.replace("-", "")
    invoices = []
    for seq, customer_id in enumerate(sorted(lines_by_customer), start=1):
        entries = sorted(lines_by_customer[customer_id], key=lambda e: (e[0], e[1]["order_id"]))
        lines = [line for _, line in entries]

        amount_by_rate = defaultdict(int)
        for line in lines:
            rate = TAX_PERCENT_BY_CATEGORY.get(categories[line["sku"]], DEFAULT_TAX_PERCENT)
            amount_by_rate[rate] += line["amount"]

        discount_percent = DISCOUNT_PERCENT_BY_TIER.get(tiers[customer_id], 0)
        discount = 0
        tax = 0
        for rate, amount in amount_by_rate.items():
            bucket_discount = amount * discount_percent // 100
            discount += bucket_discount
            tax += (amount - bucket_discount) * rate // 100

        subtotal = sum(line["amount"] for line in lines)
        invoices.append(
            {
                "invoice_id": f"INV-{yyyymm}-{seq:04d}",
                "customer_id": customer_id,
                "lines": lines,
                "subtotal": subtotal,
                "discount": discount,
                "tax": tax,
                "total": subtotal - discount + tax,
            }
        )
    return invoices


def write_summary_csv(invoices, out_path):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(invoices)


def main(argv):
    if len(argv) != 3:
        print("usage: python solution.py <data_dir> <YYYY-MM> <out.csv>", file=sys.stderr)
        return 2
    data_dir, month, out_path = argv
    try:
        invoices = make_invoices(data_dir, month)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    write_summary_csv(invoices, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
