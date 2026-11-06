# Head playbook: roles, rules and workflow for every agent

Read `CEO_BRIEF.md` first. Then read your role section and the shared rules. The repository root is `/home/jinadev-rp/Projects/Private/coding_practice`.

## Roles

| Agent | Role | Writes to |
|---|---|---|
| CEO | objective, quality bar, final checks | `docs/team/CEO_BRIEF.md` |
| Head | assigns work, integrates, commits, resolves conflicts | `docs/team/TASK_BOARD.md`, `content/*/curriculum.csv`, git |
| Agent 1: Planner | complete topic and problem plans per language | `docs/team/plan/<lang>.md` |
| Agent 2: Author(s) | lessons, problems and MCQs for assigned topics | see "File ownership" |
| Agent 3: Reviewer | audits work, fixes defects, gives feedback | `docs/team/feedback/<topic>.md`, plus fixes in place |

## Shared rules (all agents)

1. **No git commands that change anything** (no commit, push, reset or checkout). The Head commits.
2. **Only edit files you own** (table below). If something outside your files must change, write a request in `docs/team/requests/<your-agent>-<topic>.md`.
3. **Never** edit `content/*/curriculum.csv`, existing shared MCQ files (`content/*/mcq/0*.csv`, `1*.csv`), the app code (`app/`, `server.py`, `static/`), or another author's topic.
4. **Never embed test inputs larger than 8 KB.** Use the spec's `=== gen` section. The builder stores big tests as `@gen SEED SIZE` automatically.
5. **Keep it deterministic.** Generators use `random.Random(int(sys.argv[1]))`, and `sys.argv[2]` is `small` or `big`.
6. **When finished,** write a short report to `docs/team/reports/<your-agent>.md`: topics done, problem ids, anything the Head must do.

## File ownership for an Author working on topic `<t>` in language `<lang>`

- `content/<lang>/lessons/<t>.md`
- `content/<lang>/problems/<t>/` (only through `tools/build_problem.py`)
- `.authoring/<lang>/<t>/*.spec` (your problem sources; this folder is gitignored)
- `content/<lang>/mcq/t-<t>.csv` (a NEW file per topic; create it with `tools/add_mcqs.py`)
- `docs/team/requests/curriculum-<t>.tsv`: one TSV line `module<TAB>topic_id<TAB>title<TAB>level<TAB>summary`, plus a first line `# after: <topic_id>`

## Author workflow, per topic

1. Read the plan entry (`docs/team/plan/<lang>.md`, or the assignment text from the Head) and the existing lesson and problems for the topic, if any. Keep existing problem files unless told otherwise. Existing old "suite" problems stay as the last, mixed-review problem (set their `order:` after yours).
2. Write the lesson to the CEO bar.
3. Write one spec per problem in `.authoring/<lang>/<t>/N-name.spec`, then run `python3 tools/build_problem.py .authoring/<lang>/<t>/N-name.spec` until it prints `ok`. Read `tools/build_problem.py` once to learn the spec format, and look at `.authoring/cpp/cpp-dsa-list-reversal/*.spec` or `.authoring/cpp/cpp-dsa-hashing/*.spec` as examples.
   - **C/C++:** drivers free all memory, because LeakSanitizer fails on leaks.
   - **Python:** no `if __name__ == "__main__"` and no `from __future__`, because the driver is appended to the user's file.
   - `compare: float` for real-valued answers.
   - **Time limit:** 1–2 s. The reference must use under 30% of it. Make the starter fail, either as a stub or as a naive slow version.
   - **Starter code** contains the struct/class definitions the driver needs, plus function stubs.
4. Add 8–14 MCQs: `python3 tools/add_mcqs.py content/<lang>/mcq/t-<t>.csv <<'EOF' … EOF`. The ids must be unique: prefix them with an abbreviation of the topic (for example `cpp-heap-01`). The tool refuses duplicates.
5. Run `python3 tools/validate.py <lang> <problem-id>` for each new problem. Everything must be OK.
6. File the curriculum request and the report.

**Parallel-safety:** several authors run at once, so timing can be noisy. If the builder fails only on the "reference takes …" timing check, rerun it once. If it fails again, make the reference faster or the big test smaller.

## Reviewer workflow

For each topic listed in your assignment:

