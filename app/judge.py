"""Compiles and runs submissions locally against a problem's tests.

How to build and run a language comes entirely from its language.json, so a new
language needs no change here.
"""
from __future__ import annotations

import json
import math
import os
import resource
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from .content import Language, Problem

MAX_OUT = 64_000           # stderr / compiler messages
MAX_STDOUT = 32_000_000   # program output kept for comparison (big tests print MBs)
_expected_cache: dict[tuple[str, float], list[str]] = {}

# Python submissions run in the isolated environment created by tools/setup_judge_env.sh
# (NumPy, pandas, SciPy, scikit-learn, PyTorch, OpenCV, ...); fall back to the server's interpreter.
_JUDGE_VENV_PY = Path(__file__).resolve().parent.parent / ".venv-judge" / "bin" / "python"
PYTHON = os.environ.get("JUDGE_PYTHON") or (str(_JUDGE_VENV_PY) if _JUDGE_VENV_PY.exists() else sys.executable)
# Extra runtime variables recorded by the setup script (e.g. ROS 2 library paths).
_JUDGE_ENV_FILE = _JUDGE_VENV_PY.parent.parent / "judge_env.json"
PY_EXTRA_ENV: dict[str, str] = {}
if PYTHON == str(_JUDGE_VENV_PY) and _JUDGE_ENV_FILE.exists():
    import json as _json
    PY_EXTRA_ENV = _json.loads(_JUDGE_ENV_FILE.read_text())


# ------------------------------------------------------------------ sandbox
# When the app is shared (server.py --multi-user), every compile and run goes through bubblewrap:
# no network, its own PID namespace, a read-only view of the system toolchains only (the repository,
# reference solutions and progress databases are not visible), and a writable temp workspace.
SANDBOX = os.environ.get("JUDGE_SANDBOX", "auto")     # "on" | "off" | "auto" (on when bwrap works)
_RO_DIRS = ["/usr", "/etc", "/opt"]


def _bwrap_prefix(workdir: Path) -> list[str]:
    cmd = ["bwrap", "--unshare-all", "--die-with-parent", "--new-session",
           "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]
    for d in _RO_DIRS:
        if os.path.isdir(d):
            cmd += ["--ro-bind", d, d]
    for top in ("bin", "lib", "lib64", "sbin"):
        p = Path("/" + top)
        if p.is_symlink():
            cmd += ["--symlink", os.readlink(p), str(p)]
        elif p.is_dir():
            cmd += ["--ro-bind", str(p), str(p)]
    venv = _JUDGE_VENV_PY.parent.parent
    if venv.is_dir():
        cmd += ["--ro-bind", str(venv), str(venv)]
        # A uv-managed interpreter lives outside /usr (~/.local/share/uv/python/cpython-X/...), reached through
        # version symlinks: expose the whole folder of managed interpreters so every hop resolves.
        base = Path(os.path.realpath(_JUDGE_VENV_PY)).parent.parent
        if not any(str(base).startswith(d + "/") for d in _RO_DIRS):
            cmd += ["--ro-bind", str(base.parent), str(base.parent)]
    return cmd + ["--bind", str(workdir), str(workdir), "--chdir", str(workdir), "--"]


def _sandbox_works() -> bool:
    if not shutil.which("bwrap"):
        return False
    with tempfile.TemporaryDirectory(prefix="cp-probe-") as d:
        try:
            r = subprocess.run(_bwrap_prefix(Path(d)) + ["true"], capture_output=True, timeout=10)
            return r.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False


def sandbox_enabled() -> bool:
    global SANDBOX
    if SANDBOX == "auto":
        SANDBOX = "on" if _sandbox_works() else "off"
    return SANDBOX == "on"


def _user_procs() -> int:
    uid, n = os.getuid(), 0
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                if os.stat(f"/proc/{d}").st_uid == uid:
                    n += len(os.listdir(f"/proc/{d}/task"))
            except OSError:
                pass
    return n


def _limits(mem_mb: int, cpu_s: int):
    # RLIMIT_NPROC counts every thread of this Unix user, so allow headroom above what is running now:
    # enough for thread pools, not enough for a fork bomb to take the machine down.
    nproc = _user_procs() + 512 if SANDBOX == "on" else None
    def apply():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s + 1))
        if mem_mb:
            b = mem_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (b, b))
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_STDOUT, MAX_STDOUT))
        if nproc:
            resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
    return apply


