"""Show what each E4/E5 run needs next, inferred from sandbox files (orchestration helper).

Usage: python status_e4.py <sandbox_root>
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
root = sys.argv[1]
runs = json.load(open(os.path.join(HERE, "data", "runs_e4.json"), encoding="utf-8"))


def n_timing(sb):
    p = os.path.join(sb, "timing.txt")
    if not os.path.exists(p):
        return 0
    return sum(1 for l in open(p, encoding="utf-8", errors="ignore") if l.strip())


out = {}
snap_root = os.path.join(os.path.dirname(root.rstrip("\\/")), "tc-exp4-snap")
sent_path = os.path.join(snap_root, "sent.txt")
sent = set(open(sent_path, encoding="utf-8-sig").read().split()) if os.path.exists(sent_path) else set()
for r in runs:
    sb = r.get("sandbox") or os.path.join(root, r["run_id"])
    has = lambda f: os.path.exists(os.path.join(sb, f))
    t, c = n_timing(sb), r["condition"]
    # auto-snapshot the end of Phase 1 (before any oracle answer arrives)
    if t >= 2 and not os.path.isdir(os.path.join(snap_root, r["run_id"], "p1")) and not has("answers.md"):
        import subprocess
        subprocess.run([sys.executable, "-B", os.path.join(HERE, "snap.py"), os.path.dirname(sb), snap_root, r["run_id"], "p1"], capture_output=True)
    if r["task"] == "E2c" or c == "FULL":
        st = "done" if (has("report.md") or has("brief.md")) else "p1-running"
    elif c == "BPOST":
        st = "p1-running" if t < 2 else ("need-oracle" if not has("answers.md") else (("p2-running" if r["run_id"] in sent else "need-p2") if t < 4 else "done"))
    elif c == "NOASK":
        st = "p1-running" if t < 2 else ((("p2-running" if r["run_id"] in sent else "need-p2")) if t < 4 else "done")
    else:  # TCP
        if t < 2:
            st = "p1-running"
        elif not has("answers.md"):
            st = "need-oracle"
        elif t < 4:
            st = "p2-running" if r["run_id"] in sent else "need-p2"
        elif has("followup.md") and not has("answers2.md"):
            st = "need-oracle2"
        elif has("followup.md") and t < 6:
            st = "p3-running" if r["run_id"] + ":p3" in sent else "need-p3"
        else:
            st = "done"
    out.setdefault(st, []).append(r["run_id"])
for k in sorted(out):
    print(f"{k} ({len(out[k])}): {' '.join(out[k])}")
