# Searching and Binary Search

Searching asks "where is it?" or "is it there?". On unsorted data, the answer costs a linear scan. On sorted data, **binary search** answers in O(log n): 20 comparisons for a million elements, 30 for a billion. But binary search is famously easy to get *slightly* wrong. Jon Bentley found that most professional programmers couldn't write a correct one, and Java's library version carried an overflow bug for nine years. This lesson gives you a method that makes it correct by construction, plus the generalisation that solves a whole class of optimisation problems: **binary search on the answer**.

## 1. Linear search, done well

```c
/* returns the index of key, or -1 */
ptrdiff_t linear_search(const int *a, size_t n, int key) {
    for (size_t i = 0; i < n; i++)
        if (a[i] == key) return (ptrdiff_t)i;
    return -1;
}
```

Linear search is O(n) and needs no ordering, and for small arrays (tens of elements) it often **beats** binary search, thanks to sequential memory access and predictable branches. A **sentinel** variant writes `key` past the end so the loop needs only one comparison per element. That's a classic micro-optimisation.

## 2. Binary search with invariants

Think of a sorted array as a predicate that is `false…false true…true`. For "first element ≥ key", the predicate is `a[i] >= key`. Binary search finds the **boundary**. Keep a half-open range `[lo, hi)` and an invariant:

> everything before `lo` is `< key`, everything from `hi` on is `>= key`.

```c
/* lower_bound: first index i with a[i] >= key, or n if none. */
size_t lower_bound(const int *a, size_t n, int key) {
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;     /* no overflow, unlike (lo + hi) / 2 */
        if (a[mid] < key) lo = mid + 1;      /* mid is < key: the boundary is right of mid */
        else              hi = mid;          /* mid is >= key: it could be the answer */
    }
    return lo;                               /* lo == hi: the boundary */
}

/* upper_bound: first index i with a[i] > key. */
size_t upper_bound(const int *a, size_t n, int key) {
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (a[mid] <= key) lo = mid + 1;
        else               hi = mid;
    }
    return lo;
}
```

From these two, everything follows:

| Question | Answer |
|---|---|
| is `key` present? | `i = lower_bound(...); i < n && a[i] == key` |
| first occurrence | `lower_bound` (if present) |
| last occurrence | `upper_bound - 1` (if present) |
| count of `key` | `upper_bound - lower_bound` |
| insertion point that keeps order | `lower_bound` (or `upper_bound` to insert after equals) |
| largest element < key | `lower_bound - 1` (if ≥ 0) |
| number of elements in `[x, y]` | `upper_bound(y) - lower_bound(x)` |

> [!KEY]
> Correctness checklist:
> 1. The loop **terminates**: each iteration strictly shrinks `[lo, hi)`, because `mid < hi` and `lo = mid + 1 > mid`.
> 2. The invariant holds initially (empty prefix and suffix) and is preserved by both branches.
> 3. At the end, `lo == hi` is the boundary.
>
> Mixing conventions (closed `[lo, hi]` with `hi = mid`) is what produces infinite loops and off-by-one errors.

> [!DANGER]
> `mid = (lo + hi) / 2` overflows when `lo + hi` exceeds the type's maximum. With `int` indices on arrays over 2³⁰ elements, that's UB and a negative index. With `size_t`, it wraps around. Always write `lo + (hi - lo) / 2`.

## 3. `bsearch` from the standard library

```c
void *bsearch(const void *key, const void *base, size_t nmemb, size_t size,
              int (*compar)(const void *key, const void *elem));
```

```c
int key = 42;
int *p = bsearch(&key, a, n, sizeof *a, cmp_int);
if (p) printf("found at %td\n", p - a);
```

`bsearch` returns **some** matching element (not necessarily the first) or `NULL`. Use your own `lower_bound` when you need the first or last occurrence or an insertion point. The comparator's first argument is always the key, so you can search an array of structs by a bare key:

```c
typedef struct { int id; const char *name; } Robot;
static int cmp_id_key(const void *k, const void *e) {
    int id = *(const int *)k, eid = ((const Robot *)e)->id;
    return (id > eid) - (id < eid);
}
Robot *r = bsearch(&wanted, fleet, n, sizeof *fleet, cmp_id_key);
```

## 4. Binary search on the answer

