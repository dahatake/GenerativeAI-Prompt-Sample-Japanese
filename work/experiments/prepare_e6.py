"""Prepare sandboxes and render prompts for experiment set v4 (E6 coverage checklist, E7 B-POST remedies, E8 Trust boundary on MAI).

Usage: python prepare_e6.py <hidden_spec.json> <hidden_spec_v2.json> <sandbox_root> [--render-only]
Writes data/rendered_e6/<run_id>__<step>.txt and data/runs_e6.json.
  E6 TCP / TCPCL : p1 -> oracle_contract -> p2 -> [if followup.md] oracle_followup -> p3   (same as E3/E4 TCP)
  E7a BALL       : p1 (B + "list all assumptions") -> oracle_report -> p2                    (same as E3/E4 B-POST)
  E7b OFULL/OFILE: sandbox = task data + v3 B-POST Phase 1 outputs -> oracle_report -> p2 (new session)
  E8 G/GTB/GTB2  : p1 (E2c brief)
Oracles always run on the harness default model (general-purpose agent).
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "prompts")
TASK_DIR = {"T1": "T1_sales", "T4": "T4_timesheet", "E2c": "E2c_brief"}
MODELS = {"mai": "mai-code-2-flash", "gpt": "gpt-6.2-sol"}
GPT_ROOT = r"C:\Users\dahatake\tc-sandbox6"  # GPT-6.2 Sol refuses %TEMP% (v3 deviation D-v3-1)


def read(name):
    with open(os.path.join(P, name), encoding="utf-8-sig") as f:
        return f.read().strip()


def plan():
    runs = []
    for m in MODELS:
        for t in ["T1", "T4"]:
            runs += [("E6", m, t, "TCP", i) for i in (1, 2)]
            runs += [("E6", m, t, "TCPCL", i) for i in (1, 2, 3)]
            runs += [("E7a", m, t, "BALL", i) for i in (1, 2, 3)]
            for i in (1, 2):
                if (m, t) == ("gpt", "T4"):
                    continue  # Phase 1 outputs missing in v3 (D-v3-2)
                runs += [("E7b", m, t, c, i) for c in ("OFULL", "OFILE")]
    runs += [("E8", "mai", "E2c", c, i) for c in ("G", "GTB", "GTB2") for i in range(1, 6)]
    return runs


def main():
    spec = {}
    for p in sys.argv[1:3]:
        spec.update(json.load(open(p, encoding="utf-8")))
    root = sys.argv[3]
    render_only = "--render-only" in sys.argv
    out = os.path.join(HERE, "data", "rendered_e6")
    os.makedirs(out, exist_ok=True)
    timing = read("_timing.txt")
    meta = []
    for exp, m, task, cond, rep in plan():
        rid = f"{exp}-{m}-{task}-{cond}-{rep}"
        sb = os.path.join(GPT_ROOT if m == "gpt" else root, rid)
        if not render_only:
            if os.path.exists(sb):
                shutil.rmtree(sb)
            shutil.copytree(os.path.join(HERE, "tasks", TASK_DIR[task]), sb)
            for dp, _, fns in os.walk(sb):
                for fn in fns:
                    if fn.endswith(".md.txt"):
                        os.replace(os.path.join(dp, fn), os.path.join(dp, fn[:-4]))
            if exp == "E7b":
                src = os.path.join(HERE, "data", "artifacts_e4", f"E4-{m}-{task}-BPOST-{rep}", "p1")
                shutil.copy(os.path.join(src, "solution.py"), os.path.join(sb, "solution.py"))
                shutil.copy(os.path.join(src, "report.md.txt"), os.path.join(sb, "report.md"))
        header = read("_header.txt").replace("{SANDBOX}", sb)
        steps = {}
        if task == "E2c":
            g = read("E2_G.txt")
            steps["p1"] = {"G": g, "GTB": read("E2_GTB.txt").replace("{G}", g), "GTB2": read("E2_GTB2.txt").replace("{G}", g)}[cond]
        else:
            short = read(f"{task}_short.txt")
            reqs = "\n".join(f"- {v}" for v in spec[task]["requirements"].values())
            if exp == "E6":
                steps["p1"] = read("E3_TCP_phase1.txt" if cond == "TCP" else "E6_TCPCL_phase1.txt").replace("{SHORT}", short)
                steps["p2"] = read("E3_TCP_phase2.txt")
                steps["p3"] = read("E3_TCP_phase3.txt")
                o = read("ORACLE_FILE.txt").replace("{SANDBOX}", sb).replace("{REQUIREMENTS}", reqs)
                steps["oracle_contract"] = o.replace("{QFILE}", "contract.md").replace("{AFILE}", "answers.md")
                steps["oracle_followup"] = o.replace("{QFILE}", "followup.md").replace("{AFILE}", "answers2.md")
            elif exp == "E7a":
                steps["p1"] = read("E7_BALL.txt").replace("{SHORT}", short)
                steps["p2"] = read("E3_BPOST_phase2.txt")
                o = read("ORACLE_FILE.txt").replace("{SANDBOX}", sb).replace("{REQUIREMENTS}", reqs)
                steps["oracle_report"] = o.replace("{QFILE}", "report.md").replace("{AFILE}", "answers.md")
            else:  # E7b
                o = read("ORACLE_FULL.txt" if cond == "OFULL" else "ORACLE_FILE.txt")
                steps["oracle_report"] = o.replace("{SANDBOX}", sb).replace("{REQUIREMENTS}", reqs).replace("{QFILE}", "report.md").replace("{AFILE}", "answers.md")
                steps["p2"] = read("E7b_phase2_newsession.txt").replace("{SHORT}", short)
        for k, v in steps.items():
            v = v.replace("{HEADER}", header).replace("{TIMING}", timing)
            with open(os.path.join(out, f"{rid}__{k}.txt"), "w", encoding="utf-8") as f:
                f.write(v)
        meta.append({"run_id": rid, "experiment": exp, "model": MODELS[m], "task": task, "condition": cond,
                     "rep": rep, "sandbox": sb, "steps": list(steps)})
    json.dump(meta, open(os.path.join(HERE, "data", "runs_e6.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(meta), "runs prepared")


if __name__ == "__main__":
    main()
