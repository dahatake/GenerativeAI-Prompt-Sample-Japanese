from pathlib import Path
import solution

base = Path.cwd()

actual = solution.monthly_sales(base / "sales.csv")
assert actual == {
    "2026-01": 15000,
    "2026-02": 10000,
    "2026-03": 0,
    "2026-04": 17000,
    "2026-05": 7000,
}
assert isinstance(actual, dict)
assert all(isinstance(key, str) and isinstance(value, int) for key, value in actual.items())
assert list(actual) == sorted(actual)
assert solution.monthly_sales(base / "sales.csv") == actual
print("PASS sales.csv expected totals:", actual)

boundary_csv = base / "test_sales.csv"
boundary_csv.write_text(
    "order_id,ordered_at,amount_incl_tax,status\n"
    "B-1,2026-01-31T14:59:59Z,1100,completed\n"
    "B-2,2026-01-31T15:00:00Z,1100,completed\n"
    "B-3,2026-02-10T00:00:00Z,-1100,completed\n"
    "B-4,2026-03-01T00:00:00Z,9900,cancelled\n"
    "B-5,2026-04-01T00:00:00Z,0,completed\n",
    encoding="utf-8",
)
try:
    boundary = solution.monthly_sales(boundary_csv)
    assert boundary == {
        "2026-01": 1000,
        "2026-02": 0,
        "2026-03": 0,
        "2026-04": 0,
    }, boundary
    print("PASS JST boundaries, negative, cancelled, zero, missing months:", boundary)
finally:
    boundary_csv.unlink(missing_ok=True)

empty_csv = base / "test_empty_sales.csv"
empty_csv.write_text("order_id,ordered_at,amount_incl_tax,status\n", encoding="utf-8")
try:
    assert solution.monthly_sales(empty_csv) == {}
    print("PASS empty CSV:", {})
finally:
    empty_csv.unlink(missing_ok=True)

print("PASS callable, type, repeatability, and key ordering")
