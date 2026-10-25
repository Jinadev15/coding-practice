# Getting started on your own laptop

Coding Practice teaches Python, C and C++ from the basics up to robotics-level projects. Each topic has a lesson, a quiz and coding problems that are checked automatically. Everything runs on your own laptop. It's free, it works offline once installed, and your progress stays on your machine.

## 1. What you need

| Your laptop | What to do |
|---|---|
| **Linux** (Ubuntu, Debian, Fedora, Arch) | Nothing extra. Go to step 2. |
| **Windows 10/11** | Install WSL first (below), then do everything inside the Ubuntu window. |
| **macOS** | Install [Homebrew](https://brew.sh) first. The C++ topics that need the newest standard may not compile with Apple's compiler. |

About 3 GB of free disk space is enough for everything.

**Windows: install WSL (one time).** Open PowerShell as Administrator and run:

```powershell
wsl --install -d Ubuntu
```

Restart when asked. Open **Ubuntu** from the Start menu, create a Linux username and password, and type every command below into that window. The app still opens in your normal Windows browser.

## 2. Install (one command)

```bash
git clone https://github.com/Jinadev15/coding-practice.git
cd coding-practice
./setup.sh
```

`setup.sh` does four things:

1. It installs whatever is missing: compilers (`gcc`/`g++`), the C++ libraries the advanced topics use (Eigen, OpenCV, GoogleTest, fmt, spdlog, Boost, nlohmann/json), and `bubblewrap` for the sandbox. This step asks for your password because it uses `sudo`.
2. It creates a private Python environment with NumPy, pandas, scikit-learn, PyTorch (CPU), OpenCV, FastAPI and the rest. If your Python is older than 3.14, it downloads 3.14 for this environment without touching your system Python. The first run downloads about 1 GB.
3. If ROS 2 is installed, it sets up the ROS 2 problems. Without ROS 2, only those few problems are unavailable.
4. It runs a self-test and tells you exactly what works.

If `git` itself is missing, install it first: `sudo apt install git` (Ubuntu/WSL), `sudo dnf install git` (Fedora) or `brew install git` (macOS).

**Short on disk space or on a slow connection?** Run `./setup.sh --minimal`. It installs only what the core Python, C and C++ topics need. You can run the full `./setup.sh` later.

## 3. Start it

```bash
python3 server.py
```

Your browser opens at **http://127.0.0.1:8765**. Leave the terminal open while you study, and press `Ctrl+C` to stop. Next time, just `cd coding-practice` and run `python3 server.py` again. On WSL, if the browser doesn't open by itself, paste the address into your Windows browser.

## 4. How to study

1. **Pick a language** on the dashboard, and start at the top of its curriculum. Topics build on each other.
2. **Read the lesson.** Every lesson explains the idea, shows worked examples with their real output, lists common mistakes, and ends with self-check questions (click *Answers* to reveal them). Press **Mark lesson as studied** when you're done.
3. **Take the topic quiz:** 10 questions, and 70% passes. Wrong answers come with an explanation.
4. **Solve the coding problems.** Type your solution yourself (paste is disabled on purpose, because typing is how you learn).
   - **Run** checks the sample tests. **Submit** runs all of them.
   - Stuck? Open the **hints** one at a time.
   - At **75%** of tests passed, the reference solution unlocks so you can compare. A problem counts as completed only at **100%**.
5. **Special quizzes** unlock at 25%, 50%, 75% and 100% of a language's topics. Each one has a **study guide** that teaches the new algorithms first. You can read it before the quiz unlocks.
6. The **sidebar target** and the **heatmap** track your daily progress. Set a deadline in *Settings* if you like.

## 5. Getting new lessons

When new content is added:

```bash
cd coding-practice
git pull
./setup.sh
```

Your progress lives in `data/`, which git never touches, so updating never loses it. To back it up, copy `data/progress.db`.

## 6. Your code is sandboxed

On Linux and WSL, every program you submit runs inside a `bubblewrap` sandbox. It has no network and no access to your files, and limits on time, memory and output stop an infinite loop or a runaway program from affecting your laptop. The setup self-test shows whether the sandbox is on.

## Troubleshooting

| Problem | Fix |
|---|---|
| `./setup.sh: Permission denied` | `bash setup.sh` |
| `Address already in use` | The app is already running in another terminal, or use `python3 server.py --port 9000` |
| C++ problems say a feature doesn't exist | Your g++ is older than 13. Ubuntu 24.04 or newer (or Fedora 39+) has a new enough one. |
| `sandbox: off` in the self-test | Install `bubblewrap`. On some systems unprivileged user namespaces are disabled, and the app still works without the sandbox. |
| Python problems with NumPy/PyTorch fail | Run `./setup.sh` without `--minimal` |
| Anything else | Run `./setup.sh` again. It is safe to repeat and shows what is missing. |
