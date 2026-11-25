from datetime import datetime, timezone

_OLDEST = datetime.min.replace(tzinfo=timezone.utc)


def _normalize_email(email):
    if not isinstance(email, str):
        return None
    normalized = email.strip().lower()
    return normalized or None


def _parse_updated_at(value):
    if not isinstance(value, str):
        return _OLDEST
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return _OLDEST
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def dedupe(records):
    """Remove duplicate member records.

    Records are considered duplicates when their email addresses match after
    trimming whitespace and lowercasing. Among duplicates, the record with the
    latest ``updated_at`` is kept (ties keep the earlier record). Records
    without a usable email are never merged. The result preserves the position
    of each group's first appearance in the input.
    """
    result = []
    index_by_email = {}

    for record in records:
        key = _normalize_email(record.get("email"))
        if key is None:
            result.append(record)
            continue
        if key not in index_by_email:
            index_by_email[key] = len(result)
            result.append(record)
            continue
        pos = index_by_email[key]
        if _parse_updated_at(record.get("updated_at")) > _parse_updated_at(
            result[pos].get("updated_at")
        ):
            result[pos] = record

    return result


if __name__ == "__main__":
    import json
    from pathlib import Path

    data = json.loads(Path(__file__).with_name("members.json").read_text(encoding="utf-8"))
    print(json.dumps(dedupe(data), ensure_ascii=False, indent=2))
