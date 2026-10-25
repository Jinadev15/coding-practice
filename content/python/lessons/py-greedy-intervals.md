# Greedy Algorithms and Intervals

A **greedy algorithm** builds a solution by repeatedly taking the locally best choice and never reconsidering it. When it works, it's usually the simplest and fastest solution (often a sort plus one pass), but it only works when the problem has the **greedy-choice property**: some optimal solution begins with the greedy choice. This lesson shows how to *prove* a greedy algorithm correct (exchange arguments, staying ahead) and covers the big family of **interval problems** (scheduling, merging, covering, meeting rooms), along with classic greedy problems such as jump game, gas station, Huffman coding and task assignment.

## 1. When greedy works, and how to prove it

| Proof technique | Idea |
|---|---|
| **Exchange argument** | take any optimal solution that differs from the greedy one; swap in the greedy choice without making it worse; repeat until they're identical |
| **Greedy stays ahead** | show by induction that after each step, the greedy partial solution is at least as good as any other |
| **Matroid structure** | for problems on matroids (e.g. spanning forests), greedy by weight is optimal (Kruskal) |

> [!WARNING]
> Always test a greedy idea against small counterexamples. "Largest coin first" fails for coins {1, 3, 4} and amount 6. "Shortest interval first" fails for interval scheduling. "Earliest start first" fails too. Only "earliest **end** first" is correct, and you should know why.

## 2. Interval scheduling: maximise non-overlapping intervals

**Greedy**: sort by **end** time, and take each interval that starts at or after the last taken end.

```python
def max_non_overlapping(intervals):
    count, end = 0, float("-inf")
    for s, e in sorted(intervals, key=lambda iv: iv[1]):
        if s >= end:                  # compatible with everything taken so far
            count += 1
            end = e
    return count
```

**Why it's correct** (an exchange argument): the interval with the earliest end, g, can replace the first interval of any optimal schedule, because g ends no later and so conflicts with nothing that interval didn't. Repeating the argument on the rest proves optimality. "Minimum intervals to remove so the rest don't overlap" is `n - max_non_overlapping`. "Minimum arrows to burst balloons" is the same algorithm with a different notion of overlap (closed intervals: `s > end`).

## 3. Merging and inserting intervals

```python
def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:          # overlaps (or touches) the last merged interval
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out

merge([[1, 3], [8, 10], [2, 6], [15, 18]])    # [[1, 6], [8, 10], [15, 18]]
```

Inserting into a sorted, non-overlapping list takes three phases: copy the intervals that end before the new one, merge all overlapping ones into it, then copy the rest. That's O(n). Intersecting two sorted interval lists uses two pointers: take `max(starts)` and `min(ends)`, then advance whichever interval ends first.

## 4. Covering and resources

| Problem | Greedy | Complexity |
|---|---|---|
| minimum meeting rooms | sort by start, min-heap of end times (or ±1 sweep) | O(n log n) |
| minimum intervals to cover [0, T] (video stitching) | among intervals starting ≤ the current reach, pick the farthest end | O(n log n) |
| jump game II (min jumps) | BFS-like layers: track the farthest reach within the current jump | O(n) |
| minimum platforms / CPUs | sweep of sorted arrivals and departures | O(n log n) |
| non-overlapping lecture assignment | earliest start + heap of free rooms | O(n log n) |

```python
def min_jumps(nums):                     # jump game II
    jumps = cur_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:                 # must jump now; jump as far as possible
            jumps += 1
            cur_end = farthest
    return jumps
```

## 5. More classic greedy problems

**Gas station**: if the total gas ≥ the total cost, a solution exists, and it starts right after the last point where the running tank went negative.

```python
def gas_station(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    tank = start = 0
    for i, (g, c) in enumerate(zip(gas, cost)):
        tank += g - c
        if tank < 0:                     # can't reach i+1 from start: no station in [start, i] works
            start, tank = i + 1, 0
    return start
```

**Assign cookies / boats / two-city scheduling**: sort, then pair greedily. For boats (capacity limit, at most 2 people), pair the heaviest with the lightest when they fit, using two pointers.

**Huffman coding** (optimal prefix codes): repeatedly merge the two least frequent symbols, using a heap, in O(n log n). The exchange argument shows that the two rarest symbols can be the deepest siblings. This is the basis of DEFLATE/ZIP and JPEG entropy coding.

**Fractional knapsack**: sort by value/weight and take greedily, splitting the last item. Greedy is optimal here, unlike 0/1 knapsack, which needs DP.

**Scheduling to minimise lateness**: sort by deadline (earliest deadline first, EDF), which is optimal by an exchange argument. EDF is also an optimal real-time CPU scheduling policy for preemptive tasks on one processor.

## 6. Greedy vs DP: a decision guide

| Signal | Leans to |
|---|---|
| sorting by one key makes every decision obvious | greedy |
| a counterexample breaks the obvious greedy | DP |
| choices interact over long ranges (knapsack weights) | DP |
| "maximum number of compatible items", intervals by end | greedy |
| optimal substructure **and** the greedy-choice property, provable | greedy |

## 7. Exam-ready answers

> [!EXAM]
> **Greedy algorithms.** A greedy algorithm constructs a solution incrementally, at each step making the choice that looks best according to a local criterion and never revising it. It produces an optimal solution when the problem has optimal substructure and the greedy-choice property, which is typically established by an exchange argument (an optimal solution can be transformed, step by step, into the greedy one without loss) or by showing the greedy solution stays ahead. For example, selecting the compatible interval with the earliest finishing time maximises the number of non-overlapping intervals, and Huffman's algorithm builds optimal prefix codes. Greedy strategies fail for problems such as 0/1 knapsack, where dynamic programming is required.

## 8. Cheat sheet

| Problem | Sort key / tool |
|---|---|
| max non-overlapping | end time |
| merge intervals | start time |
| meeting rooms | start + heap of ends |
| cover a range | start, extend to the farthest end |
| jump game II | farthest reach per layer |
| gas station | reset the start when the tank < 0 |
| Huffman | heap of frequencies |
| minimise lateness | deadline (EDF) |

> [!INTERVIEW]
> **"Prove that earliest-end-first is optimal for interval scheduling."** Let g be the interval with the earliest end, and O an optimal schedule whose first interval is o. Since end(g) ≤ end(o), replacing o with g keeps O feasible (everything after o starts after end(o) ≥ end(g)) and doesn't change its size. So some optimal schedule starts with g. Remove the intervals overlapping g and apply induction to the rest. Interviewers want the exchange argument, not just the code.
