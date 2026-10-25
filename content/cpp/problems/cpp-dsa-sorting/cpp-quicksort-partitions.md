---
id: cpp-quicksort-partitions
title: Quicksort That Survives Adversarial Input
difficulty: Medium
order: 3
tags: sorting, quicksort, Lomuto partition, randomization, three-way partition
time_limit: 2
---
## Statement
**Part 1: trace Lomuto quicksort.**

```cpp
int lomuto(std::vector<int>& a, int lo, int hi);    // pivot = a[hi]; returns the pivot's final index
void quicksort_trace(std::vector<int>& a, int lo, int hi, std::vector<std::string>& trace);
```

`quicksort_trace` sorts `a[lo..hi]`: partition, append `"pivot P -> i: <whole array>"`, then recurse on the left part and then the right part. Use exactly the Lomuto scheme from the lesson (scan `j` from `lo` to `hi−1`, swap `a[j]` into the `< pivot` region, and finally swap the pivot into place).

**Part 2: a quicksort that doesn't degrade.**

```cpp
void fast_sort(std::vector<int>& a);     // no std::sort / stable_sort / sort_heap allowed
```

The test data includes 10⁶ elements that are **already sorted**, **reverse sorted**, and **all equal**. A last-element pivot is O(n²) on those inputs and recurses 10⁶ levels deep, which crashes. Use a **random pivot** and a **three-way partition** (`< p`, `== p`, `> p`). Recursing into the smaller side first (and looping on the larger side) also bounds the stack depth to O(log n).

**Input:** cases until the end of input:

- `trace n` followed by `n` values (n ≤ 10)
- `sort kind n seed`, where kind is `random`, `sorted`, `reversed`, `equal` or `few` (only 3 distinct values). The driver generates the data.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int lomuto(vector<int>& a, int lo, int hi) { return hi; }
void quicksort_trace(vector<int>& a, int lo, int hi, vector<string>& trace) {}

