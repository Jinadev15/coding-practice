---
id: py-threaded-pipeline
title: A Three-Stage Threaded Pipeline
difficulty: Medium
order: 1
tags: threading, queue, producer-consumer, sentinels, locks
time_limit: 3
---
## Statement
Build a **producer–consumer pipeline** with threads and `queue.Queue`:

```
reader → [raw queue] → N parser threads → [parsed queue] → 1 aggregator thread
```

```python
def run_pipeline(lines: list[str], parsers: int, fetch) -> dict
```

- The **reader** (it may be the calling thread) puts each line on the raw queue, then one sentinel `None` per parser.
- Each **parser** thread takes a line, calls `fetch(line)` (provided by the driver: it **sleeps** 0.05 s to simulate I/O and returns `(sensor, value)` or raises `ValueError` for bad lines), and puts the result (or an error marker) on the parsed queue. On its sentinel it puts its own "done" marker and exits.
- The **aggregator** collects results until it has seen all parsers' "done" markers, computing per-sensor `count`, `min`, `max` and `mean` (rounded to 2 decimals), plus the number of errors.
- Return `{"sensors": {name: (count, min, max, mean)}, "errors": E}`.

There are up to 40 lines. The time limit only passes if fetches actually overlap (40 × 0.05 s = 2 s sequentially). The driver counts how many threads you start.

## Starter
```python
import threading
import queue

def run_pipeline(lines, parsers, fetch):
    sensors = {}
    errors = 0
    for line in lines:
        try:
            name, value = fetch(line)
        except ValueError:
            errors += 1
            continue
        sensors.setdefault(name, []).append(value)
    return {"sensors": {k: (len(v), min(v), max(v), round(sum(v) / len(v), 2)) for k, v in sensors.items()},
            "errors": errors}
```

## Driver
```python
import sys
import time

started = 0
_orig_start = threading.Thread.start
def _counting_start(self, *a, **k):
    global started
    started += 1
    return _orig_start(self, *a, **k)
threading.Thread.start = _counting_start

def fetch(line):
    time.sleep(0.05)
    name, sep, value = line.partition("=")
    if not sep:
        raise ValueError(line)
    return name.strip(), float(value)

data = sys.stdin.read().split("\n")
parsers = int(data[0])
lines = [l for l in data[1:] if l.strip()]
t0 = time.perf_counter()
res = run_pipeline(lines, parsers, fetch)
for name in sorted(res["sensors"]):
    c, lo, hi, mean = res["sensors"][name]
    print(f"{name}: n={c} min={lo:g} max={hi:g} mean={mean:g}")
print("errors", res["errors"])
print("threads started >= parsers:", started >= parsers)
print("alive after return:", threading.active_count() - 1)
```

## Tests
=== sample
4
imu=1.5
lidar=10
imu=2.5
bogus
lidar=4
gps=0
---
gps: n=1 min=0 max=0 mean=0
imu: n=2 min=1.5 max=2.5 mean=2
lidar: n=2 min=4 max=10 mean=7
errors 1
threads started >= parsers: True
alive after return: 0
=== hidden
1
temp=20
---
temp: n=1 min=20 max=20 mean=20
errors 0
threads started >= parsers: True
alive after return: 0
=== hidden
8
lidar=22.0
temp=55.0
imu=35.0
lidar=-0.5
temp=44.0
temp=25.5
lidar=4.5
temp=69.5
garbage line
lidar=72.0
imu=13.5
gps=35.5
temp=66.0
temp=25.5
temp=-8.0
imu=-20.5
lidar=8.0
temp=74.5
gps=28.5
temp=48.0
temp=49.5
gps=62.0
imu=10.5
lidar=64.0
imu=66.0
gps=11.0
temp=56.5
imu=19.0
temp=-6.0
garbage line
temp=-10.0
garbage line
imu=23.0
gps=45.5
gps=39.5
imu=14.5
garbage line
imu=0.0
gps=53.0
imu=18.0
---
gps: n=7 min=11 max=62 mean=39.29
imu: n=10 min=-20.5 max=66 mean=17.9
lidar: n=6 min=-0.5 max=72 mean=28.33
temp: n=13 min=-10 max=74.5 mean=37.69
errors 4
threads started >= parsers: True
alive after return: 0
=== hidden
10
lidar=23.0
temp=57.0
imu=54.0
gps=30.0
lidar=13.5
gps=41.5
gps=-24.0
gps=-22.5
lidar=-17.5
gps=34.5
gps=52.5
temp=-22.5
imu=22.0
temp=13.0
gps=-2.5
gps=72.0
gps=13.0
imu=73.5
lidar=14.5
gps=5.5
temp=58.0
imu=51.5
gps=61.0
temp=-3.5
garbage line
lidar=47.5
lidar=-10.0
garbage line
gps=48.5
gps=18.5
imu=54.0
lidar=28.5
gps=34.0
temp=12.0
temp=-20.5
lidar=0.5
garbage line
temp=46.5
lidar=-21.0
gps=44.5
---
gps: n=15 min=-24 max=72 mean=27.1
imu: n=5 min=22 max=73.5 mean=51
lidar: n=9 min=-21 max=47.5 mean=8.78
temp: n=8 min=-22.5 max=58 mean=17.5
errors 3
threads started >= parsers: True
alive after return: 0

## Hints
- Create `raw = queue.Queue()` and `parsed = queue.Queue()`. Start the parser threads and the aggregator thread **before** feeding lines.
- Parser loop: `while (line := raw.get()) is not None: try: parsed.put(("ok", *fetch(line))) except ValueError: parsed.put(("err",))`, then `parsed.put(("done",))` after the sentinel.
- The aggregator counts `"done"` markers until it reaches `parsers`. It's the only thread touching the result dictionaries, so they need no lock.
- `join()` every thread before returning (the driver checks that none are left alive).

## Solution
```python
import threading
import queue

def run_pipeline(lines, parsers, fetch):
    raw, parsed = queue.Queue(), queue.Queue()
    result = {}

    def parser():
        while (line := raw.get()) is not None:
            try:
                name, value = fetch(line)
                parsed.put(("ok", name, value))
            except ValueError:
                parsed.put(("err",))
        parsed.put(("done",))

    def aggregator():
        values, errors, done = {}, 0, 0
        while done < parsers:
            msg = parsed.get()
            if msg[0] == "ok":
                values.setdefault(msg[1], []).append(msg[2])
            elif msg[0] == "err":
                errors += 1
            else:
                done += 1
        result["sensors"] = {k: (len(v), min(v), max(v), round(sum(v) / len(v), 2)) for k, v in values.items()}
        result["errors"] = errors

    workers = [threading.Thread(target=parser, name=f"parser-{i}") for i in range(parsers)]
    agg = threading.Thread(target=aggregator, name="aggregator")
    for t in workers:
        t.start()
    agg.start()
    for line in lines:            # this thread is the reader
        raw.put(line)
    for _ in workers:
        raw.put(None)             # one sentinel per parser
    for t in workers:
        t.join()
    agg.join()
    return result
```

- **Queues do all the synchronisation:** `Queue.get()` blocks until data arrives and `put()` is thread-safe, so no explicit locks are needed anywhere.
- **Overlapping I/O:** while one parser sleeps inside `fetch`, the GIL is released and the others run, so N parsers cut the wall time by about N×. That's exactly the I/O-bound case where threads shine.
- **Clean shutdown with sentinels:** one `None` per parser guarantees each exits, and the "done" markers tell the aggregator when every result is in, with no polling, timeouts or daemon threads.
- **Single-writer state:** only the aggregator touches the statistics, the easiest way to avoid races.
