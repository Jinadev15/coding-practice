---
id: py-telemetry-cli
title: A Well-Behaved Telemetry CLI
difficulty: Medium
order: 1
tags: argparse, subcommands, exit codes, stdin, stderr, CLI testing
time_limit: 5
---
## Statement
Build the `telem` command-line tool with **argparse**. Implement `build_parser()` and `main(argv=None) -> int`. Don't add an `if __name__ == "__main__"` block: the judge appends its own code to your file, and calls `main([...])` directly and captures stdout, stderr and exit codes.

Log files contain lines `t,channel,value` (a float time, a name, a float value). Blank lines and lines starting with `#` are skipped. `FILE` may be `-`, meaning stdin.

**`telem stats FILE [--channel NAME] [--format text|json]`**
- Per channel, sorted by name: count, min, max and mean.
- Text output, one line per channel: `imu: n=3 min=1.000 max=4.000 mean=2.500`.
- JSON output: `json.dumps({name: {"n": .., "min": .., "max": .., "mean": ..}}, sort_keys=True)`, with the mean rounded to 6 decimals.
- `--channel` restricts the output to one channel.

**`telem filter FILE --min V [--max V] [--channel NAME]`**
- Prints the matching lines **exactly as they appear in the file** (stripped of surrounding whitespace), where `min <= value <= max`.
- Exit code 0 if anything matched, **1 if nothing did** (like `grep`).
- `--min` and `--max` must be finite floats. Use a custom `type=`, so `nan`, `inf` or `abc` are argparse usage errors.

**Global**
- `--version` prints `telem 1.0` and exits 0.
- A missing subcommand, missing arguments or bad option values are usage errors: argparse's own `SystemExit(2)`.

**Runtime errors** print to **stderr**, starting `telem: error: `, and return 1 (no traceback):
- An unreadable file gives `telem: error: cannot read FILE`.
- A malformed record (wrong field count, or a non-numeric time or value) gives `telem: error: line N: bad record` (1-based line number).
- `--channel X` with no data for X gives `telem: error: no data for channel X`.

Successful commands write nothing to stderr.

## Starter
```python
import argparse
import json
import sys


def build_parser():
    p = argparse.ArgumentParser(prog="telem")
    p.add_argument("command")
    p.add_argument("file")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    for line in open(args.file):
        print(line)
    return 0
```

## Driver
```python
import contextlib, io, os, tempfile

tmp = tempfile.mkdtemp()
def write(name, text):
    path = os.path.join(tmp, name)
    with open(path, "w") as f:
        f.write(text)
    return path

good = write("good.log", "# flight 7\n0.0,imu,1.5\n0.1,gps,10\n\n0.2,imu,-2.25\n0.3,imu,4\n 0.4,gps,12.5 \n0.5,baro,1013.2\n")
bad = write("bad.log", "0.0,imu,1\n0.1,imu\n")
bad2 = write("bad2.log", "0.0,imu,1\n# c\n0.2,imu,x\n")

def run(argv, stdin_text=None):
    out, err = io.StringIO(), io.StringIO()
    old = sys.stdin
    if stdin_text is not None:
        sys.stdin = io.StringIO(stdin_text)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main(argv)
            except SystemExit as e:
                code = ("exit", e.code)
    finally:
        sys.stdin = old
    return code, out.getvalue(), err.getvalue()

def show(label, argv, stdin_text=None, usage=False):
    code, out, err = run(argv, stdin_text)
    print(f"== {label}: code={code}")
    if out:
        print(out.rstrip("\n"))
    if err:
        print("stderr:", "(usage message)" if usage else err.strip().replace(tmp, "TMP"))

for cmd in sys.stdin.read().split():
    if cmd == "stats":
        show("stats text", ["stats", good])
        show("stats json", ["stats", good, "--format", "json"])
        show("stats channel", ["stats", good, "--channel", "gps"])
        show("stats stdin", ["stats", "-", "--channel", "imu"], stdin_text="1,imu,2\n2,imu,3\n3,gps,9\n")
    elif cmd == "filter":
        show("filter range", ["filter", good, "--min", "1", "--max", "12.5"])
        show("filter channel", ["filter", good, "--min", "-5", "--channel", "imu"])
        show("filter none", ["filter", good, "--min", "5000"])
    elif cmd == "errors":
        show("missing file", ["stats", os.path.join(tmp, "nope.log")])
        show("bad record", ["stats", bad])
        show("bad value", ["filter", bad2, "--min", "0"])
        show("no channel", ["stats", good, "--channel", "lidar"])
    elif cmd == "usage":
        show("version", ["--version"])
        show("no command", [], usage=True)
        show("missing --min", ["filter", good], usage=True)
        show("nan min", ["filter", good, "--min", "nan"], usage=True)
        show("inf max", ["filter", good, "--min", "0", "--max", "inf"], usage=True)
        show("bad format", ["stats", good, "--format", "xml"], usage=True)
    elif cmd == "big":
        lines = ["# big"] + [f"{i * 0.01:.2f},ch{i % 7},{(i * 37) % 1000 / 10}" for i in range(200000)]
        path = write("big.log", "\n".join(lines) + "\n")
        code, out, err = run(["stats", path, "--format", "json"])
        print("big stats", code, len(json.loads(out)), json.loads(out)["ch3"], repr(err))
        code, out, err = run(["filter", path, "--min", "99.5", "--channel", "ch0"])
        print("big filter", code, len(out.splitlines()), out.splitlines()[:2])
```

