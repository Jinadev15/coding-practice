# Two Pointers

Many array and string problems ask about **pairs** or **ranges**. The brute force tries all of them, at O(n²). The **two-pointer** technique keeps two indices that move monotonically, so each moves at most n times, and solves these problems in O(n) with O(1) extra space. Recognising when it applies is a core interview skill. The trick is always an invariant that lets you discard a whole set of pairs with one comparison.

## 1. Pattern A: opposite ends on sorted data

Find a pair summing to `target` in a **sorted** array:

```python
def pair_sum(a, target):
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:
            return i, j
        if s < target:
            i += 1          # a[i] is too small even with the LARGEST partner a[j]: discard all pairs with i
        else:
            j -= 1          # a[j] is too big even with the SMALLEST partner a[i]: discard all pairs with j
    return None
```

> [!KEY]
> **Why it's correct**: when `a[i] + a[j] < target`, every pair `(i, k)` with `k ≤ j` also sums to less than target, because the array is sorted. So index i can never be part of a solution, and we discard n − i pairs in O(1). Each step discards a row or a column of the pair matrix, which gives n steps in total.

### Extensions

| Problem | Idea |
|---|---|
| 3-sum (all unique triples summing to 0) | sort, fix `k`, run pair_sum on the rest, skip duplicates. O(n²) |
| closest pair sum | the same loop, tracking the best `abs(s - target)` |
| container with most water | move the pointer at the **shorter** wall: the taller one can't do better with a narrower width |
| trapping rain water | move the side with the smaller max, tracking `left_max`/`right_max` |
| valid palindrome | compare the ends, move inwards |

```python
def three_sum(nums):
    nums.sort()
    out = []
    for k in range(len(nums) - 2):
        if k and nums[k] == nums[k - 1]:
            continue                                  # skip duplicate anchors
        i, j = k + 1, len(nums) - 1
        while i < j:
            s = nums[k] + nums[i] + nums[j]
            if s < 0: i += 1
            elif s > 0: j -= 1
            else:
                out.append((nums[k], nums[i], nums[j]))
                i += 1
                while i < j and nums[i] == nums[i - 1]:
                    i += 1                            # skip duplicate second elements
    return out
```

## 2. Pattern B: same direction (reader/writer, fast/slow)

**In-place compaction**: the `write` pointer marks the end of the kept prefix, and the `read` pointer scans:

```python
def remove_duplicates_sorted(a):          # returns the new length; a[:k] holds the unique values
    if not a:
        return 0
    w = 1
    for r in range(1, len(a)):
        if a[r] != a[w - 1]:
            a[w] = a[r]
            w += 1
    return w

def move_zeros(a):                         # stable: keep non-zero order, zeros at the end
    w = 0
    for r in range(len(a)):
        if a[r] != 0:
            a[w], a[r] = a[r], a[w]
            w += 1
```

**Merging** two sorted arrays: one pointer in each, and always take the smaller element. That's O(n + m), and it's the heart of merge sort. Merging **in place from the back** (LeetCode "merge sorted array") avoids overwriting unread data.

**Partitioning**: the Dutch national flag (three-way partition) keeps `lo`, `mid` and `hi`:

```python
def sort_colors(a):                        # values 0, 1, 2 in one pass
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if a[mid] == 0:
            a[lo], a[mid] = a[mid], a[lo]; lo += 1; mid += 1
        elif a[mid] == 1:
            mid += 1
        else:
            a[mid], a[hi] = a[hi], a[mid]; hi -= 1     # don't advance mid: the swapped-in value is unchecked
```

## 3. Pattern C: fast and slow pointers on sequences

Floyd's cycle detection works on linked lists, and on any function `x → f(x)` over a finite set:

```python
def find_duplicate(nums):          # n+1 values in 1..n, exactly one repeated; O(1) space, no mutation
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]                  # phase 2: the distance from the start = the distance from the meeting point
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
```

Also: the middle of a linked list (fast moves 2, slow moves 1), the k-th from the end (lead by k), and "happy number" cycle detection.

## 4. When two pointers apply

> [!TIP]
> Look for one of these:
> - sorted input, or input you may sort
> - a question about pairs or triples with a monotone condition
> - in-place rearrangement with O(1) space
> - two sequences to merge or compare
>
> If the condition isn't monotone (e.g. pair sum in an **unsorted** array where you must return the original indices), use a hash map instead: one pass, O(n) time and O(n) space.

## 5. Exam-ready answers

> [!EXAM]
> **The two-pointer technique.** The two-pointer technique maintains two indices into a sequence that move monotonically, either towards each other from the ends or in the same direction, so that each index advances at most n times and the algorithm runs in O(n) time with O(1) extra space. Its correctness rests on an invariant that lets each comparison eliminate a whole family of candidates: in a sorted array, if `a[i] + a[j]` is less than the target, no pair involving i with any index up to j can reach it, so i can be advanced. Typical applications are pair and triple sums in sorted arrays, in-place removal and partitioning, merging sorted sequences, palindrome checks, and cycle detection with fast and slow pointers.

## 6. Cheat sheet

| Problem | Pointers | Time |
|---|---|---|
| pair sum (sorted) | ends, move inwards | O(n) |
| 3-sum | sort + anchor + ends | O(n²) |
| remove duplicates / zeros | read/write | O(n) |
| merge sorted | one per array | O(n + m) |
| 3-way partition | lo/mid/hi | O(n) |
| cycle / duplicate | fast/slow | O(n) |
| container with most water | ends, move the shorter | O(n) |

> [!INTERVIEW]
> **"Two-sum: hash map or two pointers?"** If the input is unsorted and you need the original indices: a hash map, O(n) time and O(n) space. If it's already sorted, or you only need the values: two pointers, O(n) time and O(1) space. Sorting first costs O(n log n). State the trade-off, then pick based on the constraints.
