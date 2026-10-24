# Sorting Algorithms

Sorting is the most studied problem in computer science for good reason: sorted data makes searching logarithmic, makes duplicates adjacent, enables merging and sweeping, and underlies databases, schedulers, collision detection (sweep-and-prune), point-cloud processing and median filters. In C you'll use the library `qsort` most of the time. But you must know how the classic algorithms work, what **stable** means, and why `O(n log n)` is a hard lower bound for comparison sorts. That's both interview core and the basis of writing fast code for embedded targets where `qsort` may be too slow or unavailable.

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **in-place** | uses O(1) (or O(log n) stack) extra memory |
| **stable** | equal keys keep their original relative order |
| **adaptive** | faster on nearly sorted input |
| **comparison sort** | only inspects data via `a < b` comparisons |

> [!KEY]
> Any comparison sort needs **Ω(n log n)** comparisons in the worst case. A decision tree that distinguishes all `n!` orderings has height ≥ log₂(n!) ≈ n log₂ n − 1.44n. Counting and radix sort beat this only because they don't compare: they index by the key's value.

## 2. The quadratic sorts (and why insertion sort still matters)

```c
void insertion_sort(int *a, size_t n) {
    for (size_t i = 1; i < n; i++) {
        int key = a[i];
        size_t j = i;
        while (j > 0 && a[j - 1] > key) {   /* shift bigger elements right */
            a[j] = a[j - 1];
            j--;
        }
        a[j] = key;
    }
}
```

| Algorithm | Best | Average | Worst | Stable | Notes |
|---|---|---|---|---|---|
| bubble | O(n) with early exit | O(n²) | O(n²) | yes | teaching only |
| selection | O(n²) | O(n²) | O(n²) | **no** | minimum number of **swaps** (n − 1), useful when writes are expensive (flash) |
| insertion | **O(n)** | O(n²) | O(n²) | yes | fastest for n ≲ 16 and for nearly sorted data |

Insertion sort's running time is O(n + inversions). Real sorts (introsort, Timsort, pdqsort) switch to insertion sort for small sub-arrays because its inner loop is tiny and cache-friendly.

> [!WARNING]
> The `size_t j` loop above uses `j > 0 && a[j - 1] > key`. Writing it with `int j = i - 1; while (j >= 0 ...)` is also fine, but **never** write `size_t j = i - 1; while (j >= 0 ...)`: an unsigned value is always ≥ 0, so the loop never ends and `j` wraps to `SIZE_MAX`.

## 3. Merge sort: guaranteed O(n log n), stable

```c
static void merge(int *a, int *tmp, size_t lo, size_t mid, size_t hi) {  /* [lo,mid) + [mid,hi) */
    size_t i = lo, j = mid, k = lo;
    while (i < mid && j < hi)
        tmp[k++] = (a[j] < a[i]) ? a[j++] : a[i++];   /* '<' not '<=' on the right: ties take the LEFT → stable */
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi)  tmp[k++] = a[j++];
    memcpy(a + lo, tmp + lo, (hi - lo) * sizeof *a);
}

static void msort(int *a, int *tmp, size_t lo, size_t hi) {
    if (hi - lo < 2) return;
    size_t mid = lo + (hi - lo) / 2;
    msort(a, tmp, lo, mid);
    msort(a, tmp, mid, hi);
    if (a[mid - 1] <= a[mid]) return;      /* already in order: makes sorted input O(n) */
    merge(a, tmp, lo, mid, hi);
}

int merge_sort(int *a, size_t n) {
    int *tmp = malloc(n * sizeof *tmp);
    if (!tmp && n) return -1;
    msort(a, tmp, 0, n);
    free(tmp);
    return 0;
}
```

The recurrence T(n) = 2T(n/2) + Θ(n) gives Θ(n log n) in **every** case. The cost is O(n) extra memory. Merge sort is the natural choice for **linked lists** (no random access needed, O(1) extra space by relinking) and for **external sorting** of files larger than RAM (sort chunks, then k-way merge them).