_LIB_CACHE_FILE = Path(__file__).resolve().parent.parent / ".cache" / "cpp_libs.json"
_lib_memo: dict[tuple[str, str], tuple[list[str], list[str], dict[str, str]]] = {}


def resolve_libs(lang: Language, names: list[str]) -> tuple[list[str], list[str], dict[str, str]]:
    """Compile flags, link flags and runtime env for the libraries a problem requests (front matter `libs:`).

    language.json maps each name to {"pkg": "<pkg-config name>"}, {"cflags": [...], "ldflags": [...]}
    or {"cache": "<key>"} (flags recorded by tools/setup_cpp_libs.py, e.g. ROS 2's rclcpp)."""
    cflags: list[str] = []
    ldflags: list[str] = []
    env: dict[str, str] = {}
    registry = lang.config.get("libs", {})
    for name in names:
        key = (lang.id, name)
        if key not in _lib_memo:
            spec = registry.get(name)
            if spec is None:
                raise RuntimeError(f"unknown library '{name}' (add it to {lang.id}/language.json)")
            c, l, e = list(spec.get("cflags", [])), list(spec.get("ldflags", [])), dict(spec.get("env", {}))
            if "pkg" in spec:
                r = subprocess.run(["pkg-config", "--cflags", "--libs", spec["pkg"]], capture_output=True, text=True)
                if r.returncode != 0:
                    raise RuntimeError(f"pkg-config can't find '{spec['pkg']}': {r.stderr.strip()}")
                for flag in r.stdout.split():
                    if flag.startswith(("-l", "-L", "-Wl")):
                        l.append(flag)
                    elif flag.startswith("-I"):
                        c += ["-isystem", flag[2:]]      # third-party headers: no warnings in the user's output
                    else:
                        c.append(flag)
            if "cache" in spec:
                cache = json.loads(_LIB_CACHE_FILE.read_text()) if _LIB_CACHE_FILE.exists() else {}
                if spec["cache"] not in cache:
                    raise RuntimeError(f"library '{name}' isn't set up: run tools/setup_cpp_libs.py")
                entry = cache[spec["cache"]]
                c += entry["cflags"]; l += entry["ldflags"]; e.update(entry.get("env", {}))
            _lib_memo[key] = (c, l, e)
        c, l, e = _lib_memo[key]
        cflags += c; ldflags += l; env.update(e)
    return cflags, ldflags, env


def _expand(cmd: list[str], sources: list[str], main: str, cflags: list[str] | None = None,
            ldflags: list[str] | None = None) -> list[str]:
    out: list[str] = []
    for part in cmd:
        if part == "{sources}":
            out.extend(sources)
        elif part == "{lib_cflags}":
            out.extend(cflags or [])
        elif part == "{lib_ldflags}":
            out.extend(ldflags or [])
        else:
            out.append(part.replace("{main}", main).replace("{python}", PYTHON))
    return out


def build_files(lang: Language, problem: Problem, user_files: dict[str, str]) -> dict[str, str]:
    """User files plus the problem's hidden driver code."""
    main = lang.config.get("main", "main.txt")
    files = dict(user_files)
    for name, code in problem.drivers.items():
        if not name:
            files[main] = files.get(main, "") + "\n\n" + code + "\n"
        else:
            files[name] = code
    return files


def compare(got: str, expected: str, mode: str) -> bool:
    if mode == "exact":
        return got == expected
    g_lines = [l.rstrip() for l in got.rstrip().splitlines()]
    e_lines = [l.rstrip() for l in expected.rstrip().splitlines()]
    if mode == "unordered":
        return sorted(g_lines) == sorted(e_lines)
    if mode in ("tokens", "float"):
        g, e = got.split(), expected.split()
        if len(g) != len(e):
            return False
        for a, b in zip(g, e):
            if a == b:
                continue
            if mode != "float":
                return False
            try:
                fa, fb = float(a), float(b)
            except ValueError:
                return False
            if not math.isclose(fa, fb, rel_tol=1e-6, abs_tol=1e-6):
                return False
        return True
    return g_lines == e_lines


