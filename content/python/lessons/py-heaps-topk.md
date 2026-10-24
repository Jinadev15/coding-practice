# Heaps and Top-K

A **binary heap** is a complete binary tree stored in an array where each parent is ≤ its children (a min-heap). It gives O(1) access to the minimum and O(log n) insert and remove-min. That's exactly the **priority queue** you need for Dijkstra and A* path planning, event-driven simulation, job scheduling by deadline, streaming top-k, merging sorted streams, and running medians. Python's `heapq` module implements a min-heap on a plain list.

## 1. `heapq` essentials

```python
import heapq

h = []
heapq.heappush(h, 5)
heapq.heappush(h, 1)
heapq.heappush(h, 3)
h[0]                      # 1: peek at the minimum, O(1)
heapq.heappop(h)          # 1: O(log n)

a = [9, 4, 7, 1, 8]
heapq.heapify(a)          # in place, O(n)
heapq.heappushpop(a, 6)   # push then pop, faster than the two separately
heapq.heapreplace(a, 2)   # pop then push (returns the old minimum)
heapq.nlargest(3, [5, 1, 9, 7, 3])          # [9, 7, 5]
heapq.nsmallest(2, robots, key=lambda r: r.battery)
heapq.merge([1, 4, 9], [2, 3, 10])          # lazy merge of sorted iterables
```

> [!KEY]
> `heapq` is a **min**-heap only. For a max-heap, push negated keys (`-priority`). For ties, push tuples `(priority, counter, item)`: the counter (from `itertools.count()`) keeps equal priorities in FIFO order and stops Python from comparing the items themselves, which raises `TypeError` for non-comparable objects.

## 2. How it works

For index i (0-based), the parent is `(i - 1) // 2` and the children are `2i + 1` and `2i + 2`. Push appends and **sifts up**. Pop moves the last element to the root and **sifts down**. Both are O(log n).

`heapify` is **O(n)**, not O(n log n). It sifts down from the last parent to the root. Most nodes are near the bottom and move only a little: the sum over levels of (nodes at height h) × h = O(n).

## 3. Top-k: a heap of size k

The k largest elements of a stream of n in O(n log k) time and O(k) memory:

```python
def top_k(stream, k):
    h = []
    for x in stream:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:                  # better than the worst of the current top k
            heapq.heapreplace(h, x)
    return sorted(h, reverse=True)
```

The heap's **root is the smallest of the top k**: the gatekeeper. That's counter-intuitive (a *min*-heap for the *largest* items) but correct. For the k closest points or the k smallest values, use a max-heap of size k (negated keys).

| Approach | Time | When |
|---|---|---|
| sort, then slice | O(n log n) | small n, or you need everything sorted anyway |
| heap of size k | O(n log k) | streams, k ≪ n |
| `heapq.nlargest` | O(n log k) | the convenient form of the above |
| quickselect | O(n) average | an array in memory, only the k-th or an unordered top k |

**Top-k frequent**: `Counter(words).most_common(k)` uses `nlargest` internally. Bucket sort by frequency is O(n).

## 4. K-way merge

```python
def merge_k_sorted(lists):
    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(h)
    out = []
    while h:
        val, i, j = heapq.heappop(h)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(h, (lists[i][j + 1], i, j + 1))
    return out
```

That's O(N log k). It's used for external sorting, merging time-stamped sensor logs from several robots, and the "smallest range covering k lists" problem.

## 5. Running median: two heaps

Keep the lower half in a max-heap and the upper half in a min-heap, with their sizes balanced:

```python
class RunningMedian:
    def __init__(self):
        self.lo, self.hi = [], []           # lo: max-heap via negation; hi: min-heap
    def add(self, x):
        heapq.heappush(self.lo, -x)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))   # move the largest of lo to hi
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))
    def median(self):
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2
```

Each add is O(log n) and each median query O(1). That's a streaming median filter for noisy sensor readings. For a **sliding-window** median, you also need deletion: use **lazy deletion** (a dict of pending removals that are discarded when they reach a heap top) or a `SortedList`.

## 6. Scheduling and simulation

```python
import itertools

def simulate(events):
    """events: (time, name). Process in time order; handlers may schedule more."""
    counter = itertools.count()
    pq = [(t, next(counter), name) for t, name in events]
    heapq.heapify(pq)
    while pq:
        t, _, name = heapq.heappop(pq)
        if name == "sensor":
            if t < 3:
                heapq.heappush(pq, (t + 1, next(counter), "sensor"))   # periodic event
        print(t, name)
```

Discrete-event simulators, OS schedulers, timer wheels and the "task scheduler with cooldown" and "meeting rooms II" problems (a min-heap of end times) all use this structure.

### Updating priorities

`heapq` can't decrease a key in place. The standard workaround (used by Dijkstra in Python) is to **push a new entry and skip stale ones** when popped:

```python
d, u = heapq.heappop(pq)
if d > dist[u]:
    continue                 # outdated entry
```

## 7. Exam-ready answers

> [!EXAM]
> **Binary heaps and priority queues.** A binary heap is a complete binary tree, usually stored implicitly in an array, satisfying the heap property: each node's key is no greater (min-heap) or no smaller (max-heap) than its children's. The extreme element is at the root and is read in O(1); insertion appends and sifts up, and removal of the root moves the last element to the root and sifts down, both in O(log n); building a heap from n elements by bottom-up sifting takes O(n). Heaps implement priority queues used in Dijkstra's algorithm, event simulation, scheduling, k-way merging and streaming top-k selection, where a heap of size k gives O(n log k) time.

## 8. Cheat sheet

| Need | Code |
|---|---|
| min-heap | `heappush` / `heappop` / `h[0]` |
| max-heap | push `-x` |
| ties / unorderable items | `(priority, next(counter), item)` |
| top k largest | a min-heap of size k, or `nlargest` |
| merge sorted streams | a heap of (value, list index, position), or `heapq.merge` |
| running median | two heaps |
| decrease-key | push a new entry, skip stale ones |

> [!INTERVIEW]
> **"Find the k-th largest element in an array."** Options: sort, O(n log n); a min-heap of size k, O(n log k), which works for streams; quickselect, O(n) average and O(n²) worst (randomised pivot or median-of-medians for a guaranteed O(n)). State the trade-offs and pick the heap for streaming data, quickselect for a one-off in memory.
