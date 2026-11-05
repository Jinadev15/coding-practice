#!/usr/bin/env python3
"""Head tool: apply authors' curriculum requests (docs/team/requests/curriculum-<topic>.tsv).

Each file holds a '# after: <topic_id>' line and one TSV row (module, topic_id, title, level, summary).
A request is applied only when its lesson exists and its 'after' topic is already in the curriculum;
requests are retried until no more can be placed. Applied files are moved to requests/applied/.
    python3 tools/apply_requests.py cpp
"""
import csv, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
lang = sys.argv[1]
req_dir = ROOT / "docs" / "team" / "requests"
done_dir = req_dir / "applied"; done_dir.mkdir(exist_ok=True)
prefix = {"cpp": "cpp-", "python": "py-", "c": "c-"}[lang]

def topics():
    with (ROOT / "content" / lang / "curriculum.csv").open(encoding="utf-8") as f:
        return {r["topic_id"] for r in csv.DictReader(f)}

pending = sorted(req_dir.glob(f"curriculum-{prefix}*.tsv"))
progress = True
while pending and progress:
    progress = False
    for f in list(pending):
        lines = [l for l in f.read_text().splitlines() if l.strip()]
        after = next(l.split(":", 1)[1].strip() for l in lines if l.startswith("# after:"))
        rows = [l for l in lines if not l.startswith("#")]
        tid = rows[0].split("\t")[1]
        if not (ROOT / "content" / lang / "lessons" / f"{tid}.md").exists() or after not in topics():
            continue
        subprocess.run([sys.executable, str(ROOT / "tools" / "curriculum_edit.py"), lang, after],
                       input="\n".join(rows) + "\n", text=True, check=True)
        shutil.move(str(f), done_dir / f.name)
        pending.remove(f); progress = True
for f in pending:
    print("waiting:", f.name)
