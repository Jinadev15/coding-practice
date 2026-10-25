# Binary Search

The STL has binary search built in (`std::lower_bound`, `std::upper_bound`, `std::equal_range`, `std::binary_search`, and C++20's `std::ranges::partition_point`), and these work on any sorted random-access range with custom comparators and projections. For **search on the answer**, you write the loop yourself around a monotone predicate. The theory (invariants, monotonicity, real-valued bisection) is covered in the Python Binary Search lesson. Here we focus on correct and idiomatic C++.

## 1. The standard functions

```cpp
vector<int> a = {1, 3, 3, 3, 7, 9};
auto lo = lower_bound(a.begin(), a.end(), 3);     // first >= 3  → index 1
auto hi = upper_bound(a.begin(), a.end(), 3);     // first > 3   → index 4
auto [l, r] = equal_range(a.begin(), a.end(), 3); // both at once
bool has = binary_search(a.begin(), a.end(), 7);  // true
int idx = lo - a.begin();                          // iterator → index
long cnt = hi - lo;                                // 3 occurrences
```

| Question | Code |
|---|---|
| present? | `binary_search(b, e, x)` |
| first ≥ x | `lower_bound` |
| first > x | `upper_bound` |
| last ≤ x | `prev(upper_bound(...))` (check that it isn't `begin`) |
| count in [L, R] | `upper_bound(R) - lower_bound(L)` |

### Custom orders and projections

```cpp
struct Robot { string name; int battery; };
vector<Robot> rs = /* sorted by battery */;
auto it = lower_bound(rs.begin(), rs.end(), 50,
                      [](const Robot& r, int value) { return r.battery < value; });  // (element, value)

// C++20 ranges: a projection instead of a comparator lambda
auto it2 = ranges::lower_bound(rs, 50, {}, &Robot::battery);

// descending order: pass greater<>()
vector<int> d = {9, 7, 3, 1};
auto j = lower_bound(d.begin(), d.end(), 5, greater<>());   // first element <= 5 → 3
```

> [!KEY]
> The comparator must use the **same ordering** the range is sorted by. For `lower_bound` it's called as `comp(element, value)`; for `upper_bound`, as `comp(value, element)`. Mixing them up compiles but searches wrongly.

## 2. `partition_point`: binary search on any predicate

```cpp
// first index where pred becomes false, for a range partitioned as [true...true false...false]
auto it = partition_point(a.begin(), a.end(), [](int x) { return x < 5; });
```

That's lower_bound generalised to any monotone predicate over a range.

## 3. Search on the answer

```cpp
// smallest capacity to ship all packages (in order) within D days
long long min_capacity(const vector<int>& w, int D) {
    auto ok = [&](long long cap) {
        int days = 1; long long load = 0;
        for (int x : w) {
            if (load + x > cap) { ++days; load = 0; }
            load += x;
        }
        return days <= D;
    };
    long long lo = *max_element(w.begin(), w.end());
    long long hi = accumulate(w.begin(), w.end(), 0LL);
    while (lo < hi) {                         // invariant: the answer is in [lo, hi]
        long long mid = lo + (hi - lo) / 2;
        if (ok(mid)) hi = mid; else lo = mid + 1;
    }
    return lo;
}
```

> [!WARNING]
> - **Overflow**: `(lo + hi) / 2` overflows when both are near `LLONG_MAX`. Use `lo + (hi - lo) / 2`.
> - **Infinite loops**: when the "maximise" branch sets `lo = mid`, round the midpoint **up**: `mid = lo + (hi - lo + 1) / 2`.
> - **Floating point**: iterate a fixed number of times (100 iterations) rather than `while (hi - lo > eps)`, which may never terminate when eps is below the precision of the values.

## 4. Searching in rotated arrays, matrices and functions

```cpp
int find_min_rotated(const vector<int>& a) {     // distinct values
    int lo = 0, hi = (int)a.size() - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] > a[hi]) lo = mid + 1; else hi = mid;
    }
    return a[lo];
}

// k-th smallest in a row- and column-sorted matrix: binary search on the VALUE, counting elements <= mid
long long count_le(const vector<vector<int>>& m, long long x) {
    int n = m.size(), r = n - 1, c = 0; long long cnt = 0;
    while (r >= 0 && c < n) {
        if (m[r][c] <= x) { cnt += r + 1; ++c; } else --r;   // staircase walk: O(n)
    }
    return cnt;
}
```

## 5. Ordered containers

For dynamic sorted data, use `std::set` / `std::multiset` / `std::map` with **member** `lower_bound` (O(log n)):

```cpp
set<int> s = {10, 20, 30};
auto it = s.lower_bound(15);                 // 20
if (it != s.begin()) { auto pred = prev(it); /* 10: the largest < 15 */ }
multiset<int> ms; ms.insert(5); ms.insert(5);
ms.erase(ms.find(5));                        // erase ONE copy (ms.erase(5) erases ALL)
```

For "k-th element / rank" on a dynamic set, GCC's policy-based `tree` (`__gnu_pbds::tree` with `tree_order_statistics_node_update`) provides `find_by_order` and `order_of_key` in O(log n).

## 6. Exam-ready answers

> [!EXAM]
> **std::lower_bound and std::upper_bound.** For a range sorted with respect to a comparator, `std::lower_bound` returns an iterator to the first element not less than the given value, and `std::upper_bound` an iterator to the first element greater than it; together (or via `std::equal_range`), they delimit all elements equivalent to the value. They perform O(log n) comparisons and run in O(log n) time on random-access iterators, but advancing non-random-access iterators (such as those of `std::set`) takes linear time, so associative containers provide member functions with logarithmic complexity instead.

## 7. Cheat sheet

| Need | C++ |
|---|---|
| bounds on a sorted vector | `lower_bound`, `upper_bound`, `equal_range` |
| by a struct field | `ranges::lower_bound(v, x, {}, &T::field)` |
| any predicate | `partition_point` |
| bounds in a set/map | `s.lower_bound(x)` (member) |
| erase one from a multiset | `ms.erase(ms.find(x))` |
| midpoint | `lo + (hi - lo) / 2` |
| order statistics | `__gnu_pbds::tree` |

> [!INTERVIEW]
> **"`std::lower_bound(s.begin(), s.end(), x)` on a `std::set` with 10⁶ elements is slow. Why?"** `std::lower_bound` performs O(log n) comparisons, but moving a bidirectional iterator to the midpoint costs O(distance), so the total is O(n). `s.lower_bound(x)` descends the tree directly in O(log n). The same applies to `std::distance` on set iterators, which is O(n).
