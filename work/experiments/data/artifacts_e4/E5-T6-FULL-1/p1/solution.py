"""Monthly invoice generation from CSV data (customers, products, prices, orders)."""
import csv
import os
import sys
from datetime import date, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
REDUCED_RATE_CATEGORIES = {"food"}
# Rates and discount are kept as integer percentages so rounding stays exact.
STANDARD_RATE = 10
REDUCED_RATE = 8
GOLD_DISCOUNT = 5


def _read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _parse_utc(text):
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_month(month):
    try:
        year, mon = (int(p) for p in month.split("-"))
        date(year, mon, 1)
    except (ValueError, AttributeError):
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")
    return year, mon


def make_invoices(data_dir, month):
    year, mon = _parse_month(month)

    customers = {r["customer_id"]: r for r in _read_csv(os.path.join(data_dir, "customers.csv"))}
    products = {r["sku"]: r for r in _read_csv(os.path.join(data_dir, "products.csv"))}
    prices = {}
    for r in _read_csv(os.path.join(data_dir, "prices.csv")):
        prices.setdefault(r["sku"], []).append(
            (date.fromisoformat(r["effective_from"]), int(r["unit_price"]))
        )
    for entries in prices.values():
        entries.sort()

    def price_on(sku, day):
        valid = [p for eff, p in prices.get(sku, []) if eff <= day]
        if not valid:
            raise ValueError(f"no effective price for sku {sku} on {day}")
        return valid[-1]

    by_customer = {}
    for r in _read_csv(os.path.join(data_dir, "orders.csv")):
        if r["status"].lower() not in BILLABLE_STATUSES:
            continue
        ordered_utc = _parse_utc(r["ordered_at"])
        ordered_jst = ordered_utc.astimezone(JST)
        if (ordered_jst.year, ordered_jst.month) != (year, mon):
            continue
        sku = r["sku"]
        if sku not in products:
            raise ValueError(f"unknown sku {sku} in order {r['order_id']}")
        qty = int(r["qty"])
        unit_price = price_on(sku, ordered_jst.date())
        by_customer.setdefault(r["customer_id"], []).append(
            (ordered_utc, r["order_id"], {
                "order_id": r["order_id"],
                "sku": sku,
                "qty": qty,
                "unit_price": unit_price,
                "amount": unit_price * qty,
            })
        )

    invoices = []
    for seq, customer_id in enumerate(sorted(by_customer), start=1):
        entries = sorted(by_customer[customer_id], key=lambda e: (e[0], e[1]))
        lines = [e[2] for e in entries]

        subtotal_by_rate = {}
        for line in lines:
            category = products[line["sku"]]["category"].lower()
            rate = REDUCED_RATE if category in REDUCED_RATE_CATEGORIES else STANDARD_RATE
            subtotal_by_rate[rate] = subtotal_by_rate.get(rate, 0) + line["amount"]

        is_gold = customers.get(customer_id, {}).get("tier", "").lower() == "gold"
        discount = tax = 0
        for rate, sub in subtotal_by_rate.items():
            disc = sub * GOLD_DISCOUNT // 100 if is_gold else 0
            discount += disc
            tax += (sub - disc) * rate // 100

        subtotal = sum(subtotal_by_rate.values())
        invoices.append({
            "invoice_id": f"INV-{year:04d}{mon:02d}-{seq:04d}",
            "customer_id": customer_id,
            "lines": lines,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": subtotal - discount + tax,
        })
    return invoices


def write_invoices_csv(invoices, out_path):
    fields = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
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
