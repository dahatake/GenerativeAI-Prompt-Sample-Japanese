"""Generate the T6 (monthly billing) task data deterministically. Run once; output is written to tasks/T6_billing/data."""
import csv, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "T6_billing", "data")
os.makedirs(D, exist_ok=True)


def w(name, header, rows):
    with open(os.path.join(D, name), "w", newline="", encoding="utf-8") as f:
        c = csv.writer(f)
        c.writerow(header)
        c.writerows(rows)


w("customers.csv", ["customer_id", "name", "tier"], [
    ["C004", "東和商事", "standard"], ["C001", "青葉食品", "gold"], ["C005", "南星工業", "standard"],
    ["C003", "北斗電機", "gold"], ["C002", "西川物産", "standard"]])
w("products.csv", ["sku", "name", "category"], [
    ["A100", "USBケーブル", "general"], ["A200", "ワイヤレスマウス", "general"],
    ["F100", "コーヒー豆 500g", "food"], ["F200", "クッキー詰め合わせ", "food"]])
w("prices.csv", ["sku", "effective_from", "unit_price"], [
    ["A100", "2026-01-01", 1200], ["A100", "2026-10-16", 1300], ["A200", "2026-01-01", 2980],
    ["F100", "2026-01-01", 1580], ["F100", "2026-10-10", 1680], ["F200", "2026-01-01", 540]])
orders = [
    ["O1001", "C001", "2026-09-28T02:10:00Z", "A100", 2, "completed"],
    ["O1002", "C003", "2026-09-30T15:30:00Z", "F100", 3, "completed"],   # JST 10/01 00:30
    ["O1003", "C001", "2026-10-02T01:00:00Z", "F200", 10, "completed"],
    ["O1004", "C002", "2026-10-03T05:20:00Z", "A200", 1, "shipped"],
    ["O1005", "C004", "2026-10-04T08:45:00Z", "A100", 5, "completed"],
    ["O1006", "C005", "2026-10-05T03:00:00Z", "A200", 2, "cancelled"],
    ["O1007", "C003", "2026-10-07T23:30:00Z", "F100", 2, "completed"],   # JST 10/08
    ["O1008", "C001", "2026-10-09T15:10:00Z", "F100", 4, "shipped"],     # JST 10/10 00:10 (new F100 price)
    ["O1009", "C002", "2026-10-11T04:00:00Z", "F200", 6, "completed"],
    ["O1010", "C004", "2026-10-12T06:30:00Z", "A200", 1, "returned"],
    ["O1011", "C003", "2026-10-14T02:00:00Z", "A100", 3, "completed"],
    ["O1012", "C001", "2026-10-15T15:20:00Z", "A100", 7, "completed"],   # JST 10/16 00:20 (new A100 price)
    ["O1013", "C002", "2026-10-17T07:00:00Z", "A100", 1, "cancelled"],
    ["O1014", "C004", "2026-10-18T09:15:00Z", "F100", 1, "completed"],
    ["O1015", "C003", "2026-10-20T01:40:00Z", "F200", 12, "shipped"],
    ["O1016", "C001", "2026-10-22T05:05:00Z", "A200", 2, "completed"],
    ["O1017", "C005", "2026-10-23T02:00:00Z", "F200", 3, "returned"],
    ["O1018", "C002", "2026-10-25T10:00:00Z", "F100", 2, "completed"],
    ["O1019", "C004", "2026-10-27T00:30:00Z", "A100", 2, "completed"],
    ["O1020", "C003", "2026-10-29T03:20:00Z", "A200", 1, "completed"],
    ["O1021", "C001", "2026-10-31T16:00:00Z", "F200", 5, "completed"],   # JST 11/01 01:00
    ["O1022", "C002", "2026-10-31T14:50:00Z", "A200", 1, "completed"],   # JST 10/31 23:50
    ["O1023", "C004", "2026-11-02T04:00:00Z", "F100", 2, "completed"],
    ["O1024", "C003", "2026-11-03T06:00:00Z", "A100", 1, "shipped"],
]
random.Random(6).shuffle(orders)
w("orders.csv", ["order_id", "customer_id", "ordered_at", "sku", "qty", "status"], orders)
print("written", D)
