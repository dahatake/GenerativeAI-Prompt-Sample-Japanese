"""Snapshot sandbox files at the end of a phase (outside the sandbox, so later phases cannot see/alter them).

Usage: python snap.py <sandbox_root> <snap_root> <run_id> <stage>
"""
import os, shutil, sys

root, snap_root, rid, stage = sys.argv[1:5]
src = os.path.join(root, rid)
dst = os.path.join(snap_root, rid, stage)
os.makedirs(dst, exist_ok=True)
copied = []
for name in ["solution.py", "report.md", "contract.md", "answers.md", "followup.md", "answers2.md", "timing.txt", "brief.md", "outbox.log"]:
    p = os.path.join(src, name)
    if os.path.exists(p):
        shutil.copy(p, os.path.join(dst, name))
        copied.append(name)
print(rid, stage, copied)
