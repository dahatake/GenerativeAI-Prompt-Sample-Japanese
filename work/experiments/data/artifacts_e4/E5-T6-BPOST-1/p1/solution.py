"""Monthly invoice generation from CSV data (see report.md for assumptions)."""
import csv
import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR

JST = timezone(timedelta(hours=9))
BILLABLE_STATUSES = {"completed", "shipped"}
TAX_RATES = {"food": Decimal("0.08")}  # reduced rate; others use DEFAULT_TAX_RATE
DEFAULT_TAX_RATE = Decimal("0.10")
# Discount rate per customer tier. No rule was specified, so none is applied by default.
DISCOUNT_RATES = {}


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), newline="", encoding="utf-8-sig") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _floor(x):
    return int(Decimal(x).to_integral_value(rounding=ROUND_FLOOR))


def _parse_ts(s):
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(JST)


def _parse_month(month):
    try:
        return datetime.strptime(month, "%Y-%m").strftime("%Y-%m")
    except (TypeError, ValueError):
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")


def _unit_price(prices, sku, day):
    candidates = [p for p in prices.get(sku, []) if p[0] <= day]
    if not candidates:
        raise ValueError(f"no price for sku {sku} on {day}")
    return max(candidates)[1]


def make_invoices(data_dir, month, discount_rates=None):
    month = _parse_month(month)
    discount_rates = DISCOUNT_RATES if discount_rates is None else discount_rates

    customers = {r["customer_id"]: r for r in _read_csv(data_dir, "customers.csv")}
    products = {r["sku"]: r for r in _read_csv(data_dir, "products.csv")}
    prices = {}
    for r in _read_csv(data_dir, "prices.csv"):
        eff = datetime.strptime(r["effective_from"], "%Y-%m-%d").date()
        prices.setdefault(r["sku"], []).append((eff, int(r["unit_price"])))

    by_customer = {}
    for r in _read_csv(data_dir, "orders.csv"):
        if r["status"].lower() not in BILLABLE_STATUSES:
            continue
        ts = _parse_ts(r["ordered_at"])
        if ts.strftime("%Y-%m") != month:
            continue
        cid, sku = r["customer_id"], r["sku"]
        if cid not in customers:
            raise ValueError(f"unknown customer {cid} in order {r['order_id']}")
        if sku not in products:
            raise ValueError(f"unknown sku {sku} in order {r['order_id']}")
        qty = int(r["qty"])
        price = _unit_price(prices, sku, ts.date())
        by_customer.setdefault(cid, []).append((ts, r["order_id"], {
            "order_id": r["order_id"], "sku": sku, "qty": qty,
            "unit_price": price, "amount": price * qty,
        }))

    invoices = []
    ym = month.replace("-", "")
    for cid in sorted(by_customer):
        lines = [line for _, _, line in sorted(by_customer[cid], key=lambda x: (x[0], x[1]))]
        subtotal = sum(l["amount"] for l in lines)

        rate = Decimal(str(discount_rates.get(customers[cid].get("tier", ""), 0)))
        discount = _floor(subtotal * rate)

        # Group by tax rate; allocate the discount proportionally, then floor tax once per rate.
        buckets = {}
        for l in lines:
            tr = TAX_RATES.get(products[l["sku"]].get("category", ""), DEFAULT_TAX_RATE)
            buckets[tr] = buckets.get(tr, 0) + l["amount"]
        tax, remaining = 0, discount
        keys = sorted(buckets)
        for i, tr in enumerate(keys):
            if i == len(keys) - 1:
                share = remaining
            else:
                share = discount * buckets[tr] // subtotal
                remaining -= share
            tax += _floor((buckets[tr] - share) * tr)

        invoices.append({
            "invoice_id": f"INV-{ym}-{cid}",
            "customer_id": cid,
            "lines": lines,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": subtotal - discount + tax,
        })
    return invoices


FIELDS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]


def write_csv(invoices, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(invoices)


def main(argv):
    if len(argv) != 4:
        print("usage: python solution.py <data_dir> <YYYY-MM> <out.csv>", file=sys.stderr)
        return 2
    write_csv(make_invoices(argv[1], argv[2]), argv[3])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