## 4. Quicksort: fastest in practice, with traps

```c
static void swap(int *x, int *y) { int t = *x; *x = *y; *y = t; }

/* Hoare-style partition around a median-of-three pivot. */
static void quick(int *a, ptrdiff_t lo, ptrdiff_t hi) {        /* inclusive bounds */
    while (hi - lo > 16) {
        ptrdiff_t mid = lo + (hi - lo) / 2;
        if (a[mid] < a[lo]) swap(&a[mid], &a[lo]);
        if (a[hi] < a[lo])  swap(&a[hi], &a[lo]);
        if (a[hi] < a[mid]) swap(&a[hi], &a[mid]);
        int pivot = a[mid];
        ptrdiff_t i = lo, j = hi;
        while (i <= j) {
            while (a[i] < pivot) i++;
            while (a[j] > pivot) j--;
            if (i <= j) { swap(&a[i], &a[j]); i++; j--; }
        }
        /* recurse into the SMALLER side, loop on the larger: stack depth O(log n) */
        if (j - lo < hi - i) { quick(a, lo, j); lo = i; }
        else                 { quick(a, i, hi); hi = j; }
    }
    /* finish small ranges with insertion sort */
    for (ptrdiff_t k = lo + 1; k <= hi; k++) {
        int key = a[k]; ptrdiff_t m = k;
        while (m > lo && a[m - 1] > key) { a[m] = a[m - 1]; m--; }
        a[m] = key;
    }
}
```

| Concern | Fix used above |
|---|---|
| Sorted input with "first element as pivot" → O(n²) | median-of-three pivot |
| Many equal keys → O(n²) with Lomuto partition | Hoare partition (`<` / `>` stop on equal keys and swap them, so equal keys split evenly) |
| Worst-case recursion depth O(n) → stack overflow | recurse on the smaller side, iterate on the larger |
| Overhead on tiny ranges | insertion-sort cutoff |
| Adversarial input still O(n²) | **introsort**: switch to heapsort after 2·log₂n levels (what C++ `std::sort` does) |

Quicksort isn't stable. Its average is ~1.39 n log₂ n comparisons, but its inner loop is so cheap and cache-friendly that it usually beats merge sort and heapsort.

## 5. Heapsort: O(n log n) worst case, in place

Build a max-heap in O(n) (sift down from the last parent to the root), then repeatedly swap the root to the end and sift down. It's in place with a guaranteed bound, but not stable, and its scattered memory accesses make it 2–3× slower than quicksort in practice. It's the safety net inside introsort. (See the Heaps lesson for the code.)

## 6. Linear-time sorts: counting and radix

When keys are small integers, you don't need comparisons:

```c
/* Stable counting sort of values in [0, K). out must not alias a. */
void counting_sort(const int *a, int *out, size_t n, int K) {
    size_t *cnt = calloc((size_t)K + 1, sizeof *cnt);
    for (size_t i = 0; i < n; i++) cnt[a[i] + 1]++;
    for (int k = 0; k < K; k++) cnt[k + 1] += cnt[k];   /* prefix sums: cnt[v] = first slot for v */
    for (size_t i = 0; i < n; i++) out[cnt[a[i]]++] = a[i];
    free(cnt);
}
```

Counting sort runs in O(n + K) and is stable. **LSD radix sort** applies a stable counting sort digit by digit (e.g. 8 bits at a time, 4 passes for `uint32_t`), giving O(d·(n + 256)). For millions of 32-bit keys, it often beats every comparison sort. Stability is essential here: each pass must preserve the order established by the previous passes.

## 7. `qsort`: the library sort and its comparator

```c
#include <stdlib.h>
void qsort(void *base, size_t nmemb, size_t size, int (*compar)(const void *, const void *));
```

