from __future__ import annotations

import csv
import re
from os import PathLike
from typing import Mapping


_EMPLOYEE_HEADERS = ("employee_id", "employee", "employeeid", "staff_id", "worker_id", "id")
_TYPE_HEADERS = ("type", "shift_type", "record_type", "status")
_START_HEADERS = ("start", "start_time", "clock_in", "in", "check_in")
_END_HEADERS = ("end", "end_time", "clock_out", "out", "check_out")


def _header_map(fieldnames: list[str] | None) -> dict[str, str]:
    if not fieldnames:
        return {}

    mapping: dict[str, str] = {}
    for field in fieldnames:
        normalized = re.sub(r"[^a-z0-9]", "", field.strip().lower())
        mapping.setdefault(normalized, field)
    return mapping


def _find_header(headers: Mapping[str, str], candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        normalized = re.sub(r"[^a-z0-9]", "", candidate.lower())
        if normalized in headers:
            return headers[normalized]
    return None


def _parse_clock(value: str) -> float:
    text = value.strip()
    if not text:
        raise ValueError("empty clock time")

    if "T" in text:
        text = text.split("T", 1)[1]
    elif re.search(r"\d{4}-\d{2}-\d{2}[ ]", text):
        text = text.split(" ", 1)[1]

    match = re.fullmatch(r"(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.\d+)?", text)
    if not match:
        raise ValueError(f"invalid clock time: {value!r}")

    hour = int(match.group(1))
    minute = int(match.group(2))
    second = int(match.group(3) or 0)
    if hour > 23 or minute > 59 or second > 59:
        raise ValueError(f"invalid clock time: {value!r}")
    return hour + minute / 60.0 + second / 3600.0


def _is_leave_type(value: str) -> bool:
    text = re.sub(r"[^a-z0-9]", "", value.strip().lower())
    return text in {
        "leave", "paidleave", "unpaidleave", "sickleave", "annualleave",
        "vacation", "holiday", "absence", "absent", "off", "break",
    }


def monthly_work_hours(path: str | PathLike[str]) -> dict[str, float]:
    """Aggregate work-shift hours for each employee in a CSV file."""
    totals: dict[str, float] = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = _header_map(reader.fieldnames)

        employee_header = _find_header(headers, _EMPLOYEE_HEADERS)
        type_header = _find_header(headers, _TYPE_HEADERS)
        start_header = _find_header(headers, _START_HEADERS)
        end_header = _find_header(headers, _END_HEADERS)

        if employee_header is None:
            raise ValueError("CSV does not contain an employee ID column")

        for row in reader:
            employee = (row.get(employee_header) or "").strip()
            if not employee:
                continue

            totals.setdefault(employee, 0.0)

            shift_type = (row.get(type_header) or "").strip() if type_header else ""
            if _is_leave_type(shift_type):
                continue

            start_text = (row.get(start_header) or "").strip() if start_header else ""
            end_text = (row.get(end_header) or "").strip() if end_header else ""
            if not start_text or not end_text:
                continue

            try:
                start = _parse_clock(start_text)
                end = _parse_clock(end_text)
            except ValueError:
                continue

            duration = end - start
            if duration < 0:
                duration += 24.0

            totals[employee] += duration

    return totals