Many optimisation problems have the form "find the smallest x such that `feasible(x)` is true", where feasibility is **monotone**: once true, it stays true for every larger x. Binary search the value of x instead of an index:

```c
/* Smallest max-load L such that the packages (in order) fit into at most D trucks. */
static int feasible(const int *w, size_t n, long long L, int D) {
    int trucks = 1; long long load = 0;
    for (size_t i = 0; i < n; i++) {
        if (w[i] > L) return 0;
        if (load + w[i] > L) { trucks++; load = 0; }
        load += w[i];
    }
    return trucks <= D;
}

long long min_capacity(const int *w, size_t n, int D) {
    long long lo = 1, hi = 0;
    for (size_t i = 0; i < n; i++) hi += w[i];       /* one truck always works */
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (feasible(w, n, mid, D)) hi = mid;        /* mid works: the answer is <= mid */
        else lo = mid + 1;
    }
    return lo;
}
```

The cost is O(n · log(sum)). The same pattern solves "minimum time to finish all jobs with k workers", "maximum minimum distance between placed sensors", "smallest speed to arrive on time" and "k-th smallest value in a sorted matrix".

### Real-valued answers

For continuous problems (e.g. "find the tension where the cable sag equals 2 m"), bisect a fixed number of times instead of comparing with an epsilon:

```c
double lo = 0.0, hi = 1e6;
for (int it = 0; it < 100; it++) {          /* each step halves the interval: 2^-100 · 1e6 */
    double mid = 0.5 * (lo + hi);
    if (f(mid) >= target) hi = mid; else lo = mid;
}
```

That's the **bisection method** for root finding: slow (one bit per step) but unconditionally convergent for a continuous function that changes sign. Newton's method is faster but can diverge.

## 5. Other searches worth knowing

| Technique | Use |
|---|---|
| **Exponential (galloping) search** | unbounded or huge sorted data: probe 1, 2, 4, 8, … until you overshoot, then binary search. O(log i) for an answer at position i. Timsort uses it when merging. |
| **Interpolation search** | uniformly distributed keys: guess the position proportionally. O(log log n) average, O(n) worst case. |
| **Ternary search** | the maximum of a **unimodal** function. (On integers, binary search on the sign of `f(m+1) - f(m)` is cleaner.) |
| **Search in a rotated sorted array** | compare `a[mid]` with `a[hi]` to tell which half is sorted. |
| **2-D sorted matrix** | start at the top-right corner: move left if bigger, down if smaller. O(rows + cols). |
| **Hash table** | O(1) average lookup, unordered (Data Structures module). |

## 6. Exam-ready answers

> [!EXAM]
> **Binary search.** Binary search locates a key in a sorted array by repeatedly comparing it with the middle element of the current range and discarding the half that cannot contain it. Each comparison halves the search space, so it needs at most ⌊log₂ n⌋ + 1 comparisons: O(log n) time and O(1) space iteratively. It requires random access and sorted data. Correct implementations maintain an explicit loop invariant over a half-open interval, compute the midpoint as `lo + (hi - lo) / 2` to avoid overflow, and are typically expressed as lower-bound and upper-bound searches, from which membership, first and last occurrence and counts can all be derived.

## 7. Cheat sheet

| Need | Code |
|---|---|
| midpoint | `lo + (hi - lo) / 2` |
| first `>= key` | `lower_bound` (`a[mid] < key → lo = mid + 1`) |
| first `> key` | `upper_bound` (`a[mid] <= key → lo = mid + 1`) |
| count of key | `upper - lower` |
| library | `bsearch(&key, a, n, sizeof *a, cmp)` (any match) |
| minimise x with monotone `ok(x)` | `while (lo < hi) { mid; ok(mid) ? (hi = mid) : (lo = mid + 1); }` |
| real-valued | bisection, 60–100 iterations |

> [!INTERVIEW]
> **"Find the first bad build among n builds, given `is_bad(k)`."** This is lower_bound on a monotone predicate (`git bisect` does exactly this): `lo = 1, hi = n`, with `is_bad(mid) ? hi = mid : lo = mid + 1`. That's ⌈log₂ n⌉ calls. Mention that the predicate must be monotone. If a flaky build can flip results, bisection gives a wrong answer, so you rerun suspicious steps.
