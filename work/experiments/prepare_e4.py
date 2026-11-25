"""Prepare sandboxes and render prompts for experiment set v3 (E4: multi-model replication, E5: long task T6).

Usage: python prepare_e4.py <hidden_spec.json> <hidden_spec_v2.json> <hidden_spec_v3.json> <sandbox_root> [--render-only]
Writes data/rendered_e4/<run_id>__<step>.txt and data/runs_e4.json.
Prompts, oracle and step order are identical to E3 (prepare_e3.py); only the subject model differs (field "model").
Oracles always run on the harness default model.
  B-POST : p1 (B prompt) -> oracle_report -> p2
  TCP    : p1 -> oracle_contract -> p2 -> [if followup.md] oracle_followup -> p3
  NOASK  : p1 -> p2 (no oracle)
  FULL, E2c : p1
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "prompts")
TASK_DIR = {"T1": "T1_sales", "T3": "T3_invoice", "T4": "T4_timesheet", "T6": "T6_billing", "E2c": "E2c_brief"}
MODELS = {"mai": "mai-code-2-flash", "son": "claude-sonnet-5.5", "gpt": "gpt-6.2-sol"}


def read(name):
    with open(os.path.join(P, name), encoding="utf-8-sig") as f:
        return f.read().strip()


def plan():
    runs = []
    for m in MODELS:
        for t in ["T1", "T3", "T4"]:
            for c in ["BPOST", "TCP", "NOASK"]:
                runs += [("E4", m, t, c, i) for i in (1, 2)]
        runs.append(("E4", m, "E2c", "B", 1))
        runs += [("E4", m, "E2c", c, i) for c in ["G", "GTB"] for i in (1, 2)]
    for c in ["BPOST", "TCP", "NOASK"]:
        runs += [("E5", "default", "T6", c, i) for i in (1, 2, 3)]
    runs.append(("E5", "default", "T6", "FULL", 1))
    return runs


def main():
    spec = {}
    for p in sys.argv[1:4]:
        spec.update(json.load(open(p, encoding="utf-8")))
    root = sys.argv[4]
    render_only = "--render-only" in sys.argv
    out = os.path.join(HERE, "data", "rendered_e4")
    os.makedirs(out, exist_ok=True)
    timing = read("_timing.txt")
    meta = []
    for exp, model, task, cond, rep in plan():
        rid = f"{exp}-{model}-{task}-{cond}-{rep}" if exp == "E4" else f"{exp}-{task}-{cond}-{rep}"
        sb = os.path.join(root, rid)
        if not render_only:
            if os.path.exists(sb):
                shutil.rmtree(sb)
            shutil.copytree(os.path.join(HERE, "tasks", TASK_DIR[task]), sb)
            for dp, _, fns in os.walk(sb):
                for fn in fns:
                    if fn.endswith(".md.txt"):
                        os.replace(os.path.join(dp, fn), os.path.join(dp, fn[:-4]))
        header = read("_header.txt").replace("{SANDBOX}", sb)
        steps = {}
        if task == "E2c":
            g = read("E2_G.txt")
            steps["p1"] = {"B": read("E2_B.txt"), "G": g, "GTB": read("E2_GTB.txt").replace("{G}", g)}[cond]
        else:
            short = read(f"{task}_short.txt")
            reqs = "\n".join(f"- {v}" for v in spec[task]["requirements"].values())
            p1 = {"BPOST": "E3_B.txt", "NOASK": "E3_TC_phase1.txt", "TCP": "E3_TCP_phase1.txt", "FULL": "E3_FULL.txt"}[cond]
            steps["p1"] = read(p1).replace("{SHORT}", short).replace("{REQUIREMENTS}", reqs)
            p2 = {"BPOST": "E3_BPOST_phase2.txt", "NOASK": "E3_NOASK_phase2.txt", "TCP": "E3_TCP_phase2.txt"}.get(cond)
            if p2:
                steps["p2"] = read(p2)
            if cond == "TCP":
                steps["p3"] = read("E3_TCP_phase3.txt")
            oracle = read("ORACLE_FILE.txt").replace("{SANDBOX}", sb).replace("{REQUIREMENTS}", reqs)
            if cond == "TCP":
                steps["oracle_contract"] = oracle.replace("{QFILE}", "contract.md").replace("{AFILE}", "answers.md")
                steps["oracle_followup"] = oracle.replace("{QFILE}", "followup.md").replace("{AFILE}", "answers2.md")
            if cond == "BPOST":
                steps["oracle_report"] = oracle.replace("{QFILE}", "report.md").replace("{AFILE}", "answers.md")
        for k, v in steps.items():
            v = v.replace("{HEADER}", header).replace("{TIMING}", timing)
            with open(os.path.join(out, f"{rid}__{k}.txt"), "w", encoding="utf-8") as f:
                f.write(v)
        meta.append({"run_id": rid, "experiment": exp, "model": MODELS.get(model, "harness-default"), "task": task,
                     "condition": cond, "rep": rep, "sandbox": sb, "steps": list(steps)})
    json.dump(meta, open(os.path.join(HERE, "data", "runs_e4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(meta), "runs prepared")


if __name__ == "__main__":
    main()
