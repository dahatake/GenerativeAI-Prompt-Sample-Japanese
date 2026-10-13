from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

INPUT_FILE = Path("sample_data/incidents.csv")
OUTPUT_FILE = Path("sample_data/incident_summary.txt")


def load_incidents(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def summarize_by_service(rows: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "minutes": 0})
    for row in rows:
        service = row["service"]
        summary[service]["count"] += 1
        summary[service]["minutes"] += int(row["impact_minutes"])
    return dict(summary)


def write_summary(path: Path, summary: dict[str, dict[str, int]]) -> None:
    lines = ["サービス別インシデント集計"]
    for service, data in sorted(summary.items()):
        lines.append(f"- {service}: {data['count']}件 / 影響時間 {data['minutes']}分")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    incidents = load_incidents(INPUT_FILE)
    summary = summarize_by_service(incidents)
    write_summary(OUTPUT_FILE, summary)
    print(OUTPUT_FILE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
