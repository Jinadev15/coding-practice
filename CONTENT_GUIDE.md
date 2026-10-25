# Content Guide — adding languages, topics and questions

Everything you study lives in `content/`. The app reads these files on every request
(it notices changes automatically), so you never touch Python or JavaScript to add material.
After editing, run the validator:

```bash
python3 tools/validate.py            # all languages
python3 tools/validate.py python     # one language
```

It checks CSV structure and MCQ answers, and **runs every reference solution against its own
tests** (it must pass 100%, and the starter code must not).

```
content/
  <language-id>/                 e.g. python, c, cpp, java, rust ...
    language.json                how to compile/run code in this language
    curriculum.csv               the ordered topic list
    lessons/<topic_id>.md        one lesson per topic (Markdown)
    mcq/*.csv                    any number of MCQ files; every CSV in the folder is loaded
    problems/<topic_id>/*.md     coding problems for that topic
    problems/milestone-1/*.md    special quiz 1 (unlocks at 25% of topics)
    problems/milestone-2/*.md    special quiz 2 (50%)
    problems/milestone-3/*.md    special quiz 3 (75%)
    problems/milestone-4/*.md    special quiz 4 (100%)
```

## 1. Adding a new language

Create `content/<id>/language.json`. Examples:

```json
{
  "name": "Java", "order": 4, "color": "#e76f00", "icon": "Jv",
  "ext": "java", "main": "Main.java", "source_ext": [".java"],
  "editor_mode": "text/x-java",
  "compile": ["javac", "{sources}"],
  "run": ["java", "Main"],
  "time_limit": 2, "memory_mb": 0
}
```

| Key | Meaning |
|---|---|
| `compile` | Command run once per submission (omit or `null` for interpreted languages). `{sources}` expands to every file ending in `source_ext`. |
| `run` | Command run once per test, with the test input on stdin. `{python}` is the interpreter running the app; `{main}` is the main file name. |
| `main` | The file name shown in the editor for single-file problems. |
| `editor_mode` | A CodeMirror 5 mode or MIME type (`python`, `text/x-csrc`, `text/x-c++src`, `text/x-java`). Add the matching mode file to `static/vendor/cm/mode/` and `index.html` if it is not one of the bundled modes. |
| `memory_mb` | Address-space limit per run. Use `0` for JVM-based languages (the JVM reserves a lot of virtual memory up front). |

## 2. curriculum.csv

```csv
order,module,topic_id,title,level,summary
1,01 Foundations,py-how-python-runs,How Python Runs Your Code,Beginner,"One-line summary."
```

- `order` sets the sequence (decimals are fine for inserting: `10.5`).
- `module` groups topics; the leading number keeps modules sorted and is hidden in the UI.
- `level`: `Beginner`, `Intermediate`, `Advanced`, `Expert`, or `Research`.
- `topic_id` must be unique. Lessons, MCQs and problems refer to it.

A topic with no lesson, MCQs or problems shows as "Coming soon".

## 3. Lessons — `lessons/<topic_id>.md`

Standard Markdown (GitHub flavour) plus:

- **Code blocks** with a language tag are syntax-highlighted. Use ` ```output ` for program output.
- **Diagrams**: a ` ```mermaid ` block renders flowcharts, sequence diagrams, class diagrams (UML) and more.
- **Inline SVG/HTML** is allowed. Wrap figures as `<div class="figure"><svg>…</svg><figcaption>…</figcaption></div>`.
- **Callouts**: start a blockquote with a tag:

```markdown
> [!EXAM]
> Exam-ready answer you could write word for word.

> [!SYNTAX]
> The exact grammar of a construct.
```

Tags: `NOTE`, `TIP`, `KEY`, `WARNING`, `DANGER` (common mistake), `EXAM`, `DEFINITION`, `INTERVIEW`, `SYNTAX`.
Put a short custom title on the first line after the tag if you like: `> [!TIP] Faster input`.

## 4. MCQs — `mcq/*.csv`

```csv
id,topic,difficulty,type,question,code,option_a,option_b,option_c,option_d,answer,explanation
```

