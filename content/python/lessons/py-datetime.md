# datetime and time

Timestamps are everywhere: logs, sensor data, scheduling, rate limiting, ML datasets, robot telemetry. Time is also a notorious source of bugs: time zones, daylight-saving jumps, naive vs aware objects, month lengths, leap years, and confusing wall-clock time with elapsed time. This lesson covers `datetime` (calendar dates and times), `zoneinfo` (real time zones) and `time` (clocks for measuring durations), with the rules that keep time code correct.

## 1. The types

| Type | Represents | Example |
|---|---|---|
| `date` | a calendar day | `date(2026, 10, 24)` |
| `time` | a time of day | `time(14, 30)` |
| `datetime` | date + time (optionally with a zone) | `datetime(2026, 10, 24, 14, 30)` |
| `timedelta` | a **duration** | `timedelta(days=1, hours=2)` |
| `timezone` / `ZoneInfo` | an offset / a real zone with DST rules | `timezone.utc`, `ZoneInfo("Asia/Kolkata")` |

```python
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

dt = datetime(2026, 10, 24, 14, 30)
print(dt.isoformat())                    # 2026-10-24T14:30:00
print(dt.weekday(), dt.isoweekday())     # 5 6: Monday=0 vs Monday=1
print(date(2026, 3, 1) - date(2026, 2, 1))          # 28 days, 0:00:00
print((date(2024, 3, 1) - date(2024, 2, 1)).days)   # 29 (leap year)
```

All of these are **immutable**. Methods like `replace()` return new objects, and invalid values raise immediately:

```python
date(2026, 1, 31).replace(month=2)
# ValueError: day 31 must be in range 1..28 for month 2 in year 2026
```

## 2. Arithmetic with `timedelta`

```python
start = datetime(2026, 10, 24, 23, 0)
end = start + timedelta(hours=2, minutes=15)     # 2026-10-25 01:15:00: rolls over the date
elapsed = end - start                            # timedelta(seconds=8100)
print(elapsed.total_seconds())                   # 8100.0
print(timedelta(hours=25))                       # 1 day, 1:00:00 (normalised)
```

`timedelta` stores days, seconds and microseconds. Its `.seconds` attribute is **only the seconds part** (0–86399), not the total, so use `total_seconds()`. Months and years aren't fixed-length, so `timedelta` has no `months=`. "One month later" is a calendar question: handle it with `replace` and clamping, or use `dateutil.relativedelta`.

## 3. Formatting and parsing

```python
dt.strftime("%Y-%m-%d %H:%M %A")                     # '2026-10-24 14:30 Saturday'
datetime.strptime("24/10/2026 09:05", "%d/%m/%Y %H:%M")   # 2026-10-24 09:05:00
datetime.fromisoformat("2026-10-24T14:30:00+05:30")       # aware datetime, +05:30
```

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| `%Y` | 4-digit year | `%H` | hour 00–23 |
| `%m` | month 01–12 | `%I` / `%p` | hour 01–12 / AM-PM |
| `%d` | day 01–31 | `%M` | minute |
| `%A` / `%a` | weekday name / abbreviation | `%S` | second |
| `%B` / `%b` | month name / abbreviation | `%f` | microseconds |
| `%j` | day of the year | `%z` | UTC offset, `+0530` |

> [!TIP]
> For data interchange (logs, JSON, APIs, databases), use **ISO 8601** (`isoformat()` / `fromisoformat()`) with an offset, ideally in UTC: `2026-10-24T09:00:00+00:00`. It's unambiguous and sorts correctly as a string. Never store `"10/11/2026"`: is that October or November?

## 4. Naive vs aware: the most important distinction

- A **naive** datetime has no time zone (`tzinfo is None`). It's an abstract wall-clock reading. "14:30" where?
- An **aware** datetime has `tzinfo` and represents an exact instant.

```python
ist = datetime(2026, 10, 24, 14, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
print(ist.astimezone(timezone.utc))            # 2026-10-24 09:00:00+00:00: same instant
now_utc = datetime.now(timezone.utc)           # aware "now": always prefer this

datetime(2026, 1, 1) - datetime(2026, 1, 1, tzinfo=timezone.utc)
# TypeError: can't subtract offset-naive and offset-aware datetimes
```