static void naive_qs(vector<int>& a, int lo, int hi) {      // last-element pivot: O(n^2) on sorted data
    if (lo >= hi) return;
    int p = a[hi], i = lo;
    for (int j = lo; j < hi; ++j) if (a[j] < p) swap(a[i++], a[j]);
    swap(a[i], a[hi]);
    naive_qs(a, lo, i - 1); naive_qs(a, i + 1, hi);
}
void fast_sort(vector<int>& a) { if (!a.empty()) naive_qs(a, 0, (int)a.size() - 1); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "trace") {
            int n; cin >> n;
            vector<int> a(n);
            for (auto& x : a) cin >> x;
            vector<string> tr;
            if (n) quicksort_trace(a, 0, n - 1, tr);
            for (auto& t : tr) cout << t << '\n';
            cout << "done\n";
        } else {
            string kind; int n; unsigned seed; cin >> kind >> n >> seed;
            mt19937 rng(seed);
            vector<int> a(n);
            for (int i = 0; i < n; ++i) {
                if (kind == "random") a[i] = (int)(rng() % 2000000001u) - 1000000000;
                else if (kind == "sorted") a[i] = i * 3;
                else if (kind == "reversed") a[i] = (n - i) * 3;
                else if (kind == "equal") a[i] = 42;
                else a[i] = (int)(rng() % 3);
            }
            fast_sort(a);
            long long h = 0;
            for (int i = 0; i < n; ++i) h = (h * 31 + a[i] + 1000000000LL) % 1000000007;
            cout << kind << ' ' << (is_sorted(a.begin(), a.end()) ? "sorted" : "NOT sorted") << ' ' << h << '\n';
        }
    }
}
```

## Tests
=== sample
trace 5
3 7 1 6 4
trace 4
1 2 3 4
---
pivot 4 -> 2: 3 1 4 6 7
pivot 1 -> 0: 1 3 4 6 7
pivot 7 -> 4: 1 3 4 6 7
done
pivot 4 -> 3: 1 2 3 4
pivot 3 -> 2: 1 2 3 4
pivot 2 -> 1: 1 2 3 4
done
=== hidden
trace 1
9
trace 3
2 2 2
---
done
pivot 2 -> 0: 2 2 2
pivot 2 -> 1: 2 2 2
done
=== hidden
sort random 1000000 7
sort sorted 1000000 1
sort reversed 1000000 1
---
random sorted 610001387
sorted sorted 106183006
reversed sorted 712146921
=== hidden
sort equal 1000000 1
sort few 1000000 5
---
equal sorted 402912295
few sorted 719175638
=== hidden
trace 6
6 8 5 3 7 4
trace 7
1 8 8 1 1 7 8
trace 4
5 5 1 3
trace 6
1 8 3 3 9 3
sort sorted 13 576
---
pivot 4 -> 1: 3 4 5 6 7 8
pivot 8 -> 5: 3 4 5 6 7 8
pivot 7 -> 4: 3 4 5 6 7 8
pivot 6 -> 3: 3 4 5 6 7 8
done
pivot 8 -> 4: 1 1 1 7 8 8 8
pivot 7 -> 3: 1 1 1 7 8 8 8
pivot 1 -> 0: 1 1 1 7 8 8 8
pivot 1 -> 1: 1 1 1 7 8 8 8
pivot 8 -> 5: 1 1 1 7 8 8 8
done
pivot 3 -> 1: 1 3 5 5
pivot 5 -> 2: 1 3 5 5
done
pivot 3 -> 1: 1 3 3 3 9 8
pivot 8 -> 4: 1 3 3 3 8 9
pivot 3 -> 2: 1 3 3 3 8 9
done
sorted sorted 899889473
=== hidden
trace 8
8 7 8 2 8 4 3 5
trace 4
4 7 4 1
trace 7
8 3 4 2 8 3 2
trace 3
7 4 5
sort random 32 502
---
pivot 5 -> 3: 2 4 3 5 8 7 8 8
pivot 3 -> 1: 2 3 4 5 8 7 8 8
pivot 8 -> 5: 2 3 4 5 7 8 8 8
pivot 8 -> 6: 2 3 4 5 7 8 8 8
done
pivot 1 -> 0: 1 7 4 4
pivot 4 -> 1: 1 4 4 7
pivot 7 -> 3: 1 4 4 7
done
pivot 2 -> 0: 2 3 4 2 8 3 8
pivot 8 -> 5: 2 3 4 2 3 8 8
pivot 3 -> 2: 2 2 3 3 4 8 8
pivot 4 -> 4: 2 2 3 3 4 8 8
done
pivot 5 -> 1: 4 5 7
done
random sorted 119730511
=== hidden
trace 5
5 7 9 2 2
trace 7
5 5 6 4 8 4 8
trace 6
8 2 6 3 4 2
trace 4
2 7 8 2
sort equal 41 392
---
pivot 2 -> 0: 2 7 9 2 5
pivot 5 -> 2: 2 2 5 7 9
pivot 9 -> 4: 2 2 5 7 9
done
pivot 8 -> 5: 5 5 6 4 4 8 8
pivot 4 -> 0: 4 5 6 4 5 8 8
pivot 5 -> 2: 4 4 5 5 6 8 8
pivot 6 -> 4: 4 4 5 5 6 8 8
done
pivot 2 -> 0: 2 2 6 3 4 8
pivot 8 -> 5: 2 2 6 3 4 8
pivot 4 -> 3: 2 2 3 4 6 8
pivot 3 -> 2: 2 2 3 4 6 8
done
pivot 2 -> 0: 2 7 8 2
pivot 2 -> 1: 2 2 8 7
pivot 7 -> 2: 2 2 7 8
done
equal sorted 980616220
=== hidden
sort reversed 1000000 868952
---
reversed sorted 712146921
=== hidden
sort sorted 1000000 721051
---
sorted sorted 106183006
=== hidden
sort equal 1000000 914274
---
equal sorted 402912295

## Hints
- For the trace, record the pivot value **before** partitioning, then the array after `lomuto` returns.
- Sorted and all-equal inputs are the worst cases for a last-element pivot. Pick a random pivot, and keep the elements equal to the pivot in a middle block that you never recurse into.
- To keep the recursion shallow, recurse only into the smaller part and handle the larger part with a `while` loop.

## Solution
**Lomuto.** Keep `a[lo..i−1]` as the "less than the pivot" region. Each `a[j] < pivot` is swapped to position `i`, which then grows. A final swap puts the pivot right after that region, which is its sorted position.

**Why the naive version dies.** On sorted input, the last element is the maximum, so every partition is maximally lopsided. That's n levels of recursion and Θ(n²) work. On all-equal input, Lomuto puts every element on one side, with the same effect.

**The fixes:**

1. **A random pivot** makes lopsided splits unlikely on *every* input, giving O(n log n) expected time.
2. **Three-way partitioning** (Dijkstra's Dutch national flag) groups the elements equal to the pivot in the middle and never recurses into them. All-equal arrays finish in one pass.
3. **Recurse on the smaller side, loop on the larger.** The smaller side is at most half, so the recursion depth is O(log n) even when you're unlucky.

This is close to what production introsort does, except that introsort also switches to heap sort when the depth exceeds 2·log n.

Complexity: O(n log n) expected time, O(log n) stack.

```cpp
#include <bits/stdc++.h>
using namespace std;

int lomuto(vector<int>& a, int lo, int hi) {
    int pivot = a[hi], i = lo;                    // a[lo..i-1] < pivot
    for (int j = lo; j < hi; ++j)
        if (a[j] < pivot) swap(a[i++], a[j]);
    swap(a[i], a[hi]);
    return i;
}

void quicksort_trace(vector<int>& a, int lo, int hi, vector<string>& trace) {
    if (lo >= hi) return;
    int pv = a[hi];
    int p = lomuto(a, lo, hi);
    string s = "pivot " + to_string(pv) + " -> " + to_string(p) + ":";
    for (int x : a) s += " " + to_string(x);
    trace.push_back(s);
    quicksort_trace(a, lo, p - 1, trace);
    quicksort_trace(a, p + 1, hi, trace);
}

static mt19937 rng(12345);

static void qs3(vector<int>& a, int lo, int hi) {
    while (lo < hi) {                              // loop on the larger side, recurse on the smaller
        int pivot = a[lo + (int)(rng() % (unsigned)(hi - lo + 1))];
        int lt = lo, i = lo, gt = hi;              // [lo,lt) < p, [lt,i) == p, (gt,hi] > p
        while (i <= gt) {
            if (a[i] < pivot) swap(a[lt++], a[i++]);
            else if (a[i] > pivot) swap(a[i], a[gt--]);
            else ++i;
        }
        if (lt - lo < hi - gt) { qs3(a, lo, lt - 1); lo = gt + 1; }
        else { qs3(a, gt + 1, hi); hi = lt - 1; }
    }
}

void fast_sort(vector<int>& a) { if (!a.empty()) qs3(a, 0, (int)a.size() - 1); }
```