| Column | Notes |
|---|---|
| `id` | Unique across the language. |
| `topic` | A `topic_id` from the curriculum. |
| `difficulty` | `Easy`, `Medium`, `Hard`, `Expert`. |
| `type` | `theory`, `code` or `output` (shown as a label). |
| `question`, `explanation`, options | Markdown is allowed (`` `code` ``, **bold**). |
| `code` | Optional code snippet shown under the question. Real newlines inside the quoted cell work. |
| `option_a`…`option_f` | 2–6 options. |
| `answer` | Letter(s): `B`, or `A|C` for multiple correct answers (shown as "select all that apply"). |

Options are shuffled every attempt, so never write "both A and B". Any spreadsheet program
can edit these files; save as CSV (UTF-8).

## 5. Coding problems — `problems/<topic_id>/<anything>.md`

~~~~markdown
---
id: py-two-sum            (unique within the language)
title: Two Sum
difficulty: Easy          (Easy | Medium | Hard | Expert)
order: 1                  (position within the topic)
tags: arrays, hashing
time_limit: 2             (seconds per test; optional)
compare: lines            (lines | tokens | float | unordered | exact; optional)
libs: eigen, opencv       (C/C++ only, optional: libraries from language.json "libs")
---
## Statement
Markdown problem statement, constraints, examples.

## Starter
```python
def two_sum(nums, target):
    pass
```

## Driver
```python
# Hidden code appended after the user's main file: reads stdin, calls the
# function, prints the result. Omit this section for "write the whole program" problems.
n = int(input()); nums = list(map(int, input().split())); t = int(input())
print(*two_sum(nums, t))
```

## Tests
=== sample
4
2 7 11 15
9
---
0 1
=== hidden
...input...
---
...expected output...

## Hints
- First hint
- Second hint

## Solution
Explanation in Markdown with the reference code in a fenced block.
~~~~

- Each test starts with `=== sample` (shown to you) or `=== hidden`. Input comes first, then a `---` line, then the expected output.
- **If you leave out `---` and the output**, the judge computes the expected output by running the reference solution. That is handy for big generated tests.
- **Multi-file problems** (OOP projects): use several `## Starter: filename` sections, one per file. The reference implementation goes in `## Solution: filename` sections. A hidden helper file can be supplied with `## Driver: filename`.
- Comparison modes: `lines` (default; trailing spaces ignored), `tokens` (any whitespace), `float` (tokens, numbers within 1e-6), `unordered` (line order ignored), `exact`.

## 6. Scoring rules (for reference)

- Topic quiz: 10 questions per attempt, pass at 70%.
- Coding problem: the solution unlocks at ≥ 75% of tests passed. The problem is **completed** only at 100%.
- A topic is complete when its quiz is passed and all its problems are completed (or, for a lesson-only topic, when the lesson is marked studied).
- Special quizzes unlock at 25%, 50%, 75% and 100% of the language's topics complete.

## Libraries in problems

- **Python** submissions run in `.venv-judge` (created by `tools/setup_judge_env.sh` from `requirements-judge.txt`):
  NumPy, pandas, SciPy, Matplotlib, scikit-learn, PyTorch (CPU), OpenCV, pytest, requests, httpx, FastAPI, Flask, Django,
  SQLAlchemy, Click, Typer, and `rclpy` when ROS 2 is installed.
- **C/C++** problems list the libraries they link in the front matter, e.g. `libs: eigen, gtest`. Each name maps to an entry in the
  language's `language.json` `"libs"`: `{"pkg": "<pkg-config name>"}`, explicit `{"cflags": [...], "ldflags": [...]}`, or
  `{"cache": "rclcpp"}` for flags recorded by `tools/setup_cpp_libs.py` (ROS 2 only ships CMake packages). The flags are
  substituted for `{lib_cflags}` and `{lib_ldflags}` in the compile command.
- Available C++ names: `eigen`, `opencv`, `gtest`, `gmock`, `fmt`, `spdlog`, `boost` (header-only parts), `json` (nlohmann), `rclcpp`.
