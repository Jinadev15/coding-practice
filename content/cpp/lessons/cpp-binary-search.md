# Binary Search on Indices

Binary search finds things in **sorted** data in O(log n): about 20 steps for a million elements, and 60 for 10¹⁸. The idea is simple, yet binary search is famous for off-by-one bugs: Jon Bentley found that most professional programmers couldn't write it correctly. This lesson gives you **one template you can trust**, explains why it is correct, and covers the variations interviews love: first/last occurrence, insertion point, rotated arrays, peaks, and 2D matrices.

## 1. The idea

Looking up a word in a dictionary, you open the middle, see whether your word comes before or after, and throw away half the book. Every comparison **halves** the remaining range.

```text
find 23 in [2 5 8 12 16 23 38 56 72 91]
lo=0 hi=9  mid=4 (16) < 23 → search right half: lo=5
lo=5 hi=9  mid=7 (56) > 23 → search left half:  hi=6
lo=5 hi=6  mid=5 (23) == 23 → found at index 5
```

After `k` steps, `n / 2^k` elements remain, so `log₂ n` steps suffice.

## 2. Think in terms of a predicate, not "equals"

The most robust way to think about binary search is this:

> Find the **first index where a condition becomes true**, given that the condition is `false false … false true true … true` along the array (it is *monotone*).

For a sorted array, the condition `a[i] >= x` is monotone. Its first true index is exactly `std::lower_bound`.

```cpp
// first index in [0, n) where pred(i) is true; returns n if it is never true
template <class P>
int first_true(int n, P pred) {
    int lo = 0, hi = n;                  // the answer lies in [lo, hi]; hi = n means "not found"
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;    // lo <= mid < hi
        if (pred(mid)) hi = mid;         // mid might be the answer: keep it
        else lo = mid + 1;               // mid is false: the answer is to the right
    }
    return lo;                           // lo == hi
}
```

> [!KEY] Why this template can't loop forever or skip the answer
> - **Invariant:** everything before `lo` is false, and everything from `hi` onward is true (or past the end).
> - `mid` is always strictly less than `hi`, so `hi = mid` shrinks the range, and `lo = mid + 1` shrinks it too.
> - When `lo == hi`, the invariant says that index is the first true one.
>
> Using the half-open `[lo, hi)` style with `hi = n` handles the "not found" case without any special code.

**`mid = lo + (hi − lo) / 2`**, not `(lo + hi) / 2`. The sum can overflow when the indices or values are large, a bug that sat in Java's standard library for nine years.

## 3. The four classic queries on a sorted array

| Question | Predicate | STL |
|---|---|---|
| first element ≥ x (insertion point) | `a[i] >= x` | `lower_bound` |
| first element > x | `a[i] > x` | `upper_bound` |
| last element ≤ x | (first `a[i] > x`) − 1 | `upper_bound − 1` |
| last element < x | (first `a[i] >= x`) − 1 | `lower_bound − 1` |

- **Count of x** = `upper_bound(x) − lower_bound(x)`.
- **Does x exist?** `lo < n && a[lo] == x`, where `lo = lower_bound(x)`.

```cpp
auto lo = lower_bound(v.begin(), v.end(), x);       // iterator; v must be sorted with the same ordering
int idx = lo - v.begin();
bool found = lo != v.end() && *lo == x;
int count = upper_bound(v.begin(), v.end(), x) - lo;
```

## 4. Rotated sorted arrays

`[4 5 6 7 0 1 2]` is a sorted array rotated at some point. At any `mid`, **one of the two halves is sorted**:

- If `a[lo] <= a[mid]`, the left half `[lo, mid]` is sorted.
- Otherwise the right half `[mid, hi]` is sorted.

Check whether the target lies within the sorted half's range. If it does, search there. Otherwise search the other half.

**The minimum of a rotated array** (the rotation point) is the first index where `a[i] <= a[n−1]`, which is a monotone predicate. So use the template directly.

With **duplicates** (`[2 2 2 0 2]`) you can't always tell which half is sorted. When `a[lo] == a[mid] == a[hi]`, shrink both ends by one. The worst case degrades to O(n).

## 5. Peaks and bitonic arrays

A **peak** is an element larger than its neighbours. In `[1 3 5 4 2]`, 5 is a peak. Even in an unsorted array you can find *a* peak in O(log n): if `a[mid] < a[mid+1]`, the slope goes up to the right, so some peak lies to the right. Otherwise one lies at `mid` or to its left. The predicate "`a[i] > a[i+1]`" is monotone on the path the search follows, and the template finds the first descent.

**Bitonic arrays** (increasing, then decreasing) work the same way: find the peak, then binary search each monotone side.

## 6. Searching in 2D

- **The matrix is fully sorted** (each row continues where the previous one ended): treat it as one array of `R·C` elements, with index `k → (k / C, k % C)`.
- **Rows and columns are each sorted:** start at the **top-right** corner. If the value is too big, move left. If it's too small, move down. That's an O(R + C) staircase walk, which isn't binary search, but is the classic trick.
- **k-th smallest in a sorted matrix:** binary search on the *value*, counting how many entries are ≤ mid with a staircase walk. That's "binary search on the answer", the next topic.

## 7. Binary search over real numbers

For a monotone function on reals (e.g. `x² = 2`), loop a fixed number of times instead of comparing floating-point values with `==`:

```cpp
double lo = 0, hi = 2;
for (int it = 0; it < 100; ++it) {               // each step halves the error: 2/2^100 is tiny
    double mid = (lo + hi) / 2;
    if (mid * mid < 2) lo = mid; else hi = mid;
}
```

## 8. Recognising binary search

- The input is **sorted**, or the problem mentions logarithmic time.
- "First/last position", "insert position", "how many are less than x".
- A question about a huge range (10⁹, 10¹⁸) where you can **test** a candidate answer cheaply. That's binary search on the answer (next topic).
- "Rotated", "peak", "mountain array".

## 9. Common mistakes

- **Infinite loops** from `lo = mid` with `mid` rounded down, or a `while (lo <= hi)` / `hi = mid` mismatch. Use one template consistently.
- **Off-by-one** in "last ≤ x". Derive it as (first > x) − 1.
- **Overflow** in `lo + hi`.
- **Searching unsorted data,** or data sorted with a different comparator than the one you search with.
- **`std::binary_search` only returns a bool.** Use `lower_bound` when you need the position.

## 10. Interview questions

> [!INTERVIEW] "Find the first and last position of x in a sorted array."
> Two binary searches: lower_bound(x) for the first index ≥ x, and upper_bound(x) − 1 for the last index ≤ x. If lower_bound is past the end or doesn't equal x, the answer is not found. That's O(log n). Explain the invariant (everything before lo is < x, everything from hi on is ≥ x) to show why it terminates correctly.

> [!EXAM] Why must you compute mid as lo + (hi − lo) / 2?
> lo + hi can exceed the integer range when the bounds are large (e.g. searching a value range up to 2·10⁹ with int, or up to 10¹⁸ with long long). The difference form never exceeds hi, so it can't overflow.

## Check your understanding

1. In `[1 2 2 2 3]`, what are lower_bound(2), upper_bound(2) and the count of 2?
2. In the template, why is it `hi = mid` and not `hi = mid − 1`?
3. Which half of `[6 7 1 2 3 4 5]` is sorted at mid = 3?

<details><summary>Answers</summary>

1. 1, 4 and 3.
2. mid itself satisfies the predicate and might be the first true index, so it must stay inside the range.
3. a[lo] = 6 > a[mid] = 2, so the left half isn't sorted, but the right half [2 3 4 5] is.

</details>
