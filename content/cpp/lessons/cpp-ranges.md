# Ranges (C++20)

The Ranges library modernises the STL in two ways. **Range algorithms** take a whole container instead of an iterator pair (`std::ranges::sort(v)`), with projections and better error messages. **Views** are lazy, composable adaptors that you chain with `|` into pipelines (`v | views::filter(p) | views::transform(f)`), which compute elements on demand without building intermediate containers. It's C++'s answer to Python generators and functional pipelines.

## 1. Range algorithms

```cpp
#include <algorithm>
#include <ranges>
namespace rv = std::views;

std::vector<int> v{3, 1, 2};
std::ranges::sort(v);                                  // no begin/end noise
auto it = std::ranges::find(v, 2);
std::ranges::reverse(v);
bool ok = std::ranges::all_of(v, [](int x) { return x > 0; });
```

### Projections

Most range algorithms accept a **projection**, a function applied to each element before comparing:

```cpp
struct Robot { std::string name; double battery; };
std::vector<Robot> fleet = ...;
std::ranges::sort(fleet, {}, &Robot::battery);                     // sort by battery
std::ranges::sort(fleet, std::greater{}, &Robot::name);            // by name, descending
auto low = std::ranges::find_if(fleet, [](double b) { return b < 0.2; }, &Robot::battery);
auto top = std::ranges::max(fleet, {}, &Robot::battery);           // the Robot with the max battery
```

That's no comparator lambda just to say "compare by this field".

## 2. Views: lazy pipelines

```cpp
for (int x : rv::iota(1, 20)
           | rv::filter([](int x) { return x % 3 == 0; })
           | rv::transform([](int x) { return x * x; })
           | rv::take(3))
    std::cout << x << ' ';            // 9 36 81
```

Nothing is computed until the loop pulls an element, and only as many elements as needed are produced. `take(3)` stops the whole pipeline after three outputs, even though `iota` could continue. Views don't own data: they reference the underlying range and are cheap to copy (O(1)).

| View | Produces |
|---|---|
| `views::iota(a, b)` / `iota(a)` | a, a+1, … (b exclusive) / an infinite sequence |
| `views::filter(pred)` | the elements satisfying pred |
| `views::transform(f)` | f(x) for each x |
| `views::take(n)` / `drop(n)` | the first n / all but the first n |
| `views::take_while(p)` / `drop_while(p)` | a prefix by predicate |
| `views::reverse` | backwards |
| `views::keys` / `views::values` | `.first` / `.second` of pair-like elements (maps!) |
| `views::split(d)` | subranges separated by a delimiter |
| `views::join` | flattens a range of ranges |
| `views::enumerate` (C++23) | `(index, element)` pairs |
| `views::zip(a, b)` (C++23) | tuples of corresponding elements |
| `views::chunk(n)`, `slide(n)` (C++23) | fixed-size groups / sliding windows |

```cpp
std::map<std::string, int> ages{{"ada", 36}, {"bob", 25}};
for (const auto& name : ages | rv::keys) std::cout << name << ' ';

for (auto [i, x] : rv::enumerate(v)) std::cout << i << ':' << x << ' ';     // C++23
for (auto [a, b] : rv::zip(xs, ys)) dot += a * b;                         // C++23

auto evens = v | rv::filter([](int x) { return x % 2 == 0; });
std::vector<int> owned(evens.begin(), evens.end());                       // materialise
auto squares = rv::iota(1, 6) | rv::transform([](int x) { return x * x; })
             | std::ranges::to<std::vector>();                            // C++23
```

> [!WARNING]
> Views **reference** their source, so they dangle if the source dies first. `auto bad = std::vector{1, 2, 3} | rv::filter(...)` is rejected for temporaries in many cases (ranges have dangling protection), but storing a view of a local container and returning it is a real bug. Also, `filter` caches its `begin()`, so modifying elements through a filter view so that they no longer satisfy the predicate is undefined behaviour. Treat views as short-lived, read-mostly pipelines.

## 3. Laziness and cost

```cpp
auto big = rv::iota(0) | rv::transform(expensive) | rv::filter(pred) | rv::take(10);
```

This computes `expensive` only for the elements actually examined. That's the same benefit as Python generators: infinite sequences, early termination, no temporaries. But it's not free: each `++` walks the adaptor chain, and `filter` may re-evaluate the predicate. Compilers inline the chain well. Where performance matters, measure against a plain loop.

## 4. Concepts make errors readable

Ranges are constrained with C++20 **concepts** (`std::ranges::random_access_range`, `std::sortable`). Calling `std::ranges::sort` on a `std::list` gives a short "constraints not satisfied" message instead of pages of template errors. The Templates module covers writing your own concepts.

## 5. Exam-ready answers

> [!EXAM]
> **Ranges.** The C++20 Ranges library generalises iterator pairs into ranges, objects providing `begin` and `end`. Range algorithms in `std::ranges` accept whole ranges, support projections that transform elements before comparison or testing, and are constrained by concepts that produce clearer diagnostics. Views are lightweight, non-owning ranges that lazily transform or filter an underlying range; range adaptors such as `views::filter`, `views::transform`, `views::take` and `views::reverse` can be composed with the pipe operator into pipelines, and elements are computed on demand as the pipeline is iterated, without intermediate containers. Because views refer to their underlying data, they must not outlive it.

## 6. Cheat sheet

| Need | Code |
|---|---|
| sort a whole container | `std::ranges::sort(v)` |
| sort by a member | `std::ranges::sort(v, {}, &T::field)` |
| filter + map | `v \| views::filter(p) \| views::transform(f)` |
| first n results | `\| views::take(n)` |
| map keys / values | `m \| views::keys` / `views::values` |
| index + element | `views::enumerate(v)` (C++23) |
| to a vector | `\| std::ranges::to<std::vector>()` (C++23) |
| numbers a..b-1 | `views::iota(a, b)` |

> [!INTERVIEW]
> **"What's the advantage of `v | views::filter(p) | views::transform(f) | views::take(k)` over the equivalent STL calls?"** With classic algorithms you'd `copy_if` into a temporary vector, `transform` into another, then truncate: two allocations, full passes over all the data, and f computed for every filtered element. The view pipeline is lazy: it allocates nothing, stops after k results, computes f only for elements actually produced, reads as a declarative pipeline, and works on infinite ranges. The caveats are lifetime (views don't own data) and that some views, like `filter`, have per-iteration overhead.
