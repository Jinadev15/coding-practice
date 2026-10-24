---
id: cpp-grid-cpp23
title: An Occupancy Grid in C++23 Style
difficulty: Hard
order: 1
tags: C++23, deducing this, multidimensional subscript, std::formatter, std::print, ranges
---
## Statement
Robots map their surroundings as **occupancy grids**. Implement one using C++23 features:

```cpp
enum class Cell : char { Free = '.', Occupied = '#', Unknown = '?' };

class Grid {
public:
    Grid(std::size_t rows, std::size_t cols, Cell fill = Cell::Unknown);
    std::size_t rows() const; std::size_t cols() const;

    // ONE at() using an explicit object parameter (deducing this) that works on const and
    // non-const grids, returning Cell& or const Cell&; throws std::out_of_range when out of bounds
    template <typename Self> auto&& at(this Self&& self, std::size_t r, std::size_t c);

    // a C++23 multidimensional subscript: g[r, c] (unchecked), also via deducing this
    template <typename Self> auto&& operator[](this Self&& self, std::size_t r, std::size_t c);

    void mark_line(std::size_t r0, std::size_t c0, std::size_t r1, std::size_t c1, Cell value);  // Bresenham line
    std::size_t count(Cell value) const;                    // use std::ranges::count
    std::vector<std::pair<std::size_t, std::size_t>> neighbours(std::size_t r, std::size_t c) const;  // 4-connected, in bounds
    std::optional<int> shortest_path(std::size_t r0, std::size_t c0, std::size_t r1, std::size_t c1) const;  // BFS through non-Occupied cells
};

template <> struct std::formatter<Grid>;   // std::format("{}", g) prints the rows separated by '\n'
```

Bresenham: mark every cell on the line from (r0, c0) to (r1, c1) inclusive, using the standard integer algorithm (with `err = dx - dy`, stepping x when `2·err > -dy` and y when `2·err < dx`, where x is the column and y the row). `shortest_path` counts moves; it's `std::nullopt` if the target is unreachable or either endpoint is occupied.

## Starter
```cpp
#include <vector>
#include <format>
#include <optional>
#include <cstddef>

enum class Cell : char { Free = '.', Occupied = '#', Unknown = '?' };

class Grid {
public:
    Grid(std::size_t rows, std::size_t cols, Cell fill = Cell::Unknown) {}
};
```

## Driver
```cpp
#include <print>
#include <iostream>
#include <string>
#include <type_traits>

static_assert(std::is_same_v<decltype(std::declval<Grid&>().at(0, 0)), Cell&>);
static_assert(std::is_same_v<decltype(std::declval<const Grid&>().at(0, 0)), const Cell&>);
static_assert(std::is_same_v<decltype(std::declval<const Grid&>()[0, 0]), const Cell&>);

int main() {
    std::size_t R, C;
    std::cin >> R >> C;
    Grid g(R, C, Cell::Free);
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "wall") {
            std::size_t r0, c0, r1, c1;
            std::cin >> r0 >> c0 >> r1 >> c1;
            g.mark_line(r0, c0, r1, c1, Cell::Occupied);
        } else if (cmd == "unknown") {
            std::size_t r, c;
            std::cin >> r >> c;
            g[r, c] = Cell::Unknown;
        } else if (cmd == "path") {
            std::size_t r0, c0, r1, c1;
            std::cin >> r0 >> c0 >> r1 >> c1;
            auto d = g.shortest_path(r0, c0, r1, c1);
            if (d) std::println("path ({},{})->({},{}) = {}", r0, c0, r1, c1, *d);
            else std::println("path ({},{})->({},{}) = unreachable", r0, c0, r1, c1);
        } else if (cmd == "probe") {
            std::size_t r, c;
            std::cin >> r >> c;
            try {
                const Grid& cg = g;
                std::println("probe ({},{}) = '{}' with {} neighbours", r, c, static_cast<char>(cg.at(r, c)), cg.neighbours(r, c).size());
            } catch (const std::out_of_range&) {
                std::println("probe ({},{}) = out of range", r, c);
            }
        }
    }
    std::println("{}", g);
    std::println("free={} occupied={} unknown={}", g.count(Cell::Free), g.count(Cell::Occupied), g.count(Cell::Unknown));
}
```

## Tests
=== sample
5 8
wall 0 3 3 3
wall 4 0 4 2
unknown 2 6
probe 0 0
probe 4 7
probe 9 9
path 0 0 0 7
path 0 0 4 0
path 4 1 0 0
path 0 4 4 7
path 0 0 3 2
---
probe (0,0) = '.' with 2 neighbours
probe (4,7) = '.' with 2 neighbours
probe (9,9) = out of range
path (0,0)->(0,7) = unreachable
path (0,0)->(4,0) = unreachable
path (4,1)->(0,0) = unreachable
path (0,4)->(4,7) = 7
path (0,0)->(3,2) = 5
...#....
...#....
...#..?.
...#....
###.....
free=32 occupied=7 unknown=1
=== hidden
6 6
wall 0 0 5 5
wall 5 0 0 5
path 0 1 1 0
path 0 1 0 4
probe 2 2
probe 0 5
---
path (0,1)->(1,0) = unreachable
path (0,1)->(0,4) = 3
probe (2,2) = '#' with 4 neighbours
probe (0,5) = '#' with 2 neighbours
#....#
.#..#.
..##..
..##..
.#..#.
#....#
free=24 occupied=12 unknown=0
=== hidden
3 10
wall 1 0 1 8
path 0 0 2 0
path 0 0 2 9
wall 0 9 2 9
path 0 0 2 0
unknown 0 0
probe 0 0
---
path (0,0)->(2,0) = 20
path (0,0)->(2,9) = 11
path (0,0)->(2,0) = unreachable
probe (0,0) = '?' with 2 neighbours
?........#
##########
.........#
free=17 occupied=12 unknown=1

