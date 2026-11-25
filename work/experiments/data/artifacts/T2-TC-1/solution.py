from datetime import datetime


def _email_key(record):
    email = record.get("email")
    if email is None:
        return None
    key = email.strip().lower()
    return key or None


def dedupe(records):
    """Remove duplicate member records.

    Records sharing a normalized email (stripped, lowercased) are duplicates;
    the one with the latest ``updated_at`` is kept (earlier input wins ties).
    Records with empty/null email are never deduplicated. Output follows the
    position where each group first appears; input objects are not modified.
    """
    slots = []
    group_index = {}
    for record in records:
        key = _email_key(record)
        if key is None:
            slots.append(record)
            continue
        if key not in group_index:
            group_index[key] = len(slots)
            slots.append(record)
            continue
        i = group_index[key]
        current = slots[i]
        if datetime.fromisoformat(record["updated_at"]) > datetime.fromisoformat(
            current["updated_at"]
        ):
            slots[i] = record
    return slots
