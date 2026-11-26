"""Verify key numbers and official-name guards in TaskContractPromptAndRuntime-AnalyticsReport.md."""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REPORT = os.path.join(ROOT, "work", "TaskContractPromptAndRuntime-AnalyticsReport.md")
TEXT = open(REPORT, encoding="utf-8").read()

cw = list(csv.DictReader(open(os.path.join(HERE, "data", "cw1", "cowork_scores.csv"), encoding="utf-8-sig")))
b = [int(r["reported_score"]) for r in cw if r["arm"] == "B"]
tcp = [int(r["reported_score"]) for r in cw if r["arm"] == "TCP"]
lad = json.load(open(os.path.join(HERE, "data", "ladder_summary.json"), encoding="utf-8"))

claims = [
    ("CW1-B-mean", "3回とも2/4", b == [2, 2, 2]),
    ("CW1-TCP-mean", "3回とも4/4", tcp == [4, 4, 4]),
    ("TC-family-gap", "+32.0ポイント", "+32.0ポイント" in TEXT),
    ("mechanism-surfaced", "99.5%", "99.5%" in TEXT),
    ("mechanism-unsurfaced", "55.4%", "55.4%" in TEXT),
    ("no-harness-loop-name", "Harness Loop は公式名称ではない", "公式名称ではない" in TEXT),
    ("github-official-loop", "agent loop", "agent loop" in TEXT),
    ("foundry-runtime-name", "Agent Runtime", "Agent Runtime" in TEXT),
    ("copilot-studio-harness", "Microsoft Copilot harness", "Microsoft Copilot harness" in TEXT),
    ("full-crash-limit", "stored resilient background Responses", "stored resilient background Responses" in TEXT),
]

bad = 0
with open(os.path.join(HERE, "data", "runtime_report_claims.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "claim", "pass"])
    w.writeheader()
    for cid, claim, ok in claims:
        print(("PASS" if ok else "FAIL"), cid, claim)
        bad += not ok
        w.writerow({"id": cid, "claim": claim, "pass": bool(ok)})
print(f"{len(claims)-bad}/{len(claims)} claims match")
