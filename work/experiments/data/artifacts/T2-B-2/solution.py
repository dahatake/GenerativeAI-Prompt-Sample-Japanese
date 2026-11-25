import unicodedata
from datetime import datetime, timezone

_OLDEST = datetime.min.replace(tzinfo=timezone.utc)


def _normalize_email(email):
    if not isinstance(email, str):
        return None
    normalized = unicodedata.normalize("NFKC", email).strip().lower()
    return normalized or None


def _parse_updated_at(value):
    if not isinstance(value, str) or not value.strip():
        return _OLDEST
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return _OLDEST
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def dedupe(records):
    """Remove duplicate member records.

    Records are considered duplicates when their e-mail addresses match after
    normalization (NFKC, trim, lower-case). Within a duplicate group the record
    with the latest ``updated_at`` is kept (ties keep the earlier record), placed
    at the position where the group first appeared. Records without a usable
    e-mail are never merged. Input records are not modified.
    """
    result = []
    index_by_email = {}

    for record in records:
        email = _normalize_email(record.get("email"))
        if email is None:
            result.append(record)
            continue

        if email not in index_by_email:
            index_by_email[email] = len(result)
            result.append(record)
            continue

        idx = index_by_email[email]
        if _parse_updated_at(record.get("updated_at")) > _parse_updated_at(
            result[idx].get("updated_at")
        ):
            result[idx] = record

    return result


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("members.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(dedupe(data), ensure_ascii=False, indent=2))
