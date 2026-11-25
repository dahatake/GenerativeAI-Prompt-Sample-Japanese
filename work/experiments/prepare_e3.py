"""Prepare sandboxes and render all prompts for experiment set v2 (E3, E2-BDoD, E2c).

Usage: python prepare_e3.py <hidden_spec.json> <hidden_spec_v2.json> <sandbox_root> [--render-only]
Writes data/rendered_e3/<run_id>__<step>.txt and data/runs_e3.json.
Steps per condition:
  B-POST : p1 (B prompt) -> oracle_report -> p2
  TC     : p1 -> oracle_contract -> p2
  TCP    : p1 -> oracle_contract -> p2 -> [if followup.md] oracle_followup -> p3
  NOASK  : p1 -> p2 (no oracle)
  FULL   : p1
  E2*    : p1
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "prompts")
TASK_DIR = {"T1": "T1_sales", "T3": "T3_invoice", "T4": "T4_timesheet", "T5": "T5_reorder",
            "E2": "E2_brief", "E2c": "E2c_brief"}


def read(name):
    with open(os.path.join(P, name), encoding="utf-8-sig") as f:
        return f.read().strip()


def plan():
    runs = []
    for t in ["T1", "T3"]:
        for c in ["TCP", "BPOST", "NOASK"]:
            runs += [(t, c, i) for i in (1, 2, 3)]
    for t in ["T4", "T5"]:
        for c in ["BPOST", "TC", "TCP", "NOASK"]:
            runs += [(t, c, i) for i in (1, 2, 3)]
        runs.append((t, "FULL", 1))
    runs += [("E2", "BDOD", i) for i in (1, 2, 3)]
    runs += [("E2c", c, i) for c in ["B", "G", "GTB"] for i in (1, 2, 3)]
    return runs


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    spec.update(json.load(open(sys.argv[2], encoding="utf-8")))
    root = sys.argv[3]
    render_only = "--render-only" in sys.argv
    out = os.path.join(HERE, "data", "rendered_e3")
    os.makedirs(out, exist_ok=True)
    timing = read("_timing.txt")
    meta = []
    for task, cond, rep in plan():
        rid = f"E3-{task}-{cond}-{rep}" if task.startswith("T") else f"{task}-{cond}-{rep}"
        sb = os.path.join(root, rid)
        if not render_only:
            if os.path.exists(sb):
                shutil.rmtree(sb)
            shutil.copytree(os.path.join(HERE, "tasks", TASK_DIR[task]), sb)
            # Task .md files are stored as .md.txt so the site build does not publish them (e.g. the E2c injection file).
            for dp, _, fns in os.walk(sb):
                for fn in fns:
                    if fn.endswith(".md.txt"):
                        os.replace(os.path.join(dp, fn), os.path.join(dp, fn[:-4]))
        header = read("_header.txt").replace("{SANDBOX}", sb)
        steps = {}
        if task.startswith("E2"):
            g = read("E2_G.txt")
            steps["p1"] = {"B": read("E2_B.txt"), "G": g, "GTB": read("E2_GTB.txt").replace("{G}", g), "BDOD": read("E2_BDOD.txt")}[cond]
        else:
            short = read(f"{task}_short.txt")
            reqs = "\n".join(f"- {v}" for v in spec[task]["requirements"].values())
            p1 = {"BPOST": "E3_B.txt", "TC": "E3_TC_phase1.txt", "NOASK": "E3_TC_phase1.txt", "TCP": "E3_TCP_phase1.txt", "FULL": "E3_FULL.txt"}[cond]
            steps["p1"] = read(p1).replace("{SHORT}", short).replace("{REQUIREMENTS}", reqs)
            p2 = {"BPOST": "E3_BPOST_phase2.txt", "TC": "E3_TC_phase2.txt", "NOASK": "E3_NOASK_phase2.txt", "TCP": "E3_TCP_phase2.txt"}.get(cond)
            if p2:
                steps["p2"] = read(p2)
            if cond == "TCP":
                steps["p3"] = read("E3_TCP_phase3.txt")
            oracle = read("ORACLE_FILE.txt").replace("{SANDBOX}", sb).replace("{REQUIREMENTS}", reqs)
            if cond in ("TC", "TCP"):
                steps["oracle_contract"] = oracle.replace("{QFILE}", "contract.md").replace("{AFILE}", "answers.md")
            if cond == "BPOST":
                steps["oracle_report"] = oracle.replace("{QFILE}", "report.md").replace("{AFILE}", "answers.md")
            if cond == "TCP":
                steps["oracle_followup"] = oracle.replace("{QFILE}", "followup.md").replace("{AFILE}", "answers2.md")
        for k, v in steps.items():
            v = v.replace("{HEADER}", header).replace("{TIMING}", timing)
            with open(os.path.join(out, f"{rid}__{k}.txt"), "w", encoding="utf-8") as f:
                f.write(v)
        meta.append({"run_id": rid, "task": task, "condition": cond, "rep": rep, "sandbox": sb, "steps": list(steps)})
    json.dump(meta, open(os.path.join(HERE, "data", "runs_e3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(meta), "runs prepared")


if __name__ == "__main__":
    main()
