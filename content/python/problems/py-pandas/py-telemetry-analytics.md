---
id: py-telemetry-analytics
title: Robot Fleet Telemetry Analytics with pandas
difficulty: Hard
order: 1
tags: pandas, groupby, merge, resample, interpolate, time series
time_limit: 4
---
## Statement
Fleet telemetry arrives as CSV text with columns `time,robot,battery,speed,task`:
- `time` is an ISO timestamp.
- `battery` is a percentage and may be empty.
- `speed` is in m/s.
- `task` is a short label.

Robot metadata is a second CSV, `robot,model,site`. Implement these with pandas (vectorised; no row loops):

```python
def load(csv_text):
    """Parse into a DataFrame with `time` as datetime64, sorted by (robot, time), with a fresh RangeIndex."""

def fleet_summary(df):
    """One row per robot (sorted by robot): samples, mean_speed (3 decimals), min_battery,
    battery_drop = first non-null battery - last non-null battery, busiest_task = most frequent task
    (ties -> alphabetically first). Columns exactly: robot, samples, mean_speed, min_battery, battery_drop, busiest_task."""

def fill_battery(df):
    """Fill missing battery per robot by linear interpolation in time order; remaining leading/trailing gaps
    take the nearest value of the same robot. Return a new DataFrame (don't modify df)."""

def per_minute(df, robot):
    """For one robot: resample to 1-minute bins (labels = bin starts) with mean speed rounded to 3 decimals;
    empty minutes are dropped. Return a Series indexed by time."""

def site_report(df, meta_text):
    """Join telemetry with metadata on robot (robots missing from metadata go to site 'unknown');
    per site: robots (unique count) and total distance = sum of speed * seconds until the robot's next sample
    (the last sample of each robot contributes 0). Distance rounded to 1 decimal. Sorted by site."""
```

The driver prints the results with `to_string()`.

## Starter
```python
import io
import pandas as pd

def load(csv_text):
    return pd.read_csv(io.StringIO(csv_text))

def fleet_summary(df):
    return df.groupby("robot").size().reset_index(name="samples")

def fill_battery(df):
    return df.ffill()

def per_minute(df, robot):
    return df[df.robot == robot]["speed"]

def site_report(df, meta_text):
    return pd.DataFrame()
```

## Driver
```python
import sys
import numpy as np
import pandas as pd

text = sys.stdin.read()
tele, meta, *cmds = text.split("%%\n")
df = load(tele)
print("time_is_datetime:", pd.api.types.is_datetime64_any_dtype(df["time"]), "rows:", len(df), "index_ok:", df.index.equals(pd.RangeIndex(len(df))))
for c in "".join(cmds).split():
    if c == "summary":
        print(fleet_summary(df).to_string(index=False))
    elif c == "fill":
        before = df["battery"].isna().sum()
        f = fill_battery(df)
        print("filled:", int(before), "->", int(f["battery"].isna().sum()), "| original untouched:", int(df["battery"].isna().sum()) == int(before))
        print(f[["robot", "battery"]].round(2).to_string(index=False))
    elif c.startswith("minute:"):
        m = per_minute(df, c.split(":", 1)[1])
        print("minute", c.split(":", 1)[1] + ":", [f"{t:%H:%M}={v}" for t, v in m.items()])
    elif c == "sites":
        print(site_report(df, meta).to_string(index=False))
    elif c == "big":
        rng = np.random.default_rng(5)
        n = 200000
        t0 = pd.Timestamp("2026-03-01")
        big = pd.DataFrame({
            "time": t0 + pd.to_timedelta(np.sort(rng.integers(0, 86400, n)), unit="s"),
            "robot": rng.choice([f"r{i:02d}" for i in range(40)], n),
            "battery": np.where(rng.random(n) < 0.05, np.nan, rng.uniform(5, 100, n).round(1)),
            "speed": rng.uniform(0, 2, n).round(3),
            "task": rng.choice(["pick", "move", "dock", "scan"], n),
        })
        csv = big.to_csv(index=False)
        b = load(csv)
        s = fleet_summary(b)
        fb = fill_battery(b)
        m = per_minute(b, "r07")
        sr = site_report(b, "robot,model,site\n" + "\n".join(f"r{i:02d},m{i % 3},s{i % 5}" for i in range(35)))
        print("big:", len(s), round(float(s["mean_speed"].mean()), 4), int(fb["battery"].isna().sum()), len(m),
              sr["robots"].tolist(), round(float(sr["distance"].sum()), 1))
```

## Tests
=== sample
time,robot,battery,speed,task
2026-01-05T08:00:00,r1,90,0.5,move
2026-01-05T08:00:30,r1,,0.7,move
2026-01-05T08:01:10,r1,86,0.0,pick
2026-01-05T08:00:15,r2,75,1.2,scan
2026-01-05T08:02:15,r2,70,1.0,scan
%%
robot,model,site
r1,arm,lab
r2,rover,yard
%%
summary
fill
minute:r1
sites
---
time_is_datetime: True rows: 5 index_ok: True
robot  samples  mean_speed  min_battery  battery_drop busiest_task
   r1        3         0.4         86.0           4.0         move
   r2        2         1.1         70.0           5.0         scan
filled: 1 -> 0 | original untouched: True
robot  battery
   r1     90.0
   r1     88.0
   r1     86.0
   r2     75.0
   r2     70.0