class Workspace:
    def __init__(self, lang: Language, files: dict[str, str], libs: list[str] | None = None):
        self.lang, self.files = lang, files
        self.cflags, self.ldflags, self.lib_env = resolve_libs(lang, libs or [])
        self.dir = Path(tempfile.mkdtemp(prefix="cp-judge-"))
        for name, code in files.items():
            dest = (self.dir / name).resolve()
            if self.dir.resolve() not in dest.parents:
                raise ValueError(f"bad file name {name}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(code, encoding="utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _wrap(self, cmd: list[str]) -> list[str]:
        return _bwrap_prefix(self.dir) + cmd if sandbox_enabled() else cmd

    def compile(self) -> tuple[bool, str]:
        cfg = self.lang.config
        cmd = cfg.get("compile")
        if not cmd:
            return True, ""
        exts = tuple(cfg.get("source_ext", ["." + cfg.get("ext", "")]))
        sources = sorted(n for n in self.files if n.endswith(exts))
        try:
            r = subprocess.run(
                self._wrap(_expand(cmd, sources, cfg.get("main", ""), self.cflags, self.ldflags)), cwd=self.dir,
                capture_output=True,
                text=True, timeout=cfg.get("compile_timeout", 30),
                preexec_fn=_limits(0, cfg.get("compile_timeout", 30)),
            )
        except subprocess.TimeoutExpired:
            return False, "Compilation timed out."
        msg = (r.stderr + r.stdout).replace(str(self.dir) + "/", "")
        return r.returncode == 0, msg[:MAX_OUT]

    def run(self, stdin: str, time_limit: float) -> dict:
        cfg = self.lang.config
        cmd = self._wrap(_expand(cfg["run"], [], cfg.get("main", "")))
        start = time.perf_counter()
        # Output goes to files, not pipes: RLIMIT_FSIZE then caps how much a runaway program can print,
        # instead of the server buffering gigabytes in memory.
        out_f = tempfile.TemporaryFile()
        err_f = tempfile.TemporaryFile()

        def read(f, cap):
            f.seek(0)
            return f.read(cap).decode("utf-8", errors="replace").replace("\r\n", "\n")
        try:
            r = subprocess.run(
                cmd, cwd=self.dir, input=stdin.encode(), stdout=out_f, stderr=err_f,
                timeout=time_limit + 0.5,
                preexec_fn=_limits(cfg.get("memory_mb", 512), math.ceil(time_limit) + 1),
                env={"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0",
                     "PYTHONIOENCODING": "utf-8", "LANG": "C.UTF-8", "HOME": str(self.dir),
                     # glibc reserves a 64 MB malloc arena per thread; under RLIMIT_AS that makes threaded
                     # programs (OpenCV, BLAS, std::thread pools) fail randomly with bad_alloc
                     "MALLOC_ARENA_MAX": "2",
                     **(PY_EXTRA_ENV if "{python}" in cfg["run"] else {}),
                     # each run gets its own DDS domain so parallel ROS 2 tests can't see each other
                     "ROS_DOMAIN_ID": str(1 + (os.getpid() + int(time.time() * 1000)) % 100),
                     **self.lib_env,
                     **cfg.get("env", {})},
            )
        except subprocess.TimeoutExpired:
            with out_f, err_f:
                return {"status": "TLE", "stdout": read(out_f, MAX_STDOUT), "stderr": "Time limit exceeded",
                        "time_ms": int((time.perf_counter() - start) * 1000)}
        ms = int((time.perf_counter() - start) * 1000)
        with out_f, err_f:
            stdout, stderr = read(out_f, MAX_STDOUT), read(err_f, MAX_OUT)
        stderr = stderr.replace(str(self.dir) + "/", "")[:MAX_OUT]
        status = "OK"
        if r.returncode != 0:
            status = "TLE" if r.returncode in (-9, -24) else "RE"
            if r.returncode < 0 and not stderr:
                stderr = f"Killed by signal {-r.returncode}"
        if ms > time_limit * 1000 and status == "OK":
            status = "TLE"
        if r.returncode == -25:     # SIGXFSZ
            stderr = (stderr + "\nOutput limit exceeded (your program printed too much).").strip()
        return {"status": status, "stdout": stdout, "stderr": stderr, "time_ms": ms}


def problem_libs(problem: Problem) -> list[str]:
    raw = problem.meta.get("libs", "")
    return [x.strip() for x in raw.split(",") if x.strip()] if isinstance(raw, str) else list(raw)


def expected_outputs(lang: Language, problem: Problem) -> list[str]:
    """Expected output per test; tests without one are filled from the reference solution."""
    if all(t.output is not None for t in problem.tests):
        return [t.output for t in problem.tests]
    key = (f"{problem.lang}/{problem.id}", problem.path.stat().st_mtime)
    if key not in _expected_cache:
        if not problem.solution_files:
            raise RuntimeError("tests without expected output need a reference solution")
        files = build_files(lang, problem, problem.solution_files)
        outs = []
        with Workspace(lang, files, problem_libs(problem)) as ws:
            ok, msg = ws.compile()
            if not ok:
                raise RuntimeError("reference solution failed to compile:\n" + msg)
            for t in problem.tests:
                if t.output is not None:
                    outs.append(t.output)
                    continue
                r = ws.run(t.input, float(problem.meta.get("time_limit", 5)) * 3)
                if r["status"] != "OK":
                    raise RuntimeError(f"reference solution {r['status']}: {r['stderr']}")
                outs.append(r["stdout"])
        _expected_cache[key] = outs
    return _expected_cache[key]


# At most this many submissions compile/run at once; the rest wait their turn.
_slots = threading.BoundedSemaphore(int(os.environ.get("JUDGE_WORKERS", max(2, (os.cpu_count() or 4) // 2))))


def judge(lang: Language, problem: Problem, user_files: dict[str, str], samples_only=False,
          custom_input: str | None = None) -> dict:
    if not _slots.acquire(timeout=300):
        raise RuntimeError("The judge is busy. Please try again in a minute.")
    try:
        return _judge(lang, problem, user_files, samples_only, custom_input)
    finally:
        _slots.release()


def _judge(lang: Language, problem: Problem, user_files: dict[str, str], samples_only=False,
           custom_input: str | None = None) -> dict:
    files = build_files(lang, problem, user_files)
    tl = float(problem.meta.get("time_limit", lang.config.get("time_limit", 2)))
    mode = problem.meta.get("compare", "lines")
    with Workspace(lang, files, problem_libs(problem)) as ws:
        ok, msg = ws.compile()
        if not ok:
            return {"compiled": False, "compile_output": msg, "results": [], "passed": 0,
                    "total": len(problem.tests), "score": 0.0}
        if custom_input is not None:
            r = ws.run(custom_input, tl)
            return {"compiled": True, "compile_output": msg, "custom": r}
        expected = expected_outputs(lang, problem)
        results, shown_hidden = [], False
        for i, (t, exp) in enumerate(zip(problem.tests, expected)):
            if samples_only and not t.sample:
                continue
            r = ws.run(t.input, tl)
            passed = r["status"] == "OK" and compare(r["stdout"], exp, mode)
            if r["status"] == "OK" and not passed:
                r["status"] = "WA"
            item = {"index": i + 1, "sample": t.sample, "passed": passed,
                    "status": "AC" if passed else r["status"], "time_ms": r["time_ms"]}
            # Show samples fully, and the first failing hidden test so you can learn from it.
            if t.sample or (not passed and not shown_hidden):
                shown_hidden = shown_hidden or not t.sample
                item.update(input=t.input[:4000], expected=exp[:4000], got=r["stdout"][:4000],
                            stderr=r["stderr"][:4000])
            results.append(item)
    passed = sum(r["passed"] for r in results)
    total = len(results)
    return {"compiled": True, "compile_output": msg, "results": results, "passed": passed,
            "total": total, "score": passed / total if total else 0.0}
