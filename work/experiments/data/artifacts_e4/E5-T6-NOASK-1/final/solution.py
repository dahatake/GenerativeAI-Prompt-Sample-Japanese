"""Monthly invoice generation from customers/products/prices/orders CSV files.

Rules (see contract.md):
- Month and price-effective date are judged in JST (UTC+9, no DST).
- Billable statuses: completed, shipped.
- gold tier: discount = floor(subtotal * 5%), standard: 0.
- Tax: food 8%, general 10%; discount is apportioned to the 8% bucket by
  floor(discount * food_subtotal / subtotal), remainder to the 10% bucket;
  tax is floored per invoice per rate.
"""

import csv
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
KNOWN_STATUSES = {"completed", "shipped", "returned", "cancelled"}
TAX_RATE_PERCENT = {"food": 8, "general": 10}
DISCOUNT_PERCENT = {"gold": 5, "standard": 0}
CSV_COLUMNS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _parse_month(month):
    m = re.fullmatch(r"(\d{4})-(\d{2})", month or "")
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")
    return int(m.group(1)), int(m.group(2))


def _parse_ordered_at(value, order_id):
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        raise ValueError(f"invalid ordered_at for {order_id}: {value!r}") from None
    if dt.tzinfo is None:
        raise ValueError(f"ordered_at without timezone for {order_id}: {value!r}")
    return dt.astimezone(JST)


def _parse_int(value, what):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid integer for {what}: {value!r}") from None


def _load_prices(data_dir):
    prices = {}
    for row in _read_csv(data_dir, "prices.csv"):
        eff = date.fromisoformat(row["effective_from"].strip())
        price = _parse_int(row["unit_price"], f"unit_price of {row['sku']}")
        prices.setdefault(row["sku"], []).append((eff, price))
    for history in prices.values():
        history.sort()
    return prices


def _price_on(prices, sku, day):
    found = None
    for eff, price in prices.get(sku, []):
        if eff <= day:
            found = price
        else:
            break
    if found is None:
        raise ValueError(f"no effective price for {sku} on {day.isoformat()}")
    return found


def _calc_amounts(tier, subtotal_by_rate):
    subtotal = sum(subtotal_by_rate.values())
    discount = subtotal * DISCOUNT_PERCENT[tier] // 100
    food = subtotal_by_rate.get(8, 0)
    discount_food = discount * food // subtotal if subtotal else 0
    discount_by_rate = {8: discount_food, 10: discount - discount_food}
    tax = 0
    for rate, base in subtotal_by_rate.items():
        tax += (base - discount_by_rate[rate]) * rate // 100
    return subtotal, discount, tax, subtotal - discount + tax


def make_invoices(data_dir, month):
    year, mon = _parse_month(month)

    customers = {}
    for row in _read_csv(data_dir, "customers.csv"):
        tier = row["tier"].strip()
        if tier not in DISCOUNT_PERCENT:
            raise ValueError(f"unknown tier for {row['customer_id']}: {tier!r}")
        customers[row["customer_id"]] = tier

    categories = {}
    for row in _read_csv(data_dir, "products.csv"):
        category = row["category"].strip()
        if category not in TAX_RATE_PERCENT:
            raise ValueError(f"unknown category for {row['sku']}: {category!r}")
        categories[row["sku"]] = category

    prices = _load_prices(data_dir)

    lines_by_customer = {}
    for row in _read_csv(data_dir, "orders.csv"):
        order_id = row["order_id"]
        status = row["status"].strip()
        if status not in KNOWN_STATUSES:
            raise ValueError(f"unknown status for {order_id}: {status!r}")
        if row["customer_id"] not in customers:
            raise ValueError(f"unknown customer_id in {order_id}: {row['customer_id']!r}")
        if row["sku"] not in categories:
            raise ValueError(f"unknown sku in {order_id}: {row['sku']!r}")
        ordered_at = _parse_ordered_at(row["ordered_at"], order_id)
        if status not in BILLABLE_STATUSES:
            continue
        if (ordered_at.year, ordered_at.month) != (year, mon):
            continue
        qty = _parse_int(row["qty"], f"qty of {order_id}")
        unit_price = _price_on(prices, row["sku"], ordered_at.date())
        lines_by_customer.setdefault(row["customer_id"], []).append(
            (ordered_at, order_id, {
                "order_id": order_id,
                "sku": row["sku"],
                "qty": qty,
                "unit_price": unit_price,
                "amount": unit_price * qty,
            })
        )

    invoices = []
    for customer_id in sorted(lines_by_customer):
        entries = sorted(lines_by_customer[customer_id], key=lambda e: (e[0], e[1]))
        lines = [e[2] for e in entries]
        subtotal_by_rate = {}
        for line in lines:
            rate = TAX_RATE_PERCENT[categories[line["sku"]]]
            subtotal_by_rate[rate] = subtotal_by_rate.get(rate, 0) + line["amount"]
        subtotal, discount, tax, total = _calc_amounts(customers[customer_id], subtotal_by_rate)
        invoices.append({
            "invoice_id": f"INV-{year:04d}{mon:02d}-{customer_id}",
            "customer_id": customer_id,
            "lines": lines,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": total,
        })
    return invoices


def write_invoices_csv(invoices, out_path):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore", lineterminator="\n")
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
