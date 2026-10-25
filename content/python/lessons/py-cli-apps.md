# Command-Line Applications

Most engineering tools are command-line programs: `git`, `ros2`, `pytest`, `colcon`, data-processing scripts, robot calibration utilities. A good CLI parses its arguments robustly, prints helpful usage, reports errors on **stderr**, returns meaningful **exit codes**, composes with pipes, and is testable without spawning a process. This lesson covers `argparse` in depth (positionals, options, types, choices, mutually exclusive groups, subcommands), I/O conventions, exit codes and signals, configuration precedence, testing, and the third-party alternatives Click and Typer.

## 1. The anatomy of a well-behaved CLI

```text
$ telemetry stats --format json --since 10m flight.log
$ telemetry --help
$ cat flight.log | telemetry stats -          # "-" means stdin
$ echo $?                                      # 0 success, 1 failure, 2 usage error
```

| Convention | Why |
|---|---|
| Data on **stdout**, messages and errors on **stderr** | `cmd > out.json` keeps the output clean |
| Exit code 0 success, non-zero failure (2 for usage errors) | shells, `make`, CI and `&&` chains rely on it |
| `-h/--help` and `--version` | discoverability |
| Accept `-` for stdin/stdout | composes in pipelines |
| No interactive prompts unless attached to a TTY | scripts and cron jobs hang otherwise |
| Exit 130 on Ctrl-C, without a traceback | users expect quiet interruption |

## 2. argparse fundamentals

```python
import argparse

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="telemetry", description="Analyse robot telemetry logs.")
    p.add_argument("logfile", help="log file, or - for stdin")                       # positional
    p.add_argument("-n", "--limit", type=int, default=10, help="rows to show (default: %(default)s)")
    p.add_argument("--format", choices=["text", "json", "csv"], default="text")
    p.add_argument("-v", "--verbose", action="count", default=0, help="-v, -vv for more output")
    p.add_argument("--channels", nargs="+", metavar="NAME", help="one or more channel names")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--version", action="version", version="%(prog)s 2.1.0")
    return p

args = build_parser().parse_args(["flight.log", "-n", "5", "--channels", "imu", "gps", "-vv"])
print(args.logfile, args.limit, args.channels, args.verbose, args.dry_run)
```

```output
flight.log 5 ['imu', 'gps'] 2 False
```

- `--dry-run` becomes the attribute `args.dry_run`, because dashes turn into underscores.
- `type=` is any callable that converts a string, and it may raise `argparse.ArgumentTypeError` for a clean error message.
- On invalid input, argparse prints usage plus the error to stderr and raises `SystemExit(2)`.

**Custom validation types:**

```python
def positive_float(text: str) -> float:
    try:
        v = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from None
    if v <= 0:
        raise argparse.ArgumentTypeError(f"must be > 0, got {v}")
    return v

p.add_argument("--rate", type=positive_float, default=50.0)
```

**Mutually exclusive options:**

```python
g = p.add_mutually_exclusive_group()
g.add_argument("--quiet", action="store_true")
g.add_argument("--verbose", action="store_true")
```

## 3. Subcommands

Large tools (`git commit`, `ros2 topic echo`) use **subparsers**, each with its own arguments and handler:

```python
def cmd_stats(args) -> int: ...
def cmd_export(args) -> int: ...

def build_parser():
    p = argparse.ArgumentParser(prog="telemetry")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("stats", help="summary statistics")
    s.add_argument("logfile")
    s.set_defaults(func=cmd_stats)
    e = sub.add_parser("export", help="convert format")
    e.add_argument("logfile"); e.add_argument("-o", "--output", required=True)
    e.set_defaults(func=cmd_export)
    return p

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
```

> [!KEY]
> Write `main(argv=None) -> int` and call `raise SystemExit(main())`. Passing `argv` explicitly makes the CLI **testable** (`main(["stats", "x.log"])`), and returning an int keeps exit codes in one place. `parse_args(None)` reads `sys.argv[1:]`.

