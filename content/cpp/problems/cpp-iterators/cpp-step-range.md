---
id: cpp-step-range
title: A Range Class with Real Iterators
difficulty: Medium
order: 1
tags: iterators, iterator categories, range-for, STL compatibility
---
## Statement
Implement `StepRange`, a lazy arithmetic sequence like Python's `range(start, stop, step)`, with an iterator that works with range-for, standard algorithms **and** C++20 ranges:

```cpp
class StepRange {
public:
    StepRange(long long start, long long stop, long long step = 1);  // step != 0, else std::invalid_argument
    class iterator;            // a forward iterator yielding long long values
    iterator begin() const;
    iterator end() const;
    std::size_t size() const;  // the number of elements (0 if empty)
};
```

Semantics match Python's: for a positive step the values are `start, start+step, …` while `< stop`; for a negative step, while `> stop`. Your iterator must:
- define `value_type`, `difference_type`, `iterator_category` (`std::forward_iterator_tag`), plus `reference` and `pointer`,
- support `*it`, `++it`, `it++` and `==`/`!=`, and be default-constructible,
- make `end()` compare equal to the iterator reached after the last element, even when `(stop - start)` isn't a multiple of `step`. Normalise `end()` to the exact one-past-the-last value.

The driver checks the iterator with `std::forward_iterator` (a C++20 concept), then uses it with `std::accumulate`, `std::find`, `std::distance`, `std::count_if`, `std::vector`'s range constructor, and a `std::views::filter` pipeline.

## Starter
```cpp
#include <cstddef>
#include <iterator>
#include <stdexcept>

class StepRange {
public:
    StepRange(long long start, long long stop, long long step = 1) : start_(start), stop_(stop), step_(step) {}
    class iterator {
    public:
        long long cur = 0, step = 1;
        long long operator*() const { return cur; }
        iterator& operator++() { cur += step; return *this; }
        bool operator!=(const iterator& o) const { return cur != o.cur; }
    };
    iterator begin() const { return {start_, step_}; }
    iterator end() const { return {stop_, step_}; }
    std::size_t size() const { return 0; }
private:
    long long start_, stop_, step_;
};
```

## Driver
```cpp
#include <iostream>
#include <numeric>
#include <algorithm>
#include <vector>
#include <ranges>

static_assert(std::forward_iterator<StepRange::iterator>, "must model std::forward_iterator");
static_assert(std::ranges::forward_range<StepRange>);

int main() {
    long long a, b, s;
    while (std::cin >> a >> b >> s) {
        try {
            StepRange r(a, b, s);
            std::cout << "range(" << a << ", " << b << ", " << s << "): size=" << r.size()
                      << " dist=" << std::distance(r.begin(), r.end());
            std::cout << " sum=" << std::accumulate(r.begin(), r.end(), 0LL);
            auto it = std::find(r.begin(), r.end(), 0LL);
            std::cout << " has0=" << (it != r.end());
            std::cout << " odd=" << std::count_if(r.begin(), r.end(), [](long long x) { return x % 2 != 0; });
            std::vector<long long> v(r.begin(), r.end());
            std::cout << " first5=[";
            for (std::size_t i = 0; i < v.size() && i < 5; ++i) std::cout << (i ? "," : "") << v[i];
            std::cout << "] div3=";
            int shown = 0;
            for (long long x : r | std::views::filter([](long long x) { return x % 3 == 0; })) {
                if (shown++ == 3) break;
                std::cout << x << ';';
            }
            auto p = r.begin();
            auto q = p++;
            std::cout << " postinc=" << (r.size() >= 2 ? (*q == a && (p == std::next(r.begin()))) : true) << '\n';
        } catch (const std::invalid_argument&) {
            std::cout << "invalid step\n";
        }
    }
}
```

