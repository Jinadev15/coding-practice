#!/usr/bin/env python3
"""Fill in missing expected outputs in a problem's ## Tests from its reference solution.

    python3 tools/fill_expected.py cpp cpp-fraction [cpp-other ...]

Only outputs shorter than MAX_CHARS are written; longer ones stay computed at judge time.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.content import Catalog  # noqa: E402
from app.judge import expected_outputs  # noqa: E402

MAX_CHARS = 3000


def fill(lang, p) -> int:
    outs = expected_outputs(lang, p)
    text = p.path.read_text(encoding="utf-8")
    start = text.index("\n## Tests\n") + len("\n## Tests\n")
    m = re.search(r"^## ", text[start:], flags=re.M)
    end = start + m.start() if m else len(text)
    section = text[start:end]
    pieces = re.split(r"(^===[ \t]*\w*[ \t]*$)", section, flags=re.M)
    # pieces = [preamble, header1, body1, header2, body2, ...]
    n = 0
    for i, out in zip(range(2, len(pieces), 2), outs):
        body = pieces[i]
        if re.search(r"^---[ \t]*$", body, flags=re.M) or len(out) > MAX_CHARS:
            continue
        trailing = len(body) - len(body.rstrip("\n"))
        pieces[i] = body.rstrip("\n") + "\n---\n" + out.rstrip("\n") + "\n" * max(trailing, 1)
        n += 1
    p.path.write_text(text[:start] + "".join(pieces) + text[end:], encoding="utf-8")
    return n


def main() -> None:
    lang_id, *pids = sys.argv[1:]
    lang = Catalog().get()[lang_id]
    for pid in pids:
        print(pid, "filled", fill(lang, lang.problems[pid]))


if __name__ == "__main__":
    main()
