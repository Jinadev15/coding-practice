"""Loads all learning content from the content/ folder.

Nothing about a language is hardcoded here. Every folder in content/ that has a
language.json is a language. See CONTENT_GUIDE.md for the file formats.
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert", "Research"]
MILESTONES = {1: 25, 2: 50, 3: 75, 4: 100}


@dataclass
class Test:
    input: str
    output: str | None
    sample: bool


@dataclass
class Problem:
    id: str
    lang: str
    topic: str                      # topic id, or "milestone-N"
    title: str
    difficulty: str
    meta: dict
    statement: str
    starters: dict[str, str]        # filename -> code shown in editor
    drivers: dict[str, str]         # filename -> hidden code ("" key = append to main)
    tests: list[Test]
    solution_md: str
    solution_files: dict[str, str]
    hints: list[str]
    path: Path

    @property
    def milestone(self) -> int | None:
        m = re.fullmatch(r"milestone-(\d)", self.topic)
        return int(m.group(1)) if m else None


@dataclass
class Topic:
    id: str
    order: float
    module: str
    title: str
    level: str
    summary: str
    lesson_path: Path | None = None
    mcqs: list[dict] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


@dataclass
class Language:
    id: str
    config: dict
    topics: list[Topic]
    topic_map: dict[str, Topic]
    problems: dict[str, Problem]
    milestones: dict[int, list[str]]
    errors: list[str]

    @property
    def name(self) -> str:
        return self.config.get("name", self.id)


# ---------------------------------------------------------------- parsing

FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
FENCE = re.compile(r"```([^\n]*)\n(.*?)\n```", re.S)
NON_CODE = {"text", "output", "plain", "console", "mermaid", "markdown"}


def parse_front_matter(text: str) -> tuple[dict, str]:
    m = FRONT.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def split_sections(body: str) -> list[tuple[str, str]]:
    """Split on level-2 headings that are not inside code fences."""
    sections, name, buf, in_fence = [], None, [], False
    for line in body.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            if name is not None:
                sections.append((name, "\n".join(buf).strip("\n")))
            name, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if name is not None:
        sections.append((name, "\n".join(buf).strip("\n")))
    return sections


def first_fence(text: str) -> str | None:
    """First fenced code block, skipping text/output/diagram blocks."""
    blocks = FENCE.findall(text)
    for lang, code in blocks:
        if lang.strip().split()[:1] and lang.strip().split()[0] not in NON_CODE:
            return code
    return blocks[0][1] if blocks else None


def parse_tests(text: str) -> list[Test]:
    tests: list[Test] = []
    blocks = re.split(r"^===[ \t]*(\w*)[ \t]*$", text, flags=re.M)
    # blocks = [preamble, kind1, body1, kind2, body2, ...]
    for kind, body in zip(blocks[1::2], blocks[2::2]):
        body = body[1:] if body.startswith("\n") else body   # rest of the === line
        parts = re.split(r"^---[ \t]*$", body, maxsplit=1, flags=re.M)
        out = None
        if len(parts) > 1:
            # input keeps blank lines (an empty input line is meaningful)
            inp = parts[0] if parts[0].endswith("\n") else parts[0] + "\n"
            out = parts[1][1:] if parts[1].startswith("\n") else parts[1]
            out = out.rstrip("\n")   # leading blank lines are significant
        else:
            inp = parts[0].rstrip("\n") + "\n"
        tests.append(Test(inp, out, (kind or "hidden").lower() == "sample"))
    return tests


def load_problem(path: Path, lang: str, topic: str, main_file: str) -> Problem:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    p = Problem(
        id=meta.get("id") or path.stem, lang=lang, topic=meta.get("topic", topic),
        title=meta.get("title", path.stem), difficulty=meta.get("difficulty", "Medium"),
        meta=meta, statement="", starters={}, drivers={}, tests=[], solution_md="",
        solution_files={}, hints=[], path=path,
    )
    for name, content in split_sections(body):
        key, _, arg = name.partition(":")
        key, arg = key.strip().lower(), arg.strip()
        if key == "statement":
            p.statement = content
        elif key == "starter":
            p.starters[arg or main_file] = first_fence(content) or ""
        elif key == "driver":
            p.drivers[arg] = first_fence(content) or ""
        elif key == "tests":
            p.tests = parse_tests(content)
        elif key == "solution" and not arg:
            p.solution_md = content
        elif key == "solution":
            p.solution_files[arg] = first_fence(content) or ""
        elif key == "hints":
            p.hints = [h[2:].strip() for h in content.splitlines() if h.startswith("- ")]
    if not p.starters:
        p.starters[main_file] = ""
    if not p.solution_files:
        code = first_fence(p.solution_md)
        if code is not None:
            p.solution_files[main_file] = code
    return p


def load_mcq_csv(path: Path, errors: list[str] | None = None) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            if None in r or any(v is None for v in r.values()):
                if errors is not None:
                    errors.append(f"{path.name}: row {i + 2} ({r.get('id')}) has the wrong number of "
                                  "columns — quote any field containing a comma")
                continue
            r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
            opts = [r.get(f"option_{c}", "") for c in "abcdef"]
            opts = [o for o in opts if o]
            answer = [a.strip().upper() for a in re.split(r"[|,]", r.get("answer", "")) if a.strip()]
            rows.append({
                "id": r.get("id") or f"{path.stem}-{i + 1}",
                "topic": r.get("topic", ""),
                "difficulty": r.get("difficulty", "Medium"),
                "type": r.get("type", "theory"),
                "question": r.get("question", "").replace("\\n", "\n"),
                "code": r.get("code", "").replace("\\n", "\n"),
                "options": opts,
                "answer": ["ABCDEF".index(a) for a in answer if a in "ABCDEF"],
                "explanation": r.get("explanation", "").replace("\\n", "\n"),
                "source": path.name,
            })
    return rows


def load_language(folder: Path) -> Language:
    config = json.loads((folder / "language.json").read_text(encoding="utf-8"))
    lang = folder.name
    main_file = config.get("main", f"main.{config.get('ext', 'txt')}")
    errors: list[str] = []
    topics: list[Topic] = []
    cur = folder / "curriculum.csv"
    if cur.exists():
        with cur.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
                if not r.get("topic_id"):
                    continue
                topics.append(Topic(
                    id=r["topic_id"], order=float(r.get("order") or len(topics) + 1),
                    module=r.get("module", "General"), title=r.get("title", r["topic_id"]),
                    level=r.get("level", "Beginner"), summary=r.get("summary", ""),
                ))
    topics.sort(key=lambda t: t.order)
    tmap = {t.id: t for t in topics}

    for t in topics:
        lp = folder / "lessons" / f"{t.id}.md"
        t.lesson_path = lp if lp.exists() else None

    for path in sorted((folder / "mcq").glob("*.csv")) if (folder / "mcq").exists() else []:
        try:
            for q in load_mcq_csv(path, errors):
                if q["topic"] in tmap:
                    tmap[q["topic"]].mcqs.append(q)
                else:
                    errors.append(f"{path.name}: MCQ {q['id']} has unknown topic '{q['topic']}'")
        except Exception as e:  # noqa: BLE001 - surface any bad file, keep loading
            errors.append(f"{path.name}: {e}")

    problems: dict[str, Problem] = {}
    milestones: dict[int, list[str]] = {n: [] for n in MILESTONES}
    pdir = folder / "problems"
    for path in sorted(pdir.rglob("*.md")) if pdir.exists() else []:
        topic = path.parent.name
        try:
            p = load_problem(path, lang, topic, main_file)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{path.relative_to(folder)}: {e}")
            continue
        if p.id in problems:
            errors.append(f"duplicate problem id {p.id}")
            continue
        problems[p.id] = p
        if p.milestone:
            milestones.setdefault(p.milestone, []).append(p.id)
        elif p.topic in tmap:
            tmap[p.topic].problems.append(p.id)
        else:
            errors.append(f"{path.relative_to(folder)}: unknown topic folder '{p.topic}'")
    def order_key(pid):
        p = problems[pid]
        try:
            return (float(p.meta.get("order", 999)), p.path.name)
        except ValueError:
            return (999.0, p.path.name)
    for t in topics:
        t.problems.sort(key=order_key)
    for n in milestones:
        milestones[n].sort(key=order_key)
    return Language(lang, config, topics, tmap, problems, milestones, errors)


class Catalog:
    """All languages, reloaded when any content file changes."""

    def __init__(self) -> None:
        self._stamp = None
        self.languages: dict[str, Language] = {}

    def _current_stamp(self):
        latest, count = 0.0, 0
        for p in CONTENT.rglob("*"):
            if p.is_file():
                count += 1
                latest = max(latest, p.stat().st_mtime)
        return latest, count

    def get(self) -> dict[str, Language]:
        stamp = self._current_stamp()
        if stamp != self._stamp:
            langs = {}
            for folder in sorted(CONTENT.iterdir()):
                if (folder / "language.json").exists():
                    langs[folder.name] = load_language(folder)
            langs = dict(sorted(langs.items(), key=lambda kv: kv[1].config.get("order", 99)))
            self.languages, self._stamp = langs, stamp
        return self.languages
