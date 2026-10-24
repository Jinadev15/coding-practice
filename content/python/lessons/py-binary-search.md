# Binary Search and Search on Answer

Binary search finds a boundary in a **monotone** sequence in O(log n) steps. That's 20 steps for a million items, 60 for 10¹⁸. Its real power goes far beyond "find x in a sorted list". Any question of the form "what is the smallest x such that `ok(x)` is true?" can be bisected, as long as `ok` is monotone. That turns hard optimisation problems ("minimum capacity", "maximum minimum distance", "smallest time") into a feasibility check plus a logarithmic search. Python ships the boundary search ready-made in `bisect`.

## 1. Think in boundaries, not "find x"

Picture a predicate over indices that looks like `F F F F T T T`. Binary search finds the **first T**. With the half-open invariant (everything before `lo` is F, everything from `hi` on is T), it's correct by construction:

```python
def first_true(lo, hi, ok):
    """Smallest x in [lo, hi) with ok(x) True, or hi if none. ok must be monotone F...F T...T."""
    while lo < hi:
        mid = (lo + hi) // 2          # Python ints don't overflow; in C/C++/Java use lo + (hi - lo) // 2
        if ok(mid):
            hi = mid                   # mid might be the answer
        else:
            lo = mid + 1               # mid is F: the answer is to the right
    return lo
```

`lower_bound(a, x)` is `first_true(0, len(a), lambda i: a[i] >= x)`, and `upper_bound` uses `a[i] > x`.

## 2. The `bisect` module

```python
import bisect

a = [1, 3, 3, 3, 7, 9]
bisect.bisect_left(a, 3)      # 1  first index with a[i] >= 3   (lower bound)
bisect.bisect_right(a, 3)     # 4  first index with a[i] > 3    (upper bound)
bisect.bisect_right(a, 3) - bisect.bisect_left(a, 3)   # 3 occurrences
bisect.insort(a, 5)           # insert keeping a sorted (O(n) for the shift, O(log n) to find)

# key= (Python 3.10+): search a list of records by a field
robots = [("arm", 2), ("rover", 5), ("drone", 9)]       # sorted by the second field
bisect.bisect_left(robots, 5, key=lambda r: r[1])       # 1
```

| Question | Expression |
|---|---|
| is x present? | `i = bisect_left(a, x); i < len(a) and a[i] == x` |
| count of x | `bisect_right(a, x) - bisect_left(a, x)` |
| count in [lo, hi] | `bisect_right(a, hi) - bisect_left(a, lo)` |
| largest element < x | `a[bisect_left(a, x) - 1]` if index ≥ 0 |
| smallest element > x | `a[bisect_right(a, x)]` if index < n |
| rank of x (#elements < x) | `bisect_left(a, x)` |

## 3. Search on the answer

**Pattern**: the answer is a number in a known range, and "can we achieve answer x?" is monotone. Then binary search over x, and run a greedy or linear check for each candidate.

```python
def ship_within_days(weights, days):
    """Minimum ship capacity to deliver the packages (in order) within `days` days."""
    def ok(cap):
        need, load = 1, 0
        for w in weights:
            if load + w > cap:
                need += 1
                load = 0
            load += w
        return need <= days
    return first_true(max(weights), sum(weights) + 1, ok)   # cap >= heaviest package; sum always works

ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)   # 15
```

The cost is O(n · log(sum)). Recognise the family:

| Problem | Search over | ok(x) |
|---|---|---|
| Koko eating bananas | speed | hours needed ≤ h |
| split array, minimise the largest sum | max sum | pieces needed ≤ k |
| aggressive cows / sensor placement (maximise the minimum gap) | gap | greedy placement fits k (monotone **decreasing**, so search for the last True) |
| minimum days to make m bouquets | day | bouquets by that day ≥ m |
| k-th smallest in a sorted matrix or a multiplication table | value | count of elements ≤ value ≥ k |
| median of two sorted arrays | partition index | left max ≤ right min |

> [!KEY]
> For "maximise x such that ok(x)", the predicate is `T T T F F`. Either search for the first False and subtract 1, or invert the predicate. Getting the direction and the off-by-one right is the whole difficulty. Test the two-element range in your head.

## 4. Real-valued bisection

For a continuous monotone function, bisect a fixed number of times instead of comparing to an epsilon:

```python
def sqrt_bisect(x, iters=100):
    lo, hi = 0.0, max(1.0, x)
    for _ in range(iters):               # each iteration halves the interval
        mid = (lo + hi) / 2
        if mid * mid < x: lo = mid
        else: hi = mid
    return lo
```

About 60 iterations reach full double precision on any reasonable interval. Use this for "minimum speed to arrive on time", physics root-finding, or tuning a parameter until a simulated robot just clears an obstacle.

## 5. Binary search on rotated and implicit structures

```python
def search_rotated(nums, target):        # distinct values, rotated sorted array
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:        # left half sorted
            if nums[lo] <= target < nums[mid]: hi = mid - 1
            else: lo = mid + 1
        else:                            # right half sorted
            if nums[mid] < target <= nums[hi]: lo = mid + 1
            else: hi = mid - 1
    return -1

def find_peak(nums):                     # any i with nums[i] > its neighbours: O(log n)
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]: lo = mid + 1     # an ascending slope leads to a peak on the right
        else: hi = mid
    return lo
```

Peak finding shows binary search doesn't even need sortedness, only a predicate that tells you which half must contain an answer.

## 6. Exam-ready answers

> [!EXAM]
> **Binary search on the answer.** When the solution to an optimisation problem is a value in a known range and the feasibility predicate "can the task be done with value x?" is monotone in x, the optimal value can be found by binary searching over the range, evaluating the predicate at each midpoint. This requires O(log R) feasibility checks for a range of size R, so an O(n) greedy check gives O(n log R) overall. Correctness depends on monotonicity and on maintaining an invariant over a half-open interval, such as "all values below lo are infeasible and hi is feasible".

## 7. Cheat sheet

```python
lo, hi = LOW, HIGH + 1            # half-open; HIGH must be feasible (or return hi = "none")
while lo < hi:
    mid = (lo + hi) // 2
    if ok(mid): hi = mid
    else: lo = mid + 1
answer = lo
```

| Need | Use |
|---|---|
| sorted list queries | `bisect_left` / `bisect_right` (with `key=` in 3.10+) |
| keep a list sorted | `insort` (O(n)) or `sortedcontainers.SortedList` (O(log n)) |
| optimisation with a monotone check | search on the answer |
| real numbers | fixed 60–100 iterations |

> [!INTERVIEW]
> **"Find the minimum in a rotated sorted array."** Compare `nums[mid]` with `nums[hi]`: if it's greater, the minimum is to the right (`lo = mid + 1`), otherwise it's at mid or to the left (`hi = mid`). That's O(log n). Comparing with `nums[hi]` instead of `nums[lo]` avoids a special case for an unrotated array. With duplicates, `nums[mid] == nums[hi]` forces `hi -= 1`, and the worst case degrades to O(n). Say so.