> [!KEY]
> **Rule:** store and compute in **aware UTC**, and convert to local time only for display. `datetime.utcnow()` returns a *naive* datetime that only looks like UTC. It's deprecated since 3.12 because it caused exactly these bugs. Use `datetime.now(timezone.utc)`.

### Daylight saving time

`ZoneInfo` zones (from the IANA tz database) know when clocks jump. Arithmetic on aware datetimes in the **same zone** is **wall-clock arithmetic**, which can surprise you across DST changes:

```python
ny = ZoneInfo("America/New_York")
a = datetime(2026, 3, 8, 1, 30, tzinfo=ny)          # 1:30 the night clocks spring forward
print(a + timedelta(hours=1))                       # 2026-03-08 02:30:00-05:00: a time that never existed on clocks
```

For **elapsed** time across DST, convert to UTC, add, then convert back: `(a.astimezone(timezone.utc) + timedelta(hours=1)).astimezone(ny)` gives `03:30-04:00`.

## 5. The `time` module: clocks for measuring

| Function | Clock | Use for |
|---|---|---|
| `time.time()` | wall clock: seconds since the Unix epoch (1970-01-01 UTC) | timestamps |
| `time.monotonic()` | never goes backwards | timeouts, rate limits, control loops |
| `time.perf_counter()` | monotonic, highest resolution | benchmarking |
| `time.sleep(s)` | | waiting |
| `time.time_ns()`, `perf_counter_ns()` | integer nanoseconds | precise timing without float error |

> [!DANGER]
> Never measure durations with `time.time()` or `datetime.now()`. The wall clock can **jump** (NTP corrections, manual changes, DST in local time), so a timeout can fire early, never fire, or report negative durations. A robot control loop timed with the wall clock can stall when NTP steps the clock. Use `time.monotonic()` (or `perf_counter()`).

```python
import time
deadline = time.monotonic() + 0.5
while time.monotonic() < deadline:
    ...                                   # poll a sensor for at most 500 ms

t0 = time.perf_counter()
work()
print(f"{(time.perf_counter() - t0) * 1000:.2f} ms")
```

Converting between epoch seconds and datetimes: `datetime.fromtimestamp(ts, timezone.utc)` and `dt.timestamp()`.

## 6. Exam-ready answers

> [!EXAM]
> **Dates and times in Python.** The `datetime` module provides immutable types: `date` for calendar dates, `time` for times of day, `datetime` for combined date and time, and `timedelta` for durations, which support arithmetic such as adding a duration to a datetime or subtracting two datetimes. A datetime is naive if it has no time-zone information and aware if its `tzinfo` attribute is set; aware datetimes identify exact instants and can be converted between zones with `astimezone`, using `zoneinfo.ZoneInfo` for IANA zones with daylight-saving rules. Formatting and parsing use `strftime`/`strptime` with format codes, or the ISO 8601 functions `isoformat`/`fromisoformat`. Best practice is to store and compute times in aware UTC and convert to local time only for display, and to measure elapsed time with a monotonic clock such as `time.monotonic` or `time.perf_counter` rather than the wall clock.

## 7. Cheat sheet

| Need | Code |
|---|---|
| now (correctly) | `datetime.now(timezone.utc)` |
| local zone | `ZoneInfo("Asia/Kolkata")` |
| convert zone | `dt.astimezone(ZoneInfo("Europe/London"))` |
| format / parse | `dt.strftime(fmt)` / `datetime.strptime(s, fmt)` |
| ISO round trip | `dt.isoformat()` / `datetime.fromisoformat(s)` |
| duration in seconds | `(b - a).total_seconds()` |
| epoch ↔ datetime | `dt.timestamp()` / `datetime.fromtimestamp(ts, timezone.utc)` |
| measure time | `time.perf_counter()` |
| timeout | `time.monotonic()` |

> [!INTERVIEW]
> **"A log processor computes request durations as `end_wallclock - start_wallclock` and sometimes gets negative values. Why, and what's the fix?"** The wall clock isn't monotonic: NTP adjustments, manual clock changes, leap-second smearing, or local-time DST transitions make it jump backwards or forwards. Durations must be measured with a monotonic clock (`time.monotonic()` / `perf_counter()` in Python, `CLOCK_MONOTONIC` in C). Wall-clock timestamps should still be logged, in UTC ISO 8601, for correlating events across machines, but never subtracted to get durations within a process.
