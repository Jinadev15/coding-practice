"""Append MCQ rows to a CSV with correct quoting.
Usage: python3 tools/add_mcqs.py content/python/mcq/file.csv < rows.txt
(Writes correctly quoted CSV rows, so commas and quotes in questions/code never break the file.)
rows.txt format: blocks separated by a line '%%'. Each block has 'key: value' lines;
multi-line values continue on following lines until the next 'key:' line.
Keys: id topic difficulty type question code a b c d answer explanation
"""
import csv, sys, re
path = sys.argv[1]
text = sys.stdin.read()
cols = ["id","topic","difficulty","type","question","code","option_a","option_b","option_c","option_d","answer","explanation"]
keymap = {"a":"option_a","b":"option_b","c":"option_c","d":"option_d"}
rows = []
for block in text.split("\n%%\n"):
    if not block.strip():
        continue
    row, key = {}, None
    for line in block.split("\n"):
        m = re.match(r"^(id|topic|difficulty|type|question|code|a|b|c|d|answer|explanation):\s?(.*)$", line)
        if m:
            key = keymap.get(m.group(1), m.group(1))
            row[key] = m.group(2)
        elif key:
            row[key] += "\n" + line
    row = {k: v.rstrip("\n") for k, v in row.items()}
    missing = [c for c in cols if c not in row and c != "code"]
    if missing:
        sys.exit(f"block {row.get('id')} missing {missing}")
    rows.append(row)
import os
new = not os.path.exists(path)
with open(path, "a", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    if new:
        w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in cols})
print(f"appended {len(rows)} rows to {path}")