## Tests
=== sample
stats
usage
---
== stats text: code=0
baro: n=1 min=1013.200 max=1013.200 mean=1013.200
gps: n=2 min=10.000 max=12.500 mean=11.250
imu: n=3 min=-2.250 max=4.000 mean=1.083
== stats json: code=0
{"baro": {"max": 1013.2, "mean": 1013.2, "min": 1013.2, "n": 1}, "gps": {"max": 12.5, "mean": 11.25, "min": 10.0, "n": 2}, "imu": {"max": 4.0, "mean": 1.083333, "min": -2.25, "n": 3}}
== stats channel: code=0
gps: n=2 min=10.000 max=12.500 mean=11.250
== stats stdin: code=0
imu: n=2 min=2.000 max=3.000 mean=2.500
== version: code=('exit', 0)
telem 1.0
== no command: code=('exit', 2)
stderr: (usage message)
== missing --min: code=('exit', 2)
stderr: (usage message)
== nan min: code=('exit', 2)
stderr: (usage message)
== inf max: code=('exit', 2)
stderr: (usage message)
== bad format: code=('exit', 2)
stderr: (usage message)
=== hidden
filter
---
== filter range: code=0
0.0,imu,1.5
0.1,gps,10
0.3,imu,4
0.4,gps,12.5
== filter channel: code=0
0.0,imu,1.5
0.2,imu,-2.25
0.3,imu,4
== filter none: code=1
=== hidden
errors
---
== missing file: code=1
stderr: telem: error: cannot read TMP/nope.log
== bad record: code=1
stderr: telem: error: line 2: bad record
== bad value: code=1
stderr: telem: error: line 3: bad record
== no channel: code=1
stderr: telem: error: no data for channel lidar
=== hidden
big
---
big stats 0 7 {'max': 99.9, 'mean': 49.95536, 'min': 0.0, 'n': 28571} ''
big filter 0 142 ['21.35,ch0,99.5', '31.08,ch0,99.6']

## Hints
- `sub = p.add_subparsers(dest="command", required=True)`. Give each subparser `set_defaults(func=...)`.
- A finite-float type: convert with `float()`, then reject `math.isnan`/`math.isinf` by raising `argparse.ArgumentTypeError`.
- Parse the file once into `[(lineno, raw_line, t, channel, value)]`, raising a small private exception on a bad record. `main` catches it and prints to stderr.
- `open_input = sys.stdin if path == "-" else open(path)`. Catch `OSError` for unreadable files.

## Solution
```python
import argparse
import json
import math
import sys


class CliError(Exception):
    pass


def finite_float(text):
    try:
        v = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from None
    if math.isnan(v) or math.isinf(v):
        raise argparse.ArgumentTypeError(f"must be finite: {text!r}")
    return v


def build_parser():
    p = argparse.ArgumentParser(prog="telem", description="Robot telemetry log tool.")
    p.add_argument("--version", action="version", version="%(prog)s 1.0")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("stats", help="per-channel statistics")
    s.add_argument("file", help="log file, or - for stdin")
    s.add_argument("--channel")
    s.add_argument("--format", choices=["text", "json"], default="text")
    s.set_defaults(func=cmd_stats)

    f = sub.add_parser("filter", help="print records within a value range")
    f.add_argument("file")
    f.add_argument("--min", type=finite_float, required=True)
    f.add_argument("--max", type=finite_float, default=math.inf)
    f.add_argument("--channel")
    f.set_defaults(func=cmd_filter)
    return p


def read_records(path):
    try:
        stream = sys.stdin if path == "-" else open(path, encoding="utf-8")
    except OSError:
        raise CliError(f"cannot read {path}") from None
    records = []
    with stream:
        for lineno, raw in enumerate(stream, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            try:
                if len(parts) != 3:
                    raise ValueError
                t, value = float(parts[0]), float(parts[2])
            except ValueError:
                raise CliError(f"line {lineno}: bad record") from None
            records.append((line, t, parts[1].strip(), value))
    return records


def cmd_stats(args):
    groups = {}
    for _, _, ch, v in read_records(args.file):
        if args.channel is None or ch == args.channel:
            groups.setdefault(ch, []).append(v)
    if args.channel is not None and not groups:
        raise CliError(f"no data for channel {args.channel}")
    stats = {ch: {"n": len(vs), "min": min(vs), "max": max(vs), "mean": round(sum(vs) / len(vs), 6)}
             for ch, vs in sorted(groups.items())}
    if args.format == "json":
        print(json.dumps(stats, sort_keys=True))
    else:
        for ch, s in stats.items():
            print(f"{ch}: n={s['n']} min={s['min']:.3f} max={s['max']:.3f} mean={s['mean']:.3f}")
    return 0


def cmd_filter(args):
    matched = 0
    for line, _, ch, v in read_records(args.file):
        if (args.channel is None or ch == args.channel) and args.min <= v <= args.max:
            print(line)
            matched += 1
    return 0 if matched else 1


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except CliError as e:
        print(f"telem: error: {e}", file=sys.stderr)
        return 1

# In a real tool: if __name__ == "__main__": raise SystemExit(main())
# (left out here because the judge appends its driver to this file)
```

- **Subparsers with `set_defaults(func=...)`** dispatch without an if/elif chain, and `required=True` turns a missing subcommand into a proper usage error (exit 2).
- **A custom `type=`** puts validation inside argparse, so `--min nan` gets a standard usage message instead of a traceback later.
- **Two error channels**: usage errors are argparse's `SystemExit(2)`. Runtime errors are a private `CliError`, converted in exactly one place into a stderr message and exit code 1.
- **`main(argv) -> int`** keeps the CLI testable in-process. The real entry point is just `raise SystemExit(main())`.
- **grep-style exit codes** (1 when nothing matched) let shell scripts write `telem filter log --min 90 && alert`.
