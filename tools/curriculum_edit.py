#!/usr/bin/env python3
"""Place topics in a language's curriculum.csv.

    python3 tools/curriculum_edit.py cpp AFTER_TOPIC_ID < rows.tsv

Each input line is: module<TAB>topic_id<TAB>title<TAB>level<TAB>summary
Existing rows with the same topic_id are removed first (so this both moves and retitles), then the
rows are inserted after AFTER_TOPIC_ID in the given order, and `order` is renumbered 1..N.
"""
import csv, sys
from pathlib import Path

lang, after = sys.argv[1], sys.argv[2]
p = Path(__file__).resolve().parent.parent / "content" / lang / "curriculum.csv"
rows = list(csv.reader(p.open(encoding="utf-8")))
head, body = rows[0], rows[1:]
new = [line.rstrip("\n").split("\t") for line in sys.stdin if line.strip()]
ids = {r[1] for r in new}
body = [r for r in body if r[2] not in ids]
pos = next(i for i, r in enumerate(body) if r[2] == after) + 1
body[pos:pos] = [[""] + r for r in new]
for i, r in enumerate(body, 1):
    r[0] = str(i)
with p.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(head); w.writerows(body)
print(f"placed {len(new)} topics after {after}; {len(body)} topics total")