## Tests
=== sample
0 10 1
0 10 3
10 0 -3
5 5 1
1 0 1
0 10 0
---
range(0, 10, 1): size=10 dist=10 sum=45 has0=1 odd=5 first5=[0,1,2,3,4] div3=0;3;6; postinc=1
range(0, 10, 3): size=4 dist=4 sum=18 has0=1 odd=2 first5=[0,3,6,9] div3=0;3;6; postinc=1
range(10, 0, -3): size=4 dist=4 sum=22 has0=0 odd=2 first5=[10,7,4,1] div3= postinc=1
range(5, 5, 1): size=0 dist=0 sum=0 has0=0 odd=0 first5=[] div3= postinc=1
range(1, 0, 1): size=0 dist=0 sum=0 has0=0 odd=0 first5=[] div3= postinc=1
invalid step
=== hidden
-7 8 5
100 -100 -7
0 1000000 1
0 1000000000 999999999
-1 -2 -1
3 4 100
---
range(-7, 8, 5): size=3 dist=3 sum=-6 has0=0 odd=2 first5=[-7,-2,3] div3=3; postinc=1
range(100, -100, -7): size=29 dist=29 sum=58 has0=0 odd=14 first5=[100,93,86,79,72] div3=93;72;51; postinc=1
range(0, 1000000, 1): size=1000000 dist=1000000 sum=499999500000 has0=1 odd=500000 first5=[0,1,2,3,4] div3=0;3;6; postinc=1
range(0, 1000000000, 999999999): size=2 dist=2 sum=999999999 has0=1 odd=1 first5=[0,999999999] div3=0;999999999; postinc=1
range(-1, -2, -1): size=1 dist=1 sum=-1 has0=0 odd=1 first5=[-1] div3= postinc=1
range(3, 4, 100): size=1 dist=1 sum=3 has0=0 odd=1 first5=[3] div3=3; postinc=1

## Hints
- `size()`: for `step > 0`, it's `stop > start ? (stop - start + step - 1) / step : 0`. For `step < 0`, mirror it.
- `end()` is `start + size() * step`, which is exactly where iteration stops, so `==` on the current value works.
- To satisfy `std::forward_iterator`, the iterator needs those member types, default construction, `operator==` (and `!=` is then generated), pre- and post-increment, and a `const` `operator*`. Using `value_type` as the `reference` type (returning by value) is allowed.

## Solution
```cpp
#include <cstddef>
#include <iterator>
#include <stdexcept>

class StepRange {
public:
    StepRange(long long start, long long stop, long long step = 1)
        : start_(start), step_(step) {
        if (step == 0) throw std::invalid_argument("step must not be zero");
        long long n = 0;
        if (step > 0 && stop > start) n = (stop - start + step - 1) / step;
        if (step < 0 && stop < start) n = (start - stop + (-step) - 1) / (-step);
        size_ = static_cast<std::size_t>(n);
    }

    class iterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = long long;
        using difference_type = std::ptrdiff_t;
        using reference = long long;          // values are computed, so return by value
        using pointer = void;

        iterator() = default;
        iterator(long long cur, long long step) : cur_(cur), step_(step) {}
        long long operator*() const { return cur_; }
        iterator& operator++() { cur_ += step_; return *this; }
        iterator operator++(int) { iterator t = *this; ++*this; return t; }
        bool operator==(const iterator& o) const { return cur_ == o.cur_; }
    private:
        long long cur_ = 0, step_ = 1;
    };

    iterator begin() const { return {start_, step_}; }
    iterator end() const { return {start_ + static_cast<long long>(size_) * step_, step_}; }  // exact one-past-the-last
    std::size_t size() const { return size_; }

private:
    long long start_, step_;
    std::size_t size_;
};
```

- **Normalised `end()`** is the key design point: the iterator stops exactly where the loop would land after the last element, so plain `==` on the current value is a correct termination test for any step. The starter's `end() = stop` never matches when `stop - start` isn't a multiple of the step, and runs forever.
- **The member types** let `std::iterator_traits` and the C++20 concepts recognise the category, so algorithms like `std::distance` choose the right strategy, and `std::views::filter` accepts the range.
- **Laziness:** the range stores three numbers, no matter how many elements it represents (try `0 1000000 1`). Generators and views are built on exactly this kind of iterator.
