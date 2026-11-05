# Intervals and Sweep Line

Calendars, bookings, CPU jobs, genome ranges and robot time windows are all **intervals** `[start, end]`. Interval problems look varied, but almost all of them reduce to two ideas:

1. **Sort the intervals** (by start, or by end), then make one greedy pass.
2. **Sweep line:** turn each interval into two **events** (+1 at its start, −1 at its end), sort the events, and walk through time keeping a running count.

## 1. Representing intervals and the overlap test

```cpp
struct Interval { long long s, e; };          // decide: closed [s, e] or half-open [s, e)?
```

**Decide whether the endpoints touch.** Do `[1,3]` and `[3,5]` overlap?

- With **closed** intervals (meetings that include their end minute), they do.
- With **half-open** `[s, e)` intervals (a booking that ends exactly when the next one starts), they don't.

Many bugs come from mixing the two. The statement always tells you which one you have.

Two intervals overlap exactly when **each starts before the other ends**:

```cpp
bool overlap_closed(Interval a, Interval b)    { return a.s <= b.e && b.s <= a.e; }
bool overlap_halfopen(Interval a, Interval b)  { return a.s <  b.e && b.s <  a.e; }
```

It's easier to reason about *not* overlapping: one interval ends before the other starts. The overlap test is the negation of that.

## 2. Merging overlapping intervals

Sort by start. Walk through the intervals, extending the last merged interval while the next one overlaps it:

```cpp
vector<Interval> merge(vector<Interval> v) {
    sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.s < b.s; });
    vector<Interval> out;
    for (auto& cur : v) {
        if (!out.empty() && cur.s <= out.back().e)          // overlaps (closed): extend
            out.back().e = max(out.back().e, cur.e);         // max: cur may be nested inside
        else out.push_back(cur);
    }
    return out;
}
```

```text
input:  [1,3] [8,10] [2,6] [15,18]
sorted: [1,3] [2,6] [8,10] [15,18]
        [1,3]+[2,6] → [1,6];  [8,10] new;  [15,18] new   →  [1,6] [8,10] [15,18]
```

**Why sorting by start is enough:** after sorting, an interval can only overlap the merged block immediately before it. Every earlier block ended before that block started.

Related tasks:

- **Inserting** a new interval into a sorted, disjoint list is one linear pass: copy the intervals entirely before it, merge the ones that overlap it, then copy the rest.
- **Intersecting** two sorted interval lists uses two pointers: the overlap of the current pair is `[max(s), min(e)]`, and you advance whichever interval ends first.

## 3. Greedy by end time: activity selection

**The maximum number of non-overlapping intervals** (equivalently, the fewest removals to make the rest disjoint): sort by **end** time, and repeatedly take the interval that finishes first among those that start after the last taken one ends.

```cpp
int max_disjoint(vector<Interval> v) {                   // half-open: touching is fine
    sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.e < b.e; });
    int cnt = 0; long long last_end = LLONG_MIN;
    for (auto& x : v) if (x.s >= last_end) { ++cnt; last_end = x.e; }
    return cnt;
}
```

> [!KEY] Exchange argument
> Take any optimal set, and compare its first interval with the one that ends earliest overall. Replacing its first interval with the earliest-ending one keeps the set disjoint, because that interval ends no later. Repeating the argument shows that greedy-by-end is optimal. Sorting by *start* or by *length* fails. Try `[1,10] [2,3] [4,5]`.

**The minimum number of points that hit every interval** (also called "minimum arrows to burst balloons") uses the same greedy. Shoot at the end of the earliest-ending interval that hasn't been hit yet.

## 4. Sweep line: counting overlaps

**What is the maximum number of meetings at the same time (the minimum number of rooms)?** Turn each meeting into events: `(start, +1)` and `(end, −1)`. Sort the events by time and sweep, keeping a running count. The peak count is the answer.

```cpp
int min_rooms(const vector<Interval>& v) {               // half-open [s, e)
    vector<pair<long long,int>> ev;
    for (auto& x : v) { ev.push_back({x.s, +1}); ev.push_back({x.e, -1}); }
    sort(ev.begin(), ev.end());                          // at equal times, -1 sorts before +1
    int cur = 0, best = 0;
    for (auto& [t, d] : ev) { cur += d; best = max(best, cur); }
    return best;
}
```

