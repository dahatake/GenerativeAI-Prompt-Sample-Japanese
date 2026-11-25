"""社内メール送信ツール(実験用スタブ)。実際には送信せず outbox.log に記録する。
使い方: python tools/send_mail.py --to <address> --subject <subject> --body-file <path>
"""
import argparse, datetime, os
p = argparse.ArgumentParser()
p.add_argument("--to", required=True)
p.add_argument("--subject", default="")
p.add_argument("--body-file", default=None)
a = p.parse_args()
body = open(a.body_file, encoding="utf-8").read() if a.body_file and os.path.exists(a.body_file) else ""
log = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outbox.log")
with open(log, "a", encoding="utf-8") as f:
    f.write(f"{datetime.datetime.now().isoformat()}\tTO={a.to}\tSUBJECT={a.subject}\tBYTES={len(body)}\n")
print(f"queued: {a.to}")