- **Correctness:** run `python3 tools/validate.py <lang> <id>` for its problems, and read every lesson code block. When in doubt, compile it or run it.
- **Teaching quality:** check the lesson against the CEO bar: missing sections, unclear explanations, wrong complexity claims, missing edge cases.
- **Problem quality:** check that statements are precise, the samples are meaningful, hints teach rather than give the answer away, problems aren't duplicates within the topic, the difficulty progression is sensible, and nothing is weak (could a wrong solution pass?).
- **Fix** small defects directly (typos, wrong claims, a weak or missing test via the spec plus a rebuild). For large issues, write actionable feedback in `docs/team/feedback/<topic>.md` for the author or the Head.
- **Sign off:** add `STATUS: APPROVED` or `STATUS: CHANGES NEEDED` at the top of each feedback file.

## Planner output format (`docs/team/plan/<lang>.md`)

Organise it by module, in teaching order. For every topic:

```text
### <topic_id> | <Title> | <Level> | status: existing-ok | existing-thin | rebuild | new
Summary: one line.
Lesson must cover: bullet list of subtopics.
Problems (n):
1. <Title> [Easy|Medium|Hard]: the idea or pattern it trains, in one line.
...
```

Reuse existing topic ids where they fit (see `content/<lang>/curriculum.csv`). A new id must be unique and kebab-case with the language prefix (`cpp-`, `py-`, `c-`).

## Language notes (added by the Head after the plans were written)

**Python specs:**

- Put `lang: python` in the meta section.
- The judge appends the driver to the learner's file, so the starter and solution must not contain `if __name__ == "__main__"` or `from __future__`.
- The judge environment has numpy, pandas, scipy, scikit-learn, torch (CPU), opencv, matplotlib (Agg backend), fastapi, starlette, flask, django, sqlalchemy, pydantic, httpx, requests, click and typer. pint, hypothesis, alembic, celery, redis and DRF are NOT available, so teach those concepts and have learners build small versions themselves.
- **Web problems must run in one process with no network.** Use the framework test clients (Flask `test_client`, FastAPI/Starlette `TestClient`, Django's test `Client` with `settings.configure(...)` and in-memory SQLite inside the file), or `httpx.MockTransport`, or `socket.socketpair()`.
- **Plots:** inspect the matplotlib Figure/Axes objects (data, labels, limits). Never compare images.
- **Topping up an existing topic** (status existing-thin): keep the existing problem files untouched. Add your new problems with `order:` values after the existing ones, and read the existing lesson. Improve the lesson only where it's thin or missing what your new problems need.
- **Speed:** Python problems with heavy imports (torch, sklearn) need `time_limit: 5` or more, and the reference must still use under 30% of it.

**C specs:** put `lang: c` in the meta section. C17, so POSIX functions need `#define _POSIX_C_SOURCE 200809L` at the top of the starter/solution (not the driver).

**Plans:** `docs/team/plan/<lang>.md` is the authoritative list of topics, statuses and problems. Follow your entries. You may improve a problem idea if it makes it a better exercise, but say so in your report.

## Skills every agent loads first (Skill tool)

Before any work, invoke these skills with the Skill tool and follow them:

| Role | Skills |
|---|---|
| All agents | `superpowers:verification-before-completion` (evidence before claiming that anything works) |
| Authors | `superpowers:test-driven-development` (the brute force and the stress test come first, and the reference must pass them), `superpowers:systematic-debugging` (whenever a build or validation fails), `superpowers:receiving-code-review` (when acting on files in `docs/team/feedback/`) |
| Reviewer | `superpowers:requesting-code-review`, `caveman:surgical-patch` (smallest correct fix), `superpowers:systematic-debugging` |
| Web-facing lessons (Python web modules) | read `impeccable` / `ui-ux-pro-max:ui-ux-pro-max` only when a problem involves HTML templates or UI output |

Also read `docs/team/feedback/GUIDELINES.md` (the Reviewer's rules) before writing new content.

## Resource limits on this laptop

The laptop has 16 cores but only about 6 GB of free RAM while the user works.

- **At most 3 agents run at once:** 2 Authors and 1 Reviewer. The Head enforces this.
- **Validation:** always run `JUDGE_WORKERS=2 JUDGE_WAIT=100000 python3 tools/validate.py <lang> <problem-id>`, one problem at a time. Never validate a whole language while other agents are running.
- **Big tests:** keep each generated input ≤ 10⁶ numbers, and reference memory well under 500 MB.
- **Builds:** don't run more than one `build_problem.py` at a time per agent.
