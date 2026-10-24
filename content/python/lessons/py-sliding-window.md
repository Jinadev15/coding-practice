# Sliding Window

A **sliding window** is a contiguous subarray or substring `[left, right)` that moves across the input. Instead of recomputing each window from scratch (O(n·k) or O(n²)), you update the window's summary incrementally as one element enters on the right and another leaves on the left. That gives O(n). It's the standard tool for "longest/shortest/count of contiguous subarrays satisfying a condition" questions, and in robotics and signal processing it is literally how moving averages, rolling maxima and rate limiters work.

## 1. Fixed-size windows

```python
def max_window_sum(a, k):
    s = sum(a[:k])
    best = s
    for r in range(k, len(a)):
        s += a[r] - a[r - k]          # one element in, one out: O(1) per step
        best = max(best, s)
    return best
```

The same shape covers moving averages, counting anagram windows (keep a `Counter` of the window), and "maximum number of vowels in any window of length k".

## 2. Variable-size windows: expand right, shrink left

The general template for "**longest** window satisfying a condition":

```python
def longest_valid(a):
    left = 0
    best = 0
    state = ...                       # summary of a[left:right+1]
    for right, x in enumerate(a):
        add(x)                        # extend the window to include a[right]
        while not valid(state):       # shrink until valid again
            remove(a[left])
            left += 1
        best = max(best, right - left + 1)
    return best
```

> [!KEY]
> This works only if validity is **monotone under shrinking**: if a window is valid, every sub-window inside it is valid too. Then, for each `right`, the smallest valid `left` never moves backwards, and both pointers move at most n times, so it's O(n) total. If removing elements can make a window *invalid* (e.g. "sum exactly k" with negative numbers), the template breaks. Use prefix sums and a hash map instead (next lessons).

### Example: longest substring without repeating characters

```python
def longest_unique(s):
    last = {}                         # char -> last index seen
    left = best = 0
    for right, c in enumerate(s):
        if c in last and last[c] >= left:
            left = last[c] + 1        # jump left past the previous occurrence
        last[c] = right
        best = max(best, right - left + 1)
    return best

longest_unique("abcabcbb")   # 3 ("abc")
```

### Example: longest window with at most k distinct values

```python
from collections import defaultdict

def longest_k_distinct(a, k):
    count = defaultdict(int)
    left = best = 0
    for right, x in enumerate(a):
        count[x] += 1
        while len(count) > k:
            count[a[left]] -= 1
            if count[a[left]] == 0:
                del count[a[left]]
            left += 1
        best = max(best, right - left + 1)
    return best
```

## 3. Shortest window: shrink while valid

For "**shortest** window satisfying a condition", record the answer *inside* the shrink loop:

```python
def min_subarray_len(target, a):       # positive numbers: shortest subarray with sum >= target
    left = s = 0
    best = float("inf")
    for right, x in enumerate(a):
        s += x
        while s >= target:
            best = min(best, right - left + 1)
            s -= a[left]
            left += 1
    return 0 if best == float("inf") else best
```

**Minimum window substring** (the smallest window of `s` containing every character of `t` with multiplicity) uses the same shape. Track `need = Counter(t)` and `missing = len(t)`. Decrement `missing` when a needed character enters, and shrink while `missing == 0`. That's O(|s| + |t|).

## 4. Counting windows: "at most k" minus "at most k−1"

"Number of subarrays with **exactly** k distinct values" isn't monotone directly. But "at most k" is, and for each `right`, every window `[left..right]` with left in the valid range counts, which adds `right - left + 1` windows:

```python
def at_most(a, k):
    count, left, total = defaultdict(int), 0, 0
    for right, x in enumerate(a):
        count[x] += 1
        while len(count) > k:
            count[a[left]] -= 1
            if not count[a[left]]: del count[a[left]]
            left += 1
        total += right - left + 1
    return total

def exactly(a, k):
    return at_most(a, k) - at_most(a, k - 1)
```

## 5. Sliding window maximum: the monotonic deque

The maximum of each window of size k in O(n). Keep a `deque` of **indices** whose values are decreasing. The front is always the current maximum:

```python
from collections import deque

def window_max(a, k):
    dq, out = deque(), []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x:     # x dominates smaller elements: they can never be a max again
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:               # the front fell out of the window
            dq.popleft()
        if i >= k - 1:
            out.append(a[dq[0]])
    return out

window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)   # [3, 3, 5, 5, 6, 7]
```

Each index is pushed and popped at most once, so it's O(n) total. In robotics, this is how you compute a rolling peak of a sensor signal or a min-filter for obstacle distances in real time.

## 6. Recognising the pattern

| Clue | Window type |
|---|---|
| "subarray/substring of length k" | fixed |
| "longest … such that …" (monotone) | expand right, shrink while invalid |
| "shortest … such that …" (monotone) | expand right, shrink while valid |
| "number of subarrays with at most …" | add `right - left + 1` per step |
| "exactly k" | at_most(k) − at_most(k − 1) |
| "max/min of every window" | monotonic deque |
| negative numbers + exact sum | **not** a window: prefix sums + hash map |

## 7. Exam-ready answers

> [!EXAM]
> **The sliding window technique.** A sliding window maintains a contiguous range of a sequence, together with an incrementally updated summary such as a sum, a frequency table or a monotonic deque. As the right boundary advances, one element enters; when the window violates (or, for minimisation, satisfies) a condition, the left boundary advances and elements leave. Because each boundary only moves forward, every element is added and removed at most once, giving O(n) time instead of re-evaluating all O(n²) subarrays. The technique requires the condition to be monotone with respect to shrinking the window; for conditions such as an exact sum with negative values, prefix sums with hashing are used instead.

## 8. Cheat sheet

```python
left = 0
for right, x in enumerate(a):
    add(x)
    while invalid():          # or: while valid(): record; then shrink
        remove(a[left]); left += 1
    record(right - left + 1)
```

> [!INTERVIEW]
> **"Why is the nested `while` still O(n)?"** Because `left` only increases and never exceeds `right`, the inner loop's body runs at most n times **in total** across the whole outer loop, not n times per outer iteration. This amortised argument is the key point to explain for any two-pointer or sliding-window solution.