## 4. Input, output and errors

```python
import sys, json

def open_input(path: str):
    return sys.stdin if path == "-" else open(path, encoding="utf-8")

def cmd_stats(args) -> int:
    try:
        with open_input(args.logfile) as f:
            values = [float(line) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"telemetry: error: no such file: {args.logfile}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"telemetry: error: bad data: {e}", file=sys.stderr)
        return 1
    print(json.dumps({"n": len(values), "mean": sum(values) / len(values) if values else None}))
    return 0
```

The `with` statement would close `sys.stdin` too. That's harmless at the end of a CLI, but use `contextlib.nullcontext(sys.stdin)` in library code.

**Ctrl-C and broken pipes:**

```python
def run() -> int:
    try:
        return main()
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130                         # 128 + SIGINT(2), the shell convention
    except BrokenPipeError:                # `telemetry ... | head` closed the pipe early
        sys.stderr.close()
        return 0
```

## 5. Configuration precedence

The professional order, from lowest to highest priority, is **built-in defaults < config file < environment variables < command-line flags**:

```python
import os, tomllib
def load_settings(args) -> dict:
    cfg = {"rate": 50.0, "host": "localhost"}
    path = os.path.expanduser("~/.config/telemetry.toml")
    if os.path.exists(path):
        with open(path, "rb") as f: cfg.update(tomllib.load(f))
    if "TELEMETRY_HOST" in os.environ: cfg["host"] = os.environ["TELEMETRY_HOST"]
    if args.rate is not None: cfg["rate"] = args.rate        # use default=None to detect "not given"
    return cfg
```

## 6. Testing CLIs

```python
def test_stats_json(tmp_path, capsys):
    log = tmp_path / "a.log"; log.write_text("1\n2\n3\n")
    assert main(["stats", str(log)]) == 0
    out, err = capsys.readouterr()
    assert json.loads(out) == {"n": 3, "mean": 2.0} and err == ""

def test_usage_error(capsys):
    with pytest.raises(SystemExit) as e:
        main(["stats"])                       # missing positional
    assert e.value.code == 2
    assert "required" in capsys.readouterr().err
```

Without pytest, use `contextlib.redirect_stdout(io.StringIO())` and `redirect_stderr`. Run end-to-end tests with `subprocess.run([sys.executable, "-m", "telemetry", ...], capture_output=True, text=True)`.

## 7. Packaging an entry point

```toml
# pyproject.toml
[project.scripts]
telemetry = "telemetry.cli:run"
```

`pip install .` creates a `telemetry` executable that calls `run()`. A `__main__.py` lets users run `python -m telemetry`.

## 8. Click and Typer

```python
import typer
app = typer.Typer()

@app.command()
def stats(logfile: str, limit: int = 10, fmt: str = typer.Option("text", "--format")):
    """Summary statistics."""
    typer.echo(f"{logfile} {limit} {fmt}")

if __name__ == "__main__":
    app()
```

**Click** uses decorators (`@click.command()`, `@click.option`) and offers composable command groups, rich testing via `CliRunner`, and prompts. **Typer** builds on Click using **type hints**. argparse is in the standard library (no dependency, which matters for system tools and ROS 2 `ros2cli`). Click and Typer are more ergonomic for big tools.

> [!EXAM]
> **What makes a command-line program "well-behaved" and testable?**
> It writes data to stdout and diagnostics to stderr, returns 0 on success and non-zero on failure (2 for usage errors), supports `--help`, accepts `-` for stdin, never prompts when not on a TTY, and handles Ctrl-C (exit 130) and broken pipes quietly. Testability comes from a `main(argv) -> int` function that takes an explicit argument list and returns the exit code. Tests call it directly and capture the output (`capsys` or `redirect_stdout`), with the real entry point reduced to `raise SystemExit(main())`.
