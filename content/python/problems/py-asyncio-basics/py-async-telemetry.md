---
id: py-async-telemetry
title: Concurrent Robot Telemetry with asyncio
difficulty: Medium
order: 1
tags: asyncio, gather, create_task, to_thread, event loop
time_limit: 2
---
## Statement
A ground station polls several robots over the network. The driver provides **async** fake I/O:

```python
async def query(robot: str, field: str) -> float      # awaits a latency depending on the robot, then returns a value
def legacy_checksum(values: list[float]) -> int        # a BLOCKING library call (time.sleep inside!) that must not stall the loop
```

Implement:

```python
async def robot_status(robot: str) -> dict
    # query "battery", "temp" and "speed" for ONE robot concurrently (asyncio.gather), then compute
    # checksum = legacy_checksum([battery, temp, speed]) WITHOUT blocking the event loop (asyncio.to_thread)
    # returns {"robot": robot, "battery": b, "temp": t, "speed": s, "checksum": c}
async def fleet_status(robots: list[str]) -> list[dict]
    # all robots concurrently, results in the same order as `robots`
```

Each query takes up to 0.3 s and the blocking checksum 0.2 s. With 10 robots, a sequential version takes about 11 s. Correct concurrency finishes in about 0.5 s. The driver also runs a **heartbeat task** that ticks every 0.05 s, and reports whether it was ever starved for more than 0.15 s, which happens if you call the blocking function directly.

## Starter
```python
import asyncio

async def robot_status(robot):
    b = await query(robot, "battery")
    t = await query(robot, "temp")
    s = await query(robot, "speed")
    return {"robot": robot, "battery": b, "temp": t, "speed": s, "checksum": legacy_checksum([b, t, s])}

async def fleet_status(robots):
    return [await robot_status(r) for r in robots]
```

## Driver
```python
import sys
import time
import zlib

async def query(robot, field):
    h = zlib.crc32(f"{robot}/{field}".encode())
    await asyncio.sleep(0.1 + (h % 200) / 1000)
    return round((h % 10000) / 100, 2)

def legacy_checksum(values):
    time.sleep(0.2)                       # blocking!
    return int(sum(values) * 100) % 997

async def heartbeat(stop, gaps):
    last = time.perf_counter()
    while not stop.is_set():
        await asyncio.sleep(0.05)
        now = time.perf_counter()
        gaps.append(now - last)
        last = now

async def main():
    robots = sys.stdin.read().split()
    stop, gaps = asyncio.Event(), []
    hb = asyncio.create_task(heartbeat(stop, gaps))
    results = await fleet_status(robots)
    stop.set()
    await hb
    for r in results:
        print(f"{r['robot']}: battery={r['battery']} temp={r['temp']} speed={r['speed']} checksum={r['checksum']}")
    print("event loop stayed responsive:", max(gaps, default=0) < 0.15)

asyncio.run(main())
```

## Tests
=== sample
rover drone arm
---
rover: battery=2.17 temp=30.34 speed=74.65 checksum=746
drone: battery=53.57 temp=48.9 speed=47.41 checksum=33
arm: battery=28.72 temp=0.73 speed=58.65 checksum=834
event loop stayed responsive: True
=== hidden
solo
---
solo: battery=81.0 temp=13.64 speed=66.96 checksum=208
event loop stayed responsive: True
=== hidden
r1 r2 r3 r4 r5 r6 r7 r8 r9 r10
---
r1: battery=93.2 temp=88.07 speed=13.7 checksum=554
r2: battery=90.53 temp=8.25 speed=9.83 checksum=891
r3: battery=64.62 temp=42.52 speed=14.43 checksum=193
r4: battery=31.91 temp=48.68 speed=8.13 checksum=896
r5: battery=21.48 temp=86.57 speed=46.81 checksum=530
r6: battery=52.01 temp=6.71 speed=69.64 checksum=871
r7: battery=29.62 temp=70.02 speed=70.24 checksum=39
r8: battery=62.11 temp=22.87 speed=13.37 checksum=862
r9: battery=14.08 temp=4.42 speed=84.45 checksum=325
r10: battery=86.72 temp=22.04 speed=55.72 checksum=496
event loop stayed responsive: True

## Hints
- Three fields concurrently: `b, t, s = await asyncio.gather(query(robot, "battery"), query(robot, "temp"), query(robot, "speed"))`.
- `checksum = await asyncio.to_thread(legacy_checksum, [b, t, s])` runs the blocking call in a worker thread while the loop keeps serving other tasks.
- Fleet: `return await asyncio.gather(*(robot_status(r) for r in robots))`. `gather` returns results in argument order.

## Solution
```python
import asyncio

async def robot_status(robot):
    b, t, s = await asyncio.gather(
        query(robot, "battery"), query(robot, "temp"), query(robot, "speed"))
    checksum = await asyncio.to_thread(legacy_checksum, [b, t, s])   # never block the loop
    return {"robot": robot, "battery": b, "temp": t, "speed": s, "checksum": checksum}

async def fleet_status(robots):
    return list(await asyncio.gather(*(robot_status(r) for r in robots)))
```

- **`gather` at two levels:** the fields of one robot overlap, and all robots overlap, so the total time is about the slowest single robot (max query latency + checksum), not the sum of everything.
- **`asyncio.to_thread`** moves the blocking legacy call into a thread pool. Calling it directly would freeze the event loop for 0.2 s per robot: the heartbeat would detect gaps, and in a real station, every other connection would stall. That's the cooperative-scheduling rule: never block in a coroutine.
- **Order is preserved:** `gather` returns results in the order of its arguments, regardless of which finishes first.