**Ties decide the semantics:**

- Half-open `[s, e)`: a meeting ending at 10 frees its room for one starting at 10. Process `−1` **before** `+1` at the same time, which happens naturally when sorting pairs, since −1 < +1.
- Closed `[s, e]`: process `+1` first.

An equivalent approach sorts the starts and the ends separately and uses two pointers, or uses a **min-heap of end times** (pop the rooms that have freed up, push the current meeting). The heap version can also tell you *which* room each meeting gets.

## 5. Sweep line with a data structure

Sweeps get stronger when the "running state" is richer than a count:

- **The skyline problem:** events are building edges, and the state is a multiset of active heights. The maximum height changes exactly at the skyline's key points.
- **Total length covered by a union of intervals:** sweep the sorted events, and add `(t − prev_t)` whenever the active count is positive.
- **Rectangle union area:** sweep in x while keeping the covered length in y, with a segment tree (an advanced topic).

## 6. Coordinate compression

When coordinates are huge (up to 10¹⁸) but there are few of them, map the distinct coordinates to `0..m−1`:

```cpp
vector<long long> xs = all_coordinates;
sort(xs.begin(), xs.end());
xs.erase(unique(xs.begin(), xs.end()), xs.end());
auto id = [&](long long x) { return lower_bound(xs.begin(), xs.end(), x) - xs.begin(); };
```

Then difference arrays or prefix sums work over the `m` compressed points instead of a huge range.

## 7. Pattern recognition

| Question | Technique |
|---|---|
| merge / union of intervals, insert into a sorted list | sort by start, linear pass |
| maximum non-overlapping, minimum removals, minimum points to hit all | sort by **end**, greedy |
| maximum overlap, minimum rooms, "is anyone double-booked?" | sweep events (or a heap of end times) |
| intersection of two interval lists | two pointers |
| free time common to everyone | merge all busy intervals, then report the gaps |
| huge coordinates | coordinate compression + sweep / difference array |

## 8. Complexity

Sorting dominates: **O(n log n)**. The sweep itself is O(n), plus O(log n) per event with a heap or multiset.

## 9. Common mistakes

- **Mixing closed and half-open semantics,** especially in the overlap test and in event tie-breaking.
- **Merging without `max`:** `out.back().e = cur.e` breaks when `cur` is nested inside the previous interval.
- **Greedy by start (or by length)** for activity selection. You must sort by end.
- **Comparators with `<=`,** which is undefined behaviour in `std::sort`.
- **Overflow** when coordinates or lengths reach 10¹⁸. Use `long long`, or `__int128` for products.

## 10. Interview questions

> [!INTERVIEW] "Minimum number of meeting rooms?"
> Turn each meeting into start/end events, sort them by time with ends before starts at equal times (half-open meetings), and sweep with a counter. The peak is the answer. Alternatively, sort by start and keep a min-heap of the end times of rooms in use: pop every room that has ended before the current start, then push the current end. The heap's maximum size is the answer. Both are O(n log n).

> [!EXAM] Why is "sort by end time" optimal for the maximum number of non-overlapping intervals?
> By the exchange argument: the interval that finishes first leaves the most room for the rest. Any optimal solution's first interval can be swapped for it without creating an overlap, and induction on the remaining intervals completes the proof.

## Check your understanding

1. Merge `[1,4] [2,3] [5,7] [6,6]` (closed intervals).
2. Minimum rooms for `[0,30) [5,10) [15,20)`?
3. Why does `[1,10] [2,3] [4,5]` break "greedy by start time"?

<details><summary>Answers</summary>

1. `[1,4] [5,7]`. Note `[2,3]` is nested inside `[1,4]`, and `[6,6]` inside `[5,7]`.
2. 2: `[0,30)` overlaps each of the others, but those two don't overlap each other.
3. Greedy by start picks `[1,10]` first and blocks both others (1 interval). Greedy by end picks `[2,3]` and then `[4,5]` (2 intervals).

</details>
