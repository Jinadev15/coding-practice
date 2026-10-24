# STL Algorithms

`<algorithm>` and `<numeric>` contain over 100 tested, optimised algorithms that work on any iterator range. Professional C++ code favours them over hand-written loops ("no raw loops", as Sean Parent put it): `std::sort` is an introsort that's hard to beat, `std::find_if` states its intent in its name, and the remove-erase idiom does in O(n) what naive loops do in O(n²). This lesson organises the algorithms you'll use daily, with their complexity and their traps.

## 1. Searching and counting

```cpp
#include <algorithm>
#include <numeric>
std::vector<int> v{5, 3, 8, 3, 9};

auto it = std::find(v.begin(), v.end(), 8);                    // iterator, or end()
auto jt = std::find_if(v.begin(), v.end(), [](int x) { return x > 6; });
std::count(v.begin(), v.end(), 3);                             // 2
std::count_if(v.begin(), v.end(), [](int x) { return x % 2; });
std::any_of(v.begin(), v.end(), pred); std::all_of(...); std::none_of(...);
auto [mn, mx] = std::minmax_element(v.begin(), v.end());       // iterators
std::max(a, b); std::min({a, b, c}); std::clamp(x, lo, hi);
```

## 2. Sorting and order

| Algorithm | What it does | Complexity |
|---|---|---|
| `sort` | sorts (introsort; **not stable**) | O(n log n) |
| `stable_sort` | keeps the relative order of equal elements | O(n log n) (may use O(n) extra memory) |
| `partial_sort(b, m, e)` | smallest `m - b` elements, sorted, at the front | O(n log k) |
| `nth_element(b, n, e)` | puts the element that **would** be at `n` there, smaller ones before it, larger after (unsorted) | **O(n)** average |
| `is_sorted`, `binary_search`, `lower_bound`, `upper_bound`, `equal_range` | on sorted ranges | O(n) / O(log n) |
| `merge`, `inplace_merge`, `set_union`, `set_intersection`, `set_difference` | on sorted ranges | O(n) |

```cpp
std::sort(v.begin(), v.end());                                     // ascending
std::sort(v.begin(), v.end(), std::greater<>());                   // descending
std::sort(people.begin(), people.end(), [](const P& a, const P& b) {
    return std::tie(a.last, a.first) < std::tie(b.last, b.first); // multi-key ordering
});
std::nth_element(v.begin(), v.begin() + v.size() / 2, v.end());   // the median in O(n)
```

> [!DANGER]
> A comparator must be a **strict weak ordering**: use `<`, never `<=`. `std::sort` with `<=` is undefined behaviour and can read out of bounds and crash on large inputs with many equal elements.

## 3. Modifying sequences

```cpp
std::transform(v.begin(), v.end(), v.begin(), [](int x) { return x * 2; });     // in place
std::transform(a.begin(), a.end(), b.begin(), out.begin(), std::plus<>());      // element-wise a + b
std::fill(v.begin(), v.end(), 0);
std::iota(v.begin(), v.end(), 1);                     // 1, 2, 3, ... (<numeric>)
std::reverse(v.begin(), v.end());
std::rotate(v.begin(), v.begin() + k, v.end());       // left-rotate by k
std::shuffle(v.begin(), v.end(), std::mt19937{42});
std::copy_if(v.begin(), v.end(), std::back_inserter(out), pred);
```

### The remove-erase idiom

`std::remove` **doesn't remove anything**. It can't, because it only has iterators. It shifts the kept elements forward and returns the new logical end. The container still has its old size, with unspecified values in the tail:

```cpp
std::vector<int> w{1, 2, 3, 2, 4, 2};
auto new_end = std::remove(w.begin(), w.end(), 2);   // w: 1 3 4 ? ? ?
w.erase(new_end, w.end());                           // w: 1 3 4
std::erase(w, 3);                                    // C++20: the same in one call → 1 4
std::erase_if(w, [](int x) { return x > 3; });
```

Similarly, `std::unique` collapses **adjacent** duplicates, so sort first to deduplicate everything:

```cpp
std::sort(u.begin(), u.end());
u.erase(std::unique(u.begin(), u.end()), u.end());   // sorted, distinct values
```

### Partitioning

```cpp
auto mid = std::partition(v.begin(), v.end(), [](int x) { return x % 2 == 0; });   // evens first, O(n)
std::stable_partition(...);                                                       // keeps order
```

## 4. Numeric algorithms (`<numeric>`)

```cpp
long long sum = std::accumulate(v.begin(), v.end(), 0LL);      // the init value's TYPE sets the accumulator type!
double dot = std::inner_product(a.begin(), a.end(), b.begin(), 0.0);
std::partial_sum(v.begin(), v.end(), prefix.begin());           // prefix sums
std::adjacent_difference(...);
auto total = std::reduce(std::execution::par, v.begin(), v.end());   // parallelisable (C++17)
std::gcd(a, b); std::lcm(a, b);
```

> [!WARNING]
> `std::accumulate(v.begin(), v.end(), 0)` accumulates in `int` even if `v` holds `long long` or `double`, so it **silently truncates or overflows**. Pass `0LL` or `0.0`.

## 5. Complexity awareness

| Want | Avoid | Use |
|---|---|---|
| top-k | sorting everything, O(n log n) | `partial_sort` / `nth_element` |
| median | sort | `nth_element`, O(n) |
| delete many elements | repeated `erase`, O(n²) | `erase_if`, O(n) |
| membership in a sorted vector | `find`, O(n) | `binary_search` / `lower_bound`, O(log n) |
| dedup | a nested loop | sort + unique |

## 6. Exam-ready answers

> [!EXAM]
> **STL algorithms.** The standard algorithms are function templates that operate on ranges specified by iterator pairs, independent of the containers that hold the elements, and are often customised with predicates or comparators such as lambdas. They include non-modifying algorithms (`find`, `count`, `all_of`), modifying algorithms (`copy`, `transform`, `fill`, `reverse`), sorting and related operations (`sort`, `stable_sort`, `partial_sort`, `nth_element`, `binary_search`, `lower_bound`), and numeric algorithms (`accumulate`, `inner_product`, `partial_sum`). Algorithms cannot change the size of a container: `remove` and `unique` reorder elements and return a new logical end, which must be passed to the container's `erase` member (the erase-remove idiom). Comparators must define a strict weak ordering.

## 7. Cheat sheet

| Need | Code |
|---|---|
| sort by several keys | `std::tie(a.x, a.y) < std::tie(b.x, b.y)` |
| stable sort | `std::stable_sort` |
| k-th smallest | `std::nth_element(b, b + k, e)` |
| remove values | `std::erase(v, x)` / `std::erase_if(v, pred)` |
| dedup | `sort` then `v.erase(std::unique(...), v.end())` |
| sum safely | `std::accumulate(b, e, 0LL)` |
| fill 1..n | `std::iota(b, e, 1)` |
| filter into a new vector | `std::copy_if(b, e, std::back_inserter(out), pred)` |

> [!INTERVIEW]
> **"Find the median of an unsorted array in better than O(n log n)."** Use `std::nth_element(v.begin(), v.begin() + n/2, v.end())`, then `v[n/2]`. It implements introselect: quickselect with a fallback, average O(n). For an even n, the lower median is the max of the left part, `*std::max_element(v.begin(), v.begin() + n/2)`. Mention that sorting is O(n log n), and that for streaming data you'd use the two-heap technique instead.
