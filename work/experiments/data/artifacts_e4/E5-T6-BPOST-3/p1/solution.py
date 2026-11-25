"""Monthly invoice generation from CSV data (customers/products/prices/orders)."""
import csv
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_DOWN, Decimal

# Business rules (assumptions; see report.md)
JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
TAX_RATES = {"food": Decimal("0.08")}  # reduced rate for food
DEFAULT_TAX_RATE = Decimal("0.10")
DISCOUNT_RATES = {"gold": Decimal("0.10")}  # other tiers: no discount

CSV_COLUMNS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _floor(value):
    return int(value.quantize(Decimal("1"), rounding=ROUND_DOWN))


def _to_jst(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(JST)


def _parse_month(month):
    if not isinstance(month, str) or not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")
    year, mon = map(int, month.split("-"))
    if not 1 <= mon <= 12:
        raise ValueError(f"invalid month: {month!r}")
    return year, mon


def _load_prices(data_dir):
    prices = defaultdict(list)
    for row in _read_csv(data_dir, "prices.csv"):
        prices[row["sku"]].append((date.fromisoformat(row["effective_from"]), int(row["unit_price"])))
    for history in prices.values():
        history.sort()
    return prices


def _unit_price(prices, sku, on):
    price = None
    for effective_from, unit_price in prices.get(sku, []):
        if effective_from <= on:
            price = unit_price
        else:
            break
    if price is None:
        raise ValueError(f"no price for sku {sku} on {on}")
    return price


def make_invoices(data_dir, month):
    year, mon = _parse_month(month)
    customers = {r["customer_id"]: r for r in _read_csv(data_dir, "customers.csv")}
    categories = {r["sku"]: r["category"] for r in _read_csv(data_dir, "products.csv")}
    prices = _load_prices(data_dir)

    by_customer = defaultdict(list)
    for row in _read_csv(data_dir, "orders.csv"):
        if row["status"].lower() not in BILLABLE_STATUSES:
            continue
        ordered_at = _to_jst(row["ordered_at"])
        if (ordered_at.year, ordered_at.month) != (year, mon):
            continue
        if row["customer_id"] not in customers:
            raise ValueError(f"unknown customer {row['customer_id']} in order {row['order_id']}")
        if row["sku"] not in categories:
            raise ValueError(f"unknown sku {row['sku']} in order {row['order_id']}")
        by_customer[row["customer_id"]].append((ordered_at, row))

    invoices = []
    for customer_id in sorted(by_customer):
        discount_rate = DISCOUNT_RATES.get(customers[customer_id].get("tier", "").lower(), Decimal("0"))
        lines = []
        rate_subtotals = defaultdict(int)
        for ordered_at, row in sorted(by_customer[customer_id], key=lambda x: (x[0], x[1]["order_id"])):
            qty = int(row["qty"])
            unit_price = _unit_price(prices, row["sku"], ordered_at.date())
            amount = unit_price * qty
            lines.append({
                "order_id": row["order_id"],
                "sku": row["sku"],
                "qty": qty,
                "unit_price": unit_price,
                "amount": amount,
            })
            rate_subtotals[TAX_RATES.get(categories[row["sku"]].lower(), DEFAULT_TAX_RATE)] += amount

        subtotal = sum(rate_subtotals.values())
        discount = 0
        tax = 0
        # Discount and tax are computed per tax rate (invoice-system style), floored to yen.
        for rate, base in sorted(rate_subtotals.items()):
            rate_discount = _floor(base * discount_rate)
            discount += rate_discount
            tax += _floor((base - rate_discount) * rate)

        invoices.append({
            "invoice_id": f"INV-{year:04d}{mon:02d}-{customer_id}",
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
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(invoices)


def main(argv):
    if len(argv) != 4:
        print("usage: python solution.py <data_dir> <YYYY-MM> <out.csv>", file=sys.stderr)
        return 2
    write_invoices_csv(make_invoices(argv[1], argv[2]), argv[3])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