minute r1: ['08:00=0.6', '08:01=0.0']
site  robots  distance
 lab       1      43.0
yard       1     144.0
=== hidden
time,robot,battery,speed,task
2026-01-05T09:00:00,b,,1.0,dock
2026-01-05T09:00:10,b,50,1.0,move
2026-01-05T09:00:20,b,,2.0,move
2026-01-05T09:00:40,b,40,0.0,dock
2026-01-05T09:00:50,b,,0.5,move
2026-01-05T09:00:05,a,99,0.25,pick
2026-01-05T09:03:05,c,,3.0,scan
%%
robot,model,site
a,arm,lab
b,rover,lab
%%
summary
fill
minute:b
minute:a
sites
---
time_is_datetime: True rows: 7 index_ok: True
robot  samples  mean_speed  min_battery  battery_drop busiest_task
    a        1        0.25         99.0           0.0         pick
    b        5        0.90         40.0          10.0         move
    c        1        3.00          NaN           NaN         scan
filled: 4 -> 1 | original untouched: True
robot  battery
    a     99.0
    b     50.0
    b     50.0
    b     45.0
    b     40.0
    b     40.0
    c      NaN
minute b: ['09:00=0.9']
minute a: ['09:00=0.25']
   site  robots  distance
    lab       2      60.0
unknown       1       0.0
=== hidden
time,robot,battery,speed,task
2026-01-05T09:00:00,x,10,1.0,move
%%
robot,model,site
%%
big
---
time_is_datetime: True rows: 1 index_ok: True
big: 40 1.0008 0 1395 [7, 7, 7, 7, 7, 5] 3460011.2

## Hints
- `load`: `pd.read_csv(io.StringIO(text), parse_dates=["time"])`, then `sort_values(["robot", "time"]).reset_index(drop=True)`.
- `fleet_summary`: `groupby("robot").agg(...)` with named aggregations. For the first/last non-null battery, `first`/`last` skip NaN in group-by. For the busiest task, use `value_counts` sorted by (count desc, task asc), or `agg(lambda s: s.value_counts().sort_index().idxmax())`.
- `fill_battery`: `df.groupby("robot")["battery"].transform(lambda s: s.interpolate().ffill().bfill())` on a copy.
- `per_minute`: filter, `set_index("time")["speed"].resample("1min").mean().dropna().round(3)`.
- `site_report`: the next sample's time per robot is `groupby("robot")["time"].shift(-1)`. The duration is `(next - time).dt.total_seconds().fillna(0)`. Left-merge the metadata and `fillna("unknown")` the site.

## Solution
```python
import io
import pandas as pd

def load(csv_text):
    df = pd.read_csv(io.StringIO(csv_text), parse_dates=["time"])
    return df.sort_values(["robot", "time"], kind="stable").reset_index(drop=True)

def _busiest(s):
    counts = s.value_counts()
    top = counts.max()
    return sorted(counts[counts == top].index)[0]

def fleet_summary(df):
    g = df.groupby("robot", sort=True)
    out = g.agg(samples=("speed", "size"), mean_speed=("speed", "mean"), min_battery=("battery", "min"),
                first_b=("battery", "first"), last_b=("battery", "last"), busiest_task=("task", _busiest)).reset_index()
    out["mean_speed"] = out["mean_speed"].round(3)
    out["battery_drop"] = out["first_b"] - out["last_b"]
    return out[["robot", "samples", "mean_speed", "min_battery", "battery_drop", "busiest_task"]]

def fill_battery(df):
    out = df.copy()
    out["battery"] = out.groupby("robot")["battery"].transform(lambda s: s.interpolate().ffill().bfill())
    return out

def per_minute(df, robot):
    s = df.loc[df["robot"] == robot].set_index("time")["speed"]
    return s.resample("1min").mean().dropna().round(3)

def site_report(df, meta_text):
    meta = pd.read_csv(io.StringIO(meta_text))
    d = df.copy()
    nxt = d.groupby("robot")["time"].shift(-1)
    d["distance"] = d["speed"] * (nxt - d["time"]).dt.total_seconds().fillna(0)
    d = d.merge(meta[["robot", "site"]], on="robot", how="left", validate="many_to_one")
    d["site"] = d["site"].fillna("unknown")
    rep = d.groupby("site", sort=True).agg(robots=("robot", "nunique"), distance=("distance", "sum")).reset_index()
    rep["distance"] = rep["distance"].round(1)
    return rep
```

- **Parsing and ordering first**: `parse_dates` gives real `datetime64` values, so time arithmetic and resampling work, and sorting by (robot, time) makes every per-robot operation well defined.
- **Named aggregations** produce the exact output columns in one `groupby`. In group-by, `first` and `last` skip NaN, which is what "first non-null battery" needs.
- **`transform`** keeps the original row shape while working per robot, so interpolation never leaks values between robots. `ffill`/`bfill` then handle the edges.
- **Resampling** needs a `DatetimeIndex`. Minutes with no samples come out NaN and are dropped.
- **`shift(-1)` within groups** gives each sample its successor's timestamp, turning speed × elapsed time into distance with no loop. The left merge with `validate=` keeps robots that have no metadata (site 'unknown') and guards against duplicate metadata rows.
