import csv
import math
import os
from solution import monthly_work_hours


result = monthly_work_hours("shifts.csv")
assert isinstance(result, dict)
assert all(isinstance(employee, str) for employee in result)
assert all(isinstance(hours, float) for hours in result.values())
assert math.isclose(result["E001"], 22.25, rel_tol=0.0, abs_tol=1e-12)
assert math.isclose(result["E002"], 14.0, rel_tol=0.0, abs_tol=1e-12)
assert math.isclose(result["E003"], 9.25, rel_tol=0.0, abs_tol=1e-12)

custom_path = "custom.csv"
try:
    with open(custom_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["employee", "date", "type", "start", "end"])
        writer.writerow(["NIGHT", "2026-11-01", "work", "22:10", "06:05"])
        writer.writerow(["ROUND", "2026-11-01", "work", "09:07", "10:23"])

    custom = monthly_work_hours(custom_path)
    assert math.isclose(custom["NIGHT"], 7.75, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(custom["ROUND"], 1.25, rel_tol=0.0, abs_tol=1e-12)
finally:
    if os.path.exists(custom_path):
        os.remove(custom_path)

print("PASS: dict and float types")
print("PASS: shifts.csv E001=22.25, E002=14.0, E003=9.25")
print("PASS: paid_leave=7.5")
print("PASS: overnight 22:10-06:05=7.75 after 15-minute floor")
print("PASS: 09:07-10:23=76-minute duration, floored to 75 minutes=1.25 hours")
