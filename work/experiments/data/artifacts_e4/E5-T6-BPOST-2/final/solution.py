"""月次請求書の作成。

使い方: python solution.py <data_dir> <YYYY-MM> <out.csv>
"""
import csv
import os
import re
import sys
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))

BILLABLE_STATUSES = {"completed", "shipped"}

# 消費税率（%）。food は軽減税率 8%、それ以外は標準税率 10%。
TAX_RATES = {"food": 8}
DEFAULT_TAX_RATE = 10

# 顧客ランク別の値引き率（%）。
DISCOUNT_RATES = {"gold": 5}

CSV_FIELDS = ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]


def _read_csv(data_dir, name):
    with open(os.path.join(data_dir, name), encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _parse_month(month):
    m = re.fullmatch(r"(\d{4})-(\d{2})", str(month))
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise ValueError(f"month must be 'YYYY-MM': {month!r}")
    return int(m.group(1)), int(m.group(2))


def _to_jst(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(JST)


def _unit_price(price_table, sku, order_date):
    candidates = [(d, p) for d, p in price_table.get(sku, []) if d <= order_date]
    if not candidates:
        raise ValueError(f"no price for sku {sku} on {order_date.isoformat()}")
    return max(candidates)[1]


def make_invoices(data_dir, month, discount_rates=None):
    year, mon = _parse_month(month)
    discount_rates = DISCOUNT_RATES if discount_rates is None else discount_rates

    customers = {r["customer_id"]: r for r in _read_csv(data_dir, "customers.csv")}
    categories = {r["sku"]: r["category"] for r in _read_csv(data_dir, "products.csv")}
    price_table = {}
    for r in _read_csv(data_dir, "prices.csv"):
        eff = datetime.strptime(r["effective_from"], "%Y-%m-%d").date()
        price_table.setdefault(r["sku"], []).append((eff, int(r["unit_price"])))

    per_customer = {}
    for r in _read_csv(data_dir, "orders.csv"):
        if r["status"].lower() not in BILLABLE_STATUSES:
            continue
        ordered = _to_jst(r["ordered_at"])
        if (ordered.year, ordered.month) != (year, mon):
            continue
        if r["customer_id"] not in customers:
            raise ValueError(f"unknown customer {r['customer_id']} in order {r['order_id']}")
        if r["sku"] not in categories:
            raise ValueError(f"unknown sku {r['sku']} in order {r['order_id']}")
        qty = int(r["qty"])
        price = _unit_price(price_table, r["sku"], ordered.date())
        per_customer.setdefault(r["customer_id"], []).append((ordered, r["order_id"], r["sku"], qty, price))

    invoices = []
    for seq, cid in enumerate(sorted(per_customer), start=1):
        rows = sorted(per_customer[cid], key=lambda x: (x[0], x[1]))
        lines = []
        by_rate = {}
        for _, order_id, sku, qty, price in rows:
            amount = qty * price
            lines.append({"order_id": order_id, "sku": sku, "qty": qty, "unit_price": price, "amount": amount})
            rate = TAX_RATES.get(categories[sku], DEFAULT_TAX_RATE)
            by_rate[rate] = by_rate.get(rate, 0) + amount

        subtotal = sum(by_rate.values())
        disc_rate = discount_rates.get(customers[cid].get("tier", ""), 0)
        # 値引き・税額とも税率区分ごとに計算し、1円未満を切り捨てる。
        rate_discounts = {r: amt * disc_rate // 100 for r, amt in by_rate.items()}
        discount = sum(rate_discounts.values())
        tax = sum((amt - rate_discounts[r]) * r // 100 for r, amt in by_rate.items())

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


def write_csv(invoices, out_path):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
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
