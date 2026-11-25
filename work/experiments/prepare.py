"""Create isolated sandboxes and render prompts for the Task Contract experiment.

Usage: python prepare.py <hidden_spec.json> <sandbox_root> [--render-only]
Writes rendered prompts to data/rendered/<run_id>.txt and the run plan (39 runs: E1 21, E2 9, E2b 9) to data/runs.json.
--render-only regenerates prompts and runs.json without creating or wiping sandboxes.
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "prompts")
TASK_DIR = {"T1": "T1_sales", "T2": "T2_dedupe", "T3": "T3_invoice", "E2": "E2_brief", "E2b": "E2b_brief"}


def read(name):
    with open(os.path.join(P, name), encoding="utf-8-sig") as f:
        return f.read().strip()


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    root = sys.argv[2]
    render_only = "--render-only" in sys.argv
    out_dir = os.path.join(HERE, "data", "rendered")
    os.makedirs(out_dir, exist_ok=True)
    runs = []
    plan = [(t, c, i) for t in ["T1", "T2", "T3"] for c, n in [("B", 3), ("TC", 3), ("FULL", 1)] for i in range(1, n + 1)]
    plan += [(e, c, i) for e in ["E2", "E2b"] for c in ["B", "G", "GTB"] for i in range(1, 4)]
    for task, cond, rep in plan:
        run_id = f"{task}-{cond}-{rep}"
        sb = os.path.join(root, run_id)
        if not render_only:
            if os.path.exists(sb):
                shutil.rmtree(sb)
            shutil.copytree(os.path.join(HERE, "tasks", TASK_DIR[task]), sb)
        header = read("_header.txt").replace("{SANDBOX}", sb)
        if task.startswith("E2"):
            g = read("E2_G.txt")
            text = {"B": read("E2_B.txt"), "G": g, "GTB": read("E2_GTB.txt").replace("{G}", g)}[cond]
        else:
            short = read(f"{task}_short.txt")
            reqs = "\n".join(f"- {v}" for v in spec[task]["requirements"].values())
            text = {"B": read("E1_B.txt"), "FULL": read("E1_FULL.txt"), "TC": read("E1_TC_phase1.txt")}[cond]
            text = text.replace("{SHORT}", short).replace("{REQUIREMENTS}", reqs)
        text = text.replace("{HEADER}", header)
        with open(os.path.join(out_dir, f"{run_id}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        runs.append({"run_id": run_id, "task": task, "condition": cond, "rep": rep, "sandbox": sb})
    json.dump(runs, open(os.path.join(HERE, "data", "runs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(runs), "runs prepared")


if __name__ == "__main__":
    main()
