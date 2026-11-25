from pathlib import Path

from solution import validate_invoice_id


SAMPLES = [
    "INV-202601-0001",
    "INV-202601-0002",
    "INV-202512-0347",
    "INV-202603-1200",
]


def check(condition, name):
    if not condition:
        raise AssertionError(name)
    print(f"PASS {name}")


check(validate_invoice_id("INV-202601-0001") is True, "DOD-2 valid sample 1")
check(validate_invoice_id("INV-202512-0347") is True, "DOD-3 valid sample 2")

text = Path("samples.txt").read_text(encoding="utf-8")
file_samples = [line.strip() for line in text.splitlines() if line.strip().startswith("INV-")]
check(file_samples == SAMPLES, "DOD-4 samples.txt sample extraction")
check(all(validate_invoice_id(value) is True for value in file_samples), "DOD-4 all samples valid")

invalid_values = [
    "",
    None,
    2026010001,
    " INV-202601-0001",
    "INV-202601-0001 ",
    "INV-20261-0001",
    "INV-2026011-0001",
    "INV202601-0001",
    "inv-202601-0001",
    "INV-202613-0001",
    "INV-202600-0001",
    "INV-201912-0001",
    "INV-210001-0001",
    "INV-２０2601-0001",
    "INV-202601-0000",
]
for index, value in enumerate(invalid_values, start=1):
    check(validate_invoice_id(value) is False, f"DOD-5 invalid case {index}: {value!r}")

check(Path("contract.md").is_file(), "DOD-1 contract.md exists")
contract_text = Path("contract.md").read_text(encoding="utf-8")
check("承認済み" in contract_text, "DOD-1 approved contract marker")
check("2020" in contract_text and "2099" in contract_text, "DOD-1 resolved year range")
check("0001" in contract_text and "9999" in contract_text, "DOD-1 resolved serial range")

print("RESULT 25 PASS, 0 FAIL")
