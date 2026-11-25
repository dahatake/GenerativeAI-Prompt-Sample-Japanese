def dedupe(records):
    order, best, out_slots = [], {}, []
    for i, r in enumerate(records):
        e = r.get("email")
        key = e.strip().lower() if isinstance(e, str) and e.strip() else None
        if key is None:
            out_slots.append(("raw", r)); continue
        if key not in best:
            best[key] = r; out_slots.append(("key", key))
        elif r["updated_at"] > best[key]["updated_at"]:
            best[key] = r
    return [s[1] if s[0] == "raw" else best[s[1]] for s in out_slots]
