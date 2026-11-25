from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


def _email_key(record: Dict[str, Any]) -> Optional[str]:
    email = record.get("email")
    if email is None:
        return None
    key = str(email).strip().lower()
    return key or None


def _updated_at(record: Dict[str, Any]) -> datetime:
    return datetime.fromisoformat(record["updated_at"])


def dedupe(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate employee records.

    Records are duplicates when their emails match after stripping surrounding
    whitespace and lowercasing. From each group, the record with the latest
    ``updated_at`` is kept (ties keep the earlier record in the input).
    Records with an empty or missing email are never treated as duplicates.
    Output order follows each group's first appearance in the input; returned
    dicts are shallow copies and the input is not modified.
    """
    slots: List[Dict[str, Any]] = []
    slot_by_email: Dict[str, int] = {}
    latest_by_email: Dict[str, datetime] = {}

    for record in records:
        key = _email_key(record)
        if key is None:
            slots.append(record)
            continue

        ts = _updated_at(record)
        if key not in slot_by_email:
            slot_by_email[key] = len(slots)
            latest_by_email[key] = ts
            slots.append(record)
        elif ts > latest_by_email[key]:
            slots[slot_by_email[key]] = record
            latest_by_email[key] = ts

    return [dict(record) for record in slots]
