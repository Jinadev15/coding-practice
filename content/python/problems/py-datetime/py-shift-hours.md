---
id: py-shift-hours
title: Shift Hours Across Time Zones
difficulty: Medium
order: 1
tags: datetime, timezones, timedelta, ISO 8601
---
## Statement
A robotics company has operators in several countries. Each input line records one shift:

```
NAME START END
```

where `START` and `END` are ISO 8601 timestamps **with UTC offsets**, e.g. `2026-03-07T22:00:00+05:30`. A shift may cross midnight, and START and END may even use different offsets (an operator who changed zones). Lines with `END <= START` (the same instant or earlier) are invalid: count them, but ignore them otherwise.

Output:
1. For each operator, sorted by name: `NAME H:MM`, their total worked time (hours, then minutes zero-padded; hours may exceed 24).
2. `longest NAME START_UTC DURATION`: the longest single valid shift. START_UTC is formatted as `YYYY-MM-DD HH:MM` in UTC, and DURATION as `H:MM`. Ties go to the shift that appears first.
3. `invalid N`.
4. `busiest_day YYYY-MM-DD`: the **UTC calendar day** containing the most worked minutes, where a shift that spans midnight UTC contributes to each day separately. Ties go to the earlier day.

All durations are whole minutes. There's at least one valid shift.

## Starter
```python
import sys
from datetime import datetime, timedelta, timezone

for line in sys.stdin.read().splitlines():
    name, start, end = line.split()
```

## Tests
=== sample
ada 2026-03-07T22:00:00+05:30 2026-03-08T06:30:00+05:30
bob 2026-03-07T09:00:00-05:00 2026-03-07T17:15:00-05:00
ada 2026-03-08T10:00:00+05:30 2026-03-08T09:00:00+05:30
cy 2026-03-07T23:00:00+00:00 2026-03-08T01:00:00+01:00
bob 2026-03-08T20:00:00-05:00 2026-03-09T02:00:00-05:00
---
ada 8:30
bob 14:15
cy 1:00
longest ada 2026-03-07 16:30 8:30
invalid 1
busiest_day 2026-03-07
=== hidden
solo 2026-01-01T00:00:00+00:00 2026-01-03T00:30:00+00:00
---
solo 48:30
longest solo 2026-01-01 00:00 48:30
invalid 0
busiest_day 2026-01-01
=== hidden
a 2026-06-30T23:30:00+00:00 2026-07-01T00:30:00+00:00
b 2026-07-01T05:00:00+05:00 2026-07-01T06:00:00+05:00
a 2026-07-01T00:00:00+00:00 2026-07-01T00:00:00+00:00
c 2026-07-01T12:00:00+09:00 2026-07-01T03:00:00+00:00
---
a 1:00
b 1:00
longest a 2026-06-30 23:30 1:00
invalid 2
busiest_day 2026-07-01
=== hidden
x 2026-12-31T20:00:00-04:00 2027-01-01T08:00:00+08:00
y 2026-12-31T23:59:00+00:00 2027-01-01T00:01:00+00:00
---
y 0:02
longest y 2026-12-31 23:59 0:02
invalid 1
busiest_day 2026-12-31

## Hints
- `datetime.fromisoformat` parses the offset and returns **aware** datetimes, so subtracting two of them gives the true elapsed time even when the offsets differ.
- Normalise to UTC with `.astimezone(timezone.utc)` before looking at calendar days.
- To split a shift by UTC day: from `start`, repeatedly take `min(end, next_midnight)` where `next_midnight = datetime.combine(cur.date() + timedelta(days=1), time(0), tzinfo=timezone.utc)`.
- Format a timedelta as `H:MM` with `m = int(td.total_seconds()) // 60` and then `divmod(m, 60)`.

## Solution
```python
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone, time

def hm(td):
    h, m = divmod(int(td.total_seconds()) // 60, 60)
    return f"{h}:{m:02d}"

totals = defaultdict(timedelta)
per_day = defaultdict(timedelta)
invalid = 0
longest = None                                  # (duration, name, start_utc)

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    name, s, e = line.split()
    start = datetime.fromisoformat(s).astimezone(timezone.utc)
    end = datetime.fromisoformat(e).astimezone(timezone.utc)
    if end <= start:
        invalid += 1
        continue
    dur = end - start
    totals[name] += dur
    if longest is None or dur > longest[0]:
        longest = (dur, name, start)
    cur = start
    while cur < end:                            # split across UTC midnights
        midnight = datetime.combine(cur.date() + timedelta(days=1), time(0), tzinfo=timezone.utc)
        piece_end = min(end, midnight)
        per_day[cur.date()] += piece_end - cur
        cur = piece_end

for name in sorted(totals):
    print(name, hm(totals[name]))
dur, name, start = longest
print("longest", name, start.strftime("%Y-%m-%d %H:%M"), hm(dur))
print("invalid", invalid)
best_day = min(per_day, key=lambda d: (-per_day[d], d))
print("busiest_day", best_day.isoformat())
```

The key idea is to **convert to aware UTC at the boundary and do everything else in UTC**. Subtracting aware datetimes always gives the true elapsed time, so a shift from `20:00-04:00` to `08:00+08:00` the next day is correctly 0 hours (it ends at the same instant it starts), and it's flagged invalid. Splitting at UTC midnights with `min(end, next_midnight)` is the standard "bucket an interval by calendar unit" loop, useful for billing, utilisation dashboards and telemetry aggregation.