## Hints
- Store the cells in a `std::vector<Cell>` with index `r * cols + c`. `at` checks the bounds, then returns `std::forward<Self>(self).cells_[...]`. The constness of `self` flows through to the returned reference automatically.
- A multidimensional `operator[]` is legal in C++23: `auto&& operator[](this Self&& self, std::size_t r, std::size_t c)`.
- Formatter: `template <> struct std::formatter<Grid> { constexpr auto parse(std::format_parse_context& ctx) { return ctx.begin(); } auto format(const Grid& g, std::format_context& ctx) const { ... std::format_to(ctx.out(), ...) ... } };`
- BFS with a `std::queue` and a distance vector initialised to -1. Unknown cells are traversable (optimistic planning), and occupied cells aren't.

## Solution
```cpp
#include <vector>
#include <format>
#include <optional>
#include <cstddef>
#include <stdexcept>
#include <algorithm>
#include <queue>
#include <cstdlib>
#include <utility>

enum class Cell : char { Free = '.', Occupied = '#', Unknown = '?' };

class Grid {
public:
    Grid(std::size_t rows, std::size_t cols, Cell fill = Cell::Unknown)
        : rows_(rows), cols_(cols), cells_(rows * cols, fill) {}
    std::size_t rows() const { return rows_; }
    std::size_t cols() const { return cols_; }

    template <typename Self>
    auto&& at(this Self&& self, std::size_t r, std::size_t c) {
        if (r >= self.rows_ || c >= self.cols_) throw std::out_of_range("grid index");
        return std::forward<Self>(self).cells_[r * self.cols_ + c];
    }

    template <typename Self>
    auto&& operator[](this Self&& self, std::size_t r, std::size_t c) {
        return std::forward<Self>(self).cells_[r * self.cols_ + c];
    }

    void mark_line(std::size_t r0, std::size_t c0, std::size_t r1, std::size_t c1, Cell value) {
        long x0 = static_cast<long>(c0), y0 = static_cast<long>(r0);
        long x1 = static_cast<long>(c1), y1 = static_cast<long>(r1);
        long dx = std::labs(x1 - x0), dy = std::labs(y1 - y0);
        long sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
        long err = dx - dy;
        while (true) {
            at(static_cast<std::size_t>(y0), static_cast<std::size_t>(x0)) = value;
            if (x0 == x1 && y0 == y1) break;
            long e2 = 2 * err;
            if (e2 > -dy) { err -= dy; x0 += sx; }
            if (e2 < dx) { err += dx; y0 += sy; }
        }
    }

    std::size_t count(Cell value) const { return static_cast<std::size_t>(std::ranges::count(cells_, value)); }

    std::vector<std::pair<std::size_t, std::size_t>> neighbours(std::size_t r, std::size_t c) const {
        std::vector<std::pair<std::size_t, std::size_t>> out;
        if (r > 0) out.emplace_back(r - 1, c);
        if (r + 1 < rows_) out.emplace_back(r + 1, c);
        if (c > 0) out.emplace_back(r, c - 1);
        if (c + 1 < cols_) out.emplace_back(r, c + 1);
        return out;
    }

    std::optional<int> shortest_path(std::size_t r0, std::size_t c0, std::size_t r1, std::size_t c1) const {
        if ((*this)[r0, c0] == Cell::Occupied || (*this)[r1, c1] == Cell::Occupied) return std::nullopt;
        std::vector<int> dist(cells_.size(), -1);
        std::queue<std::pair<std::size_t, std::size_t>> q;
        dist[r0 * cols_ + c0] = 0;
        q.emplace(r0, c0);
        while (!q.empty()) {
            auto [r, c] = q.front();
            q.pop();
            if (r == r1 && c == c1) return dist[r * cols_ + c];
            for (auto [nr, nc] : neighbours(r, c)) {
                std::size_t k = nr * cols_ + nc;
                if (dist[k] == -1 && (*this)[nr, nc] != Cell::Occupied) {
                    dist[k] = dist[r * cols_ + c] + 1;
                    q.emplace(nr, nc);
                }
            }
        }
        return std::nullopt;
    }

private:
    std::size_t rows_, cols_;
    std::vector<Cell> cells_;
};

template <>
struct std::formatter<Grid> {
    constexpr auto parse(std::format_parse_context& ctx) { return ctx.begin(); }
    auto format(const Grid& g, std::format_context& ctx) const {
        auto out = ctx.out();
        for (std::size_t r = 0; r < g.rows(); ++r) {
            if (r) *out++ = '\n';
            for (std::size_t c = 0; c < g.cols(); ++c) *out++ = static_cast<char>(g[r, c]);
        }
        return out;
    }
};
```

**The C++23 features at work:**
- **Deducing `this`:** one `at` and one `operator[]` replace the classic const/non-const overload pairs. `Self` is deduced as `Grid&` or `const Grid&`, and `std::forward<Self>(self).cells_[...]` yields `Cell&` or `const Cell&` accordingly (verified by the `static_assert`s).
- **Multidimensional subscripts:** `g[r, c]` is finally legal syntax (before C++23, `g[r, c]` invoked the comma operator!), the same notation `std::mdspan` uses.
- **`std::formatter` specialization** plugs the type into `std::format`/`std::println` like a built-in, which is the modern replacement for `operator<<`.
- **Ranges** (`std::ranges::count`) and a **BFS on an occupancy grid**: the textbook first step in mobile-robot path planning.
