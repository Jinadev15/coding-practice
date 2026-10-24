---
id: py-m2-job-scheduler
title: DAG Job Scheduler Simulation
difficulty: Expert
order: 3
tags: graphs, topological sort, heapq, discrete-event simulation, dataclasses
time_limit: 3
---
## Statement
Simulate a build/CI scheduler (like Bazel or a robot's mission planner) running jobs with **dependencies** on a fixed number of **worker slots**.

Input: the first line is `W` (the number of workers). Each following line defines a job:

```
NAME DURATION PRIORITY [deps=a,b,c] [fail=K]
```

- A job can start when **all its dependencies have succeeded**. Among ready jobs, the scheduler picks the **highest priority** (larger number first), then the **earliest ready time**, then the **name**.
- Time is simulated (integer ticks), starting at 0. When a job finishes, its worker frees immediately and the scheduler may start another job at that same tick. Several finishing at the same tick: process completions in name order **before** starting new jobs.
- `fail=K` means the job's first K attempts fail at the end of their duration, and it's **retried** (it becomes ready again at that time, without further delay) up to 2 retries (3 attempts total). If it still fails, it's marked FAILED, and **every job depending on it, directly or transitively**, is marked SKIPPED and never runs.
- Validation before simulating: an unknown dependency → `error: unknown dependency X of Y`, and a dependency cycle → `error: cycle detected` (only these lines are printed).

Output: one line per event in time order, `t=T start NAME (attempt A) on worker K` (workers numbered 0..W-1, with the lowest free one chosen), `t=T done NAME`, `t=T fail NAME (attempt A)`. Then a summary sorted by name, `NAME: SUCCEEDED/FAILED/SKIPPED`, and `makespan T` (the time of the last event).

## Starter
```python
import heapq
import sys

lines = sys.stdin.read().splitlines()
```

## Tests
=== sample
2
fetch 3 5
build 4 3 deps=fetch
lint 2 1 deps=fetch
test 5 2 deps=build fail=1
docs 1 9
package 2 1 deps=test,lint
---
t=0 start docs (attempt 1) on worker 0
t=0 start fetch (attempt 1) on worker 1
t=1 done docs
t=3 done fetch
t=3 start build (attempt 1) on worker 0
t=3 start lint (attempt 1) on worker 1
t=5 done lint
t=7 done build
t=7 start test (attempt 1) on worker 0
t=12 fail test (attempt 1)
t=12 start test (attempt 2) on worker 0
t=17 done test
t=17 start package (attempt 1) on worker 0
t=19 done package
build: SUCCEEDED
docs: SUCCEEDED
fetch: SUCCEEDED
lint: SUCCEEDED
package: SUCCEEDED
test: SUCCEEDED
makespan 19
=== hidden
1
a 1 1
b 1 2
c 1 3
---
t=0 start c (attempt 1) on worker 0
t=1 done c
t=1 start b (attempt 1) on worker 0
t=2 done b
t=2 start a (attempt 1) on worker 0
t=3 done a
a: SUCCEEDED
b: SUCCEEDED
c: SUCCEEDED
makespan 3
=== hidden
3
root 2 0
x 1 0 deps=root fail=3
y 4 0 deps=x
z 1 0 deps=y
w 3 7 deps=root
---
t=0 start root (attempt 1) on worker 0
t=2 done root
t=2 start w (attempt 1) on worker 0
t=2 start x (attempt 1) on worker 1
t=3 fail x (attempt 1)
t=3 start x (attempt 2) on worker 1
t=4 fail x (attempt 2)
t=4 start x (attempt 3) on worker 1
t=5 done w
t=5 fail x (attempt 3)
root: SUCCEEDED
w: SUCCEEDED
x: FAILED
y: SKIPPED
z: SKIPPED
makespan 5
=== hidden
2
a 1 0 deps=b
b 1 0 deps=c
c 1 0 deps=a
---
error: cycle detected
=== hidden
2
a 1 0 deps=ghost
---
error: unknown dependency ghost of a
=== hidden
4
j000 3 3
j001 6 4 deps=j000
j002 17 6 deps=j001,j000
j003 2 3 deps=j002,j000,j001
j004 19 7
j005 13 3
j006 14 2 deps=j001,j005,j004
j007 4 6
j008 15 2 deps=j003,j001
j009 18 2 deps=j004
j010 16 9 deps=j002,j006
j011 13 1
j012 9 2 deps=j004,j005
j013 16 1 deps=j012,j007,j011
j014 8 6 deps=j001,j004
j015 9 0 deps=j009,j002,j010
j016 12 8 deps=j013,j005
j017 2 5
j018 11 7 deps=j015
j019 8 2 deps=j008,j015,j006
j020 16 0 deps=j014,j018
j021 18 1
j022 7 6 deps=j005,j015
j023 1 3 deps=j006,j009,j016
j024 1 5 deps=j019,j006,j013
j025 14 5
j026 5 6 deps=j010,j002,j001
j027 18 0
j028 12 0 deps=j023,j026
j029 14 8
j030 17 7
j031 1 6 deps=j013,j021
j032 5 2 deps=j016
j033 18 1 deps=j032,j017
j034 11 1
j035 20 0
j036 6 1 deps=j004,j014
j037 13 1 deps=j016,j001,j005
j038 13 0 deps=j031
j039 3 9 deps=j007,j004,j003
j040 16 4
j041 13 0 deps=j013,j039
j042 16 5 deps=j021
j043 16 9 deps=j016
j044 2 9 deps=j043,j006
j045 10 4 deps=j042,j029
j046 4 5 deps=j045,j030
j047 20 1 deps=j007
j048 15 6
j049 14 1 deps=j040
j050 17 3 deps=j049,j005
j051 12 0
j052 8 3 deps=j003,j021,j013
j053 17 5 deps=j030,j035
j054 12 6
j055 10 4 deps=j000
j056 13 4
j057 12 4 deps=j018
j058 10 0
j059 10 2 deps=j024
j060 13 8 deps=j018,j014,j026
j061 14 0 deps=j017,j030
j062 17 4
j063 19 5
j064 10 5 deps=j021,j037
j065 18 1 deps=j044,j008
j066 5 4 deps=j052
j067 15 5 deps=j041,j053
j068 3 8 deps=j037,j048,j040
j069 15 7 deps=j005,j058,j037
j070 20 3
j071 20 1 deps=j012
j072 17 8 deps=j042
j073 12 4 deps=j026,j051
j074 11 5 deps=j031
j075 11 2 deps=j030,j074
j076 12 2 deps=j070,j001,j025
j077 9 3 deps=j035,j048,j042
j078 4 5 deps=j039,j020,j064
j079 6 4 deps=j063,j004
j080 18 6 deps=j068,j031,j010
j081 5 4 deps=j080,j038
j082 19 3 deps=j077
j083 4 6 deps=j081,j023
j084 2 7
j085 20 0 deps=j080
j086 20 5 deps=j074
j087 8 2 deps=j011,j062,j014
j088 16 5
j089 7 2 deps=j010 fail=3
j090 19 4
j091 10 1 deps=j005
j092 15 5 deps=j040
j093 16 3
j094 14 0 deps=j017,j060,j020
j095 2 8
j096 16 3 deps=j069
j097 13 5 deps=j055,j013
j098 16 0
j099 14 1 deps=j044,j013,j028
j100 4 6 deps=j091,j090,j037
j101 12 8 deps=j033
j102 11 2 deps=j081
j103 4 9 deps=j039,j041
j104 1 7 deps=j007
j105 16 0 deps=j044
j106 11 0 deps=j024,j031
j107 15 1
j108 7 6 deps=j087,j098
j109 4 3 deps=j091,j003,j066
j110 16 8
j111 17 8 deps=j070,j055
j112 2 9 deps=j041,j040
j113 7 2
j114 16 6 deps=j024,j113
j115 19 7 deps=j033,j027,j094
j116 10 5 deps=j020
j117 9 7 deps=j088
j118 7 2 deps=j076,j022
j119 18 0 deps=j013,j015
j120 4 3 deps=j054 fail=2
j121 8 5 deps=j086
j122 6 9 deps=j101,j056
j123 7 8 deps=j089,j008,j116
j124 11 8 deps=j065
j125 19 3 deps=j073
j126 14 0 deps=j064,j114
j127 3 9 deps=j053,j009
j128 11 5 deps=j035,j014,j024
j129 9 3 deps=j021,j125,j053
j130 8 2 deps=j015,j054,j057
j131 14 1 deps=j045,j094 fail=2
j132 7 7 deps=j061
j133 14 1 deps=j068
j134 8 8
j135 8 4 deps=j126
j136 6 6 deps=j029
j137 8 8 deps=j109,j031,j086
j138 16 1 deps=j116
j139 20 2 deps=j086 fail=2
j140 17 0 deps=j111
j141 7 6 deps=j031 fail=3
j142 10 7 deps=j122
j143 20 6 deps=j059
j144 20 1 deps=j129,j093
j145 4 6 deps=j046,j120
j146 17 0 deps=j036,j030
j147 17 5 deps=j137,j123 fail=3
j148 3 6 deps=j076
j149 7 0 deps=j024,j126
j150 6 2
j151 2 5 deps=j123,j137,j019
j152 10 8 deps=j045,j128,j024
j153 8 4
j154 15 1 deps=j010,j124,j055
j155 2 3
j156 18 7 deps=j052,j095,j013
j157 20 6 deps=j123,j150,j114 fail=3
j158 10 2 deps=j064
j159 13 4 deps=j081
j160 8 4 deps=j084,j037,j146
j161 15 7
j162 7 1 deps=j008 fail=2
j163 13 3 deps=j000
j164 19 0 deps=j028,j124,j131
j165 4 9 deps=j149,j000,j008
j166 8 0 deps=j054,j055,j102
j167 12 2
j168 18 7 deps=j042,j123
j169 7 7 deps=j158,j085
j170 7 6 deps=j110,j011
j171 11 0
j172 13 9 deps=j079,j102
j173 8 0
j174 13 0 deps=j070,j088,j054
j175 5 2
j176 9 3 deps=j052
j177 17 0 deps=j093
j178 20 6 deps=j176,j063,j073
j179 8 2 deps=j138,j127,j176 fail=3
j180 16 3 deps=j019,j048,j129
j181 20 9 deps=j098,j169,j116
j182 19 8 deps=j117
j183 6 0 deps=j024
j184 16 5 deps=j074,j126
j185 19 4 deps=j085
j186 15 4
j187 11 4
j188 12 0 deps=j071,j010,j157
j189 10 8 deps=j094
j190 18 4 deps=j014,j061
j191 6 4 deps=j068,j103
j192 1 0 deps=j098,j083
j193 3 7
j194 11 9 deps=j047,j166,j191
j195 3 2 deps=j099,j096,j181
j196 20 4 deps=j045
j197 7 2 deps=j087
j198 13 1
j199 17 9 deps=j196,j177
j200 1 0
j201 2 1 deps=j171,j047,j013
j202 5 5 deps=j174,j091
j203 1 9 deps=j032,j052
j204 7 4 deps=j130,j112
j205 3 2 deps=j183,j098
j206 9 0 deps=j057,j150,j075
j207 18 9 deps=j067
j208 10 2 deps=j174,j151
j209 7 8 deps=j116,j078
j210 12 8 deps=j187
j211 14 4 deps=j180,j047,j157
j212 2 2 deps=j197,j193,j165
j213 2 0 deps=j148
j214 12 8 deps=j030,j149 fail=2
j215 12 9
j216 14 5 deps=j185,j203
j217 8 6 deps=j063,j175
j218 1 7
j219 15 4 deps=j113
j220 17 8 deps=j052,j004,j201
j221 5 2 fail=2
j222 1 5 deps=j173,j155,j174
j223 2 3 deps=j160,j156
j224 12 2 fail=1
j225 9 1
j226 16 2 deps=j032
j227 14 7 deps=j160,j050
j228 20 3 deps=j077
j229 6 1 deps=j047,j201
j230 17 3 deps=j157
j231 8 1 deps=j171,j202,j146
j232 17 2 deps=j086,j153,j032
j233 11 5 deps=j210,j140
j234 13 2 deps=j119 fail=3
j235 3 0 deps=j028,j085,j167
j236 16 5
j237 9 7 deps=j053
j238 15 7
j239 17 2 deps=j163,j165,j149
j240 19 7 deps=j022,j104
j241 3 7 deps=j070,j128,j199
j242 7 5 deps=j072,j126,j078
j243 17 8 fail=2
j244 17 0
j245 17 0 deps=j135,j043
j246 19 1 deps=j006,j012
j247 14 5 deps=j125,j133,j218
j248 15 6 deps=j089
j249 12 9 deps=j197,j043,j143
j250 17 9 deps=j067,j030,j160
j251 8 4 deps=j240
j252 14 3
j253 2 9 deps=j148,j144,j157
j254 19 1 deps=j056
j255 16 9 deps=j247,j025,j085
j256 9 7
j257 14 8 deps=j253
j258 6 0 deps=j006,j112,j023
j259 20 8 deps=j052
j260 18 8 deps=j035
j261 6 6 deps=j198
j262 4 7 deps=j043,j012
j263 18 6 deps=j202,j260
j264 6 8 deps=j185,j224,j163
j265 18 1 deps=j008
j266 10 6 deps=j091,j129,j233
j267 19 7 deps=j118
j268 10 4 deps=j100,j136
j269 5 8 deps=j200,j064
j270 15 2 deps=j234,j059
j271 8 4
j272 6 6 deps=j044
j273 18 8 deps=j214
j274 14 0 deps=j195
j275 20 9 deps=j224,j197
j276 14 3 deps=j069,j011
j277 3 9
j278 10 8 deps=j214,j030
j279 20 2
j280 7 8 deps=j201,j139
j281 1 3 deps=j206,j090,j148
j282 7 9 deps=j111
j283 18 2
j284 11 8 deps=j130,j248
j285 4 2 deps=j228,j185,j235
j286 20 6
j287 7 1
j288 20 5 deps=j208
j289 18 7 fail=2
j290 3 7 deps=j047,j132
j291 16 1 deps=j255,j005
j292 9 9 deps=j054
j293 4 9 deps=j254,j202,j066
j294 8 2
j295 10 1 deps=j143
j296 17 3 deps=j203,j184,j199
j297 4 5 deps=j066,j172,j235
j298 20 3 deps=j215,j195,j200
j299 2 9 deps=j221,j244,j025

## Hints
- Parse each job into a dataclass `Job(name, duration, priority, deps, fail_count)`. Validate the dependencies, then detect cycles with Kahn's algorithm (if the topological order doesn't contain every job, there's a cycle) or a DFS with colours.
- Two heaps: `events` of `(time, name)` completions, and `ready` of `(-priority, ready_time, name)`.
- The main loop: pop **all** completion events at the current time (in name order), update states and free workers, push newly ready jobs, then start ready jobs while workers are free. The next current time is the earliest pending event.
- Skipping: when a job finally fails, do a DFS over the *reverse* dependency graph (dependents) and mark them SKIPPED.

## Solution
```python
import heapq
import sys
from dataclasses import dataclass, field

@dataclass
class Job:
    name: str
    duration: int
    priority: int
    deps: list
    fail: int = 0
    attempts: int = 0
    state: str = "PENDING"
    waiting: set = field(default_factory=set)

def parse(lines):
    workers = int(lines[0])
    jobs = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        name, dur, pri = parts[0], int(parts[1]), int(parts[2])
        deps, fail = [], 0
        for extra in parts[3:]:
            key, _, val = extra.partition("=")
            if key == "deps":
                deps = val.split(",")
            elif key == "fail":
                fail = int(val)
        jobs[name] = Job(name, dur, pri, deps, fail)
    return workers, jobs

def has_cycle(jobs):
    indeg = {n: len(j.deps) for n, j in jobs.items()}
    dependents = {n: [] for n in jobs}
    for n, j in jobs.items():
        for d in j.deps:
            dependents[d].append(n)
    queue = [n for n, k in indeg.items() if k == 0]
    seen = 0
    while queue:
        n = queue.pop()
        seen += 1
        for m in dependents[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    return seen != len(jobs), dependents

def main():
    lines = sys.stdin.read().splitlines()
    workers, jobs = parse(lines)
    for j in jobs.values():
        for d in j.deps:
            if d not in jobs:
                print(f"error: unknown dependency {d} of {j.name}")
                return
    cyclic, dependents = has_cycle(jobs)
    if cyclic:
        print("error: cycle detected")
        return

    out, ready, events = [], [], []
    free = list(range(workers))                      # a heap of free worker ids
    running = {}                                     # name -> worker id
    for j in jobs.values():
        j.waiting = set(j.deps)
        if not j.waiting:
            j.state = "READY"
            heapq.heappush(ready, (-j.priority, 0, j.name))

    def skip_dependents(name):
        stack = list(dependents[name])
        while stack:
            n = stack.pop()
            if jobs[n].state != "SKIPPED":
                jobs[n].state = "SKIPPED"
                stack.extend(dependents[n])

    t, last = 0, 0
    while True:
        while events and events[0][0] == t:          # all completions at this tick, in name order
            batch = []
            while events and events[0][0] == t:
                batch.append(heapq.heappop(events)[1])
            for name in sorted(batch):
                j = jobs[name]
                heapq.heappush(free, running.pop(name))
                if j.attempts <= j.fail:             # this attempt fails
                    out.append(f"t={t} fail {name} (attempt {j.attempts})")
                    if j.attempts < 3:
                        j.state = "READY"
                        heapq.heappush(ready, (-j.priority, t, name))
                    else:
                        j.state = "FAILED"
                        skip_dependents(name)
                else:
                    out.append(f"t={t} done {name}")
                    j.state = "SUCCEEDED"
                    for m in dependents[name]:
                        dj = jobs[m]
                        dj.waiting.discard(name)
                        if not dj.waiting and dj.state == "PENDING":
                            dj.state = "READY"
                            heapq.heappush(ready, (-dj.priority, t, m))
                last = t
        while ready and free:
            _, _, name = heapq.heappop(ready)
            j = jobs[name]
            if j.state != "READY":
                continue
            w = heapq.heappop(free)
            j.attempts += 1
            j.state = "RUNNING"
            running[name] = w
            out.append(f"t={t} start {name} (attempt {j.attempts}) on worker {w}")
            heapq.heappush(events, (t + j.duration, name))
            last = t
        if not events:
            break
        t = events[0][0]

    print("\n".join(out))
    for name in sorted(jobs):
        state = jobs[name].state
        print(f"{name}: {state if state in ('SUCCEEDED', 'FAILED', 'SKIPPED') else 'SKIPPED'}")
    print(f"makespan {last}")

main()
```

**What this milestone integrates:**
- **Graph algorithms:** validating references, then Kahn's algorithm (BFS on in-degrees) for cycle detection, the same check every build system, package manager and task planner performs.
- **Priority queues (module 8):** one heap for ready jobs with a composite key `(-priority, ready_time, name)`, and one for future completions. That's a **discrete-event simulation**: time jumps between events instead of ticking, so it's O((jobs + retries) log jobs) whatever the durations.
- **State machines:** each job moves through PENDING → READY → RUNNING → SUCCEEDED/FAILED, or to SKIPPED, with the retry policy as an explicit transition.
- **Determinism:** explicit tie-breaking (name order for simultaneous completions, the lowest free worker id) makes the schedule reproducible, which is essential for testing schedulers, and for robots whose missions must be replayable.