```c
static int cmp_int(const void *pa, const void *pb) {
    int a = *(const int *)pa, b = *(const int *)pb;
    return (a > b) - (a < b);          /* -1, 0, 1 — NEVER 'return a - b;' */
}

typedef struct { char name[16]; int score; } Player;

static int cmp_player(const void *pa, const void *pb) {   /* score descending, then name ascending */
    const Player *a = pa, *b = pb;
    if (a->score != b->score) return (a->score < b->score) - (a->score > b->score);
    return strcmp(a->name, b->name);
}

qsort(scores, n, sizeof scores[0], cmp_int);
qsort(players, m, sizeof *players, cmp_player);
```

> [!DANGER]
> `return a - b;` overflows when `a` and `b` have opposite signs and large magnitudes (e.g. `INT_MIN - 1`). Signed overflow is **undefined behaviour**, and in practice it returns the wrong sign and corrupts the sort. Use `(a > b) - (a < b)`.

> [!KEY]
> - `qsort` is **not guaranteed stable**. For stability, add the original index as a final tie-breaker.
> - The comparator must define a **strict weak ordering**: consistent, transitive, and `cmp(x, x) == 0`. A comparator that returns random or inconsistent answers (e.g. comparing floats with NaNs) is undefined behaviour and can crash glibc's `qsort`.
> - Comparing doubles: `(a > b) - (a < b)` treats NaN as equal to everything, which breaks transitivity. Filter NaNs first.

## 8. Choosing a sort

| Situation | Choice |
|---|---|
| General data in C | `qsort` (glibc uses a merge sort when memory allows, else introsort) |
| ≤ ~16 elements, or nearly sorted | insertion sort |
| Need stability | merge sort, or `qsort` with an index tie-breaker |
| Linked list | merge sort by relinking |
| Hard real-time / no malloc | heapsort (O(1) extra, O(n log n) worst case) |
| Small integer keys | counting sort |
| Millions of fixed-width integers | LSD radix sort |
| Data bigger than RAM | external merge sort |
| Only the k-th element, or top k | quickselect (O(n) average) or a heap of size k: don't sort everything |

## 9. Exam-ready answers

> [!EXAM]
> **Stable sorting.** A sorting algorithm is stable if records with equal keys appear in the output in the same relative order as in the input. Stability matters when sorting by several keys in successive passes (sort by the secondary key, then stably by the primary key) and is required for LSD radix sort. Insertion sort, merge sort and counting sort are stable; selection sort, quicksort and heapsort, in their usual in-place forms, are not.

> [!EXAM]
> **Quicksort vs merge sort.** Quicksort partitions the array around a pivot and recursively sorts the two parts; it sorts in place with O(log n) stack space and averages O(n log n), but degrades to O(n²) with bad pivots and isn't stable. Merge sort recursively sorts two halves and merges them; it is stable and O(n log n) in every case but needs O(n) auxiliary memory for arrays. Quicksort is usually faster in practice because of its low constant factor and good cache locality, which is why library sorts combine it with insertion sort and heapsort (introsort).

## 10. Cheat sheet

| | Best | Avg | Worst | Space | Stable |
|---|---|---|---|---|---|
| insertion | n | n² | n² | 1 | ✓ |
| selection | n² | n² | n² | 1 | ✗ |
| merge | n log n | n log n | n log n | n | ✓ |
| quick | n log n | n log n | n² | log n | ✗ |
| heap | n log n | n log n | n log n | 1 | ✗ |
| counting | n + K | n + K | n + K | n + K | ✓ |
| radix (d digits) | d(n + b) | d(n + b) | d(n + b) | n + b | ✓ |

> [!INTERVIEW]
> **"Sort 1 GB of 32-bit integers with 64 MB of RAM."** Do an external merge sort. Read 64 MB chunks, sort each in memory (radix or `qsort`) and write 16 sorted runs. Then merge them in a single pass with a min-heap of size 16, reading each run through a buffer of a few MB. Each byte is read and written twice. If the values are bounded, a counting approach with a bitmap or per-range count passes can be even faster.
