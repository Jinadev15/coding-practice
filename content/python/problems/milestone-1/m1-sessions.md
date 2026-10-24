---
id: py-m1-sessions
title: User Session Analyzer
difficulty: Hard
order: 4
tags: generators, parsing, grouping, sorting, exceptions
---
## Statement
A web server log has one event per line: `timestamp user action` (timestamp = integer seconds; lines are **not** necessarily sorted). Malformed lines (wrong field count or non-integer timestamp) are skipped and counted.

A **session** is a maximal run of one user's events in which consecutive events (sorted by time) are at most `gap` seconds apart. The first line of input is `gap`.

Print:

1. `malformed M`
2. one line per user, sorted by user name: `user sessions=S events=E longest=L` where `longest` is the duration in seconds of the user's longest session (last event time − first event time)
3. `busiest second: T (N events)`: the timestamp with the most events overall (ties: the earliest), or `busiest second: none`
4. `funnel: X/Y`: the number of users who performed `view`, then later `cart`, then later `buy` (in time order, not necessarily consecutively, possibly across sessions), out of all users

Write it as a pipeline of **generator functions**: one that parses lines, one that groups events by user, and one that splits a user's sorted events into sessions.

## Starter
```python
import sys

def parse(lines, stats):
    # yield (ts, user, action); count malformed lines in stats["malformed"]
    pass

def sessions(events, gap):
    # events: sorted list of (ts, action) for one user; yield lists of events
    pass

def main():
    lines = sys.stdin.read().splitlines()
    gap = int(lines[0])

main()
```

## Tests
=== sample
30
100 ann view
110 ann cart
200 ann buy
105 bob view
bad line here
abc bob view
115 bob view
130 bob buy
100 cy view
---
malformed 2
ann sessions=2 events=3 longest=10
bob sessions=1 events=3 longest=25
cy sessions=1 events=1 longest=0
busiest second: 100 (2 events)
funnel: 1/3
=== hidden
5

---
malformed 0
busiest second: none
funnel: 0/0
=== hidden
10
50 z buy
40 z cart
30 z view
5 y cart
6 y view
7 y cart
8 y buy
60 x view
---
malformed 0
x sessions=1 events=1 longest=0
y sessions=1 events=4 longest=3
z sessions=1 events=3 longest=20
busiest second: 5 (1 events)
funnel: 2/3
=== hidden
0
1 a view
1 a cart
1 a buy
1 b view
2 b view
---
malformed 0
a sessions=1 events=3 longest=0
b sessions=2 events=2 longest=0
busiest second: 1 (4 events)
funnel: 1/2

## Hints
- `parse` yields tuples and catches `ValueError` from `int()` and from the 3-way unpacking.
- Group with a dict `user -> list`, then sort each user's list by timestamp. Python's sort is stable, so events with equal timestamps keep their input order.
- Funnel: scan a user's time-sorted actions with a state index into `["view", "cart", "buy"]`, advancing when the expected action appears.
- Note the third hidden test: user `a` does view, cart, buy all at second 1, in that input order. Stable sorting keeps that order, so it counts.

## Solution
Three small generators form the pipeline, and `main` just aggregates. Stability of `sorted` on `(ts)` keys preserves the input order of simultaneous events, which the funnel relies on.

```python
import sys

def parse(lines, stats):
    for line in lines:
        if not line.strip():
            continue
        try:
            ts, user, action = line.split()
            yield int(ts), user, action
        except ValueError:
            stats["malformed"] += 1

def sessions(events, gap):
    current = []
    for ts, action in events:
        if current and ts - current[-1][0] > gap:
            yield current
            current = []
        current.append((ts, action))
    if current:
        yield current

def funnel_done(events):
    steps = ["view", "cart", "buy"]
    k = 0
    for _, action in events:
        if k < 3 and action == steps[k]:
            k += 1
    return k == 3

def main():
    lines = sys.stdin.read().splitlines()
    gap = int(lines[0])
    stats = {"malformed": 0}
    by_user, per_second = {}, {}
    for ts, user, action in parse(lines[1:], stats):
        by_user.setdefault(user, []).append((ts, action))
        per_second[ts] = per_second.get(ts, 0) + 1

    print("malformed", stats["malformed"])
    funnel = 0
    for user in sorted(by_user):
        events = sorted(by_user[user], key=lambda e: e[0])
        sess = list(sessions(events, gap))
        longest = max(s[-1][0] - s[0][0] for s in sess)
        print(f"{user} sessions={len(sess)} events={len(events)} longest={longest}")
        funnel += funnel_done(events)
    if per_second:
        t = min(per_second, key=lambda s: (-per_second[s], s))
        print(f"busiest second: {t} ({per_second[t]} events)")
    else:
        print("busiest second: none")
    print(f"funnel: {funnel}/{len(by_user)}")

main()
```

`parse` is lazy, so a log of any size streams through it, and only the grouped events per user are held in memory. The session splitter is the classic "split a sorted sequence where the gap exceeds a threshold" pattern, used for user analytics, sensor bursts and trajectory segmentation in robotics. A gap of `0` means only simultaneous events share a session (user `b`).
