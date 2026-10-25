# Coding Practice

A private, local study platform for Python, C and C++ (and any language you add later):
lessons → topic quizzes (MCQ) → hand-typed coding problems judged against test cases, with a
GitHub-style activity heatmap, per-language daily targets and four special quizzes per language.

## Run

```bash
python3 server.py
```

It opens http://127.0.0.1:8765. The server itself needs only Python 3.10+ (no packages), plus `gcc`/`g++` for C/C++ problems.
Options: `--port 9000`, `--no-browser`.

Python problems from the scientific and AI modules use NumPy, pandas, SciPy, Matplotlib, scikit-learn, PyTorch (CPU) and OpenCV.
Install them once into an isolated environment (needs [uv](https://docs.astral.sh/uv/)):

```bash
tools/setup_judge_env.sh
```

This creates `.venv-judge/` from `requirements-judge.txt`, and the judge uses it automatically for Python submissions
(override with `JUDGE_PYTHON=/path/to/python`). Native thread pools are pinned to one thread inside the judge,
so timings are stable and memory limits hold. If ROS 2 is installed under `/opt/ros/<distro>`, the setup
script also exposes `rclpy` and the message packages to the judge, and every run gets its own DDS domain.

## How it works

- **Study** a topic's lesson, or skip it if you already know the material, and mark it studied.
- **Quiz**: 10 MCQs per attempt (theory, code reading, output prediction). Pass at 70%.
- **Code**: type the solution yourself. Paste is disabled and there is no autocomplete. *Run* checks the samples; *Submit* runs every test.
  - ≥ 75% of tests passed → the reference solution unlocks.
  - Only 100% marks the problem **completed**. Until then it shows as *not completed*.
- **Special quizzes** unlock at 25 / 50 / 75 / 100% of a language's topics, with harder and bigger problems each time.
- **Today's target** (sidebar): computed per language from your last 14 days' pace (+10%), never below your daily minimum, or from a deadline you set in Settings.
- **Heatmap**: every lesson studied, MCQ answered and code submission counts toward the day's square.

## Layout

| Path | What |
|---|---|
| `content/` | All lessons, MCQs and problems as plain files. See [CONTENT_GUIDE.md](CONTENT_GUIDE.md). |
| `data/progress.db` | Your progress (SQLite). Back it up or commit it. |
| `server.py`, `app/` | Local server, content loader, judge, progress rules. |
| `static/` | The web UI (no build step; libraries vendored in `static/vendor`). |
| `tools/validate.py` | Checks content and proves every reference solution passes its tests. |

The judge runs your code directly on this machine with CPU-time, memory and output-size limits.
It is meant for your own code, not untrusted programs.
