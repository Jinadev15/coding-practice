---
id: cpp-geometry-library
title: A Multi-File Geometry Library (Headers, Sources, ODR)
difficulty: Hard
order: 1
tags: header/source organization, ODR, inline, constexpr, namespaces, anonymous namespace, multi-file
time_limit: 4
---
## Statement
Organise a small 2-D geometry library correctly across headers and sources. The judge compiles **two translation units** (`main.cpp` and `other.cpp`) that both include your headers, so any definition that breaks the **One Definition Rule** fails at link time.

**Files to write**
1. `vec2.hpp` (**header-only**): `namespace geo` with:
   - `inline constexpr double kEps = 1e-9`;
   - an aggregate `Vec2 {x, y}` with `+`, `-`, `*` (by a scalar) and defaulted `==`, all `constexpr`;
   - `constexpr dot`, `constexpr cross` and `norm`.
   Every definition here must be legal in many TUs.
2. `polygon.cpp`: implement the `geo::Polygon` declared in `polygon.hpp`:
   - The constructor throws `std::invalid_argument` with fewer than 3 points.
   - `area` (absolute shoelace), `perimeter`, `centroid` (area-weighted), and `is_convex` (ignoring collinear vertices).
   - `contains`: even-odd ray casting, where points within `kEps` of an edge count as inside.
   Helpers go in an **anonymous namespace**.
3. `collision.cpp`: `geo::collision::point_segment_distance`, `segments_intersect` (endpoints touching and collinear overlaps count), and `convex_overlap` (separating axis theorem, where touching counts as overlapping).

`polygon.hpp` and `collision.hpp` are given. Don't change them.

## Starter: vec2.hpp
```cpp
#pragma once
#include <cmath>

namespace geo {

double kEps = 1e-9;                                    // non-inline variable in a header: ODR violation

struct Vec2 {
    double x = 0, y = 0;
    Vec2 operator+(Vec2 o) const { return {x + o.x, y + o.y}; }
    Vec2 operator-(Vec2 o) const { return {x - o.x, y - o.y}; }
    Vec2 operator*(double s) const { return {x * s, y * s}; }
    bool operator==(const Vec2&) const = default;
};

double dot(Vec2 a, Vec2 b) { return a.x * b.x + a.y * b.y; }      // non-inline functions in a header
double cross(Vec2 a, Vec2 b) { return a.x * b.y - a.y * b.x; }
double norm(Vec2 a) { return std::sqrt(dot(a, a)); }

}  // namespace geo
```

## Starter: polygon.hpp
```cpp
#pragma once
#include <vector>
#include "vec2.hpp"

namespace geo {

class Polygon {
public:
    explicit Polygon(std::vector<Vec2> pts);   // throws std::invalid_argument if fewer than 3 points
    double area() const;                       // absolute area (shoelace)
    double perimeter() const;
    Vec2 centroid() const;
    bool contains(Vec2 p) const;               // boundary counts as inside
    bool is_convex() const;
    const std::vector<Vec2>& points() const { return pts_; }
private:
    std::vector<Vec2> pts_;
};

}  // namespace geo
```

## Starter: collision.hpp
```cpp
#pragma once
#include "polygon.hpp"
#include "vec2.hpp"

namespace geo::collision {

double point_segment_distance(Vec2 p, Vec2 a, Vec2 b);
bool segments_intersect(Vec2 a, Vec2 b, Vec2 c, Vec2 d);    // touching counts
bool convex_overlap(const Polygon& a, const Polygon& b);    // separating axis theorem; touching counts

}  // namespace geo::collision
```

## Starter: polygon.cpp
```cpp
#include "polygon.hpp"
// TODO: implement Polygon here (polygon.hpp only declares it)
```

## Starter: collision.cpp
```cpp
#include "collision.hpp"
// TODO: implement geo::collision functions here
```

## Driver: main.cpp
```cpp
#include <cstdio>
#include <iostream>
#include <string>
#include "collision.hpp"
#include "polygon.hpp"
#include "vec2.hpp"

double tu2_total_area(int n);                        // defined in other.cpp (a second translation unit)
bool tu2_check();

int main() {
    using namespace geo;
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "polygon") {
            Polygon sq({{0, 0}, {4, 0}, {4, 4}, {0, 4}});
            Polygon tri({{0, 0}, {6, 0}, {0, 3}});
            Polygon ell({{0, 0}, {4, 0}, {4, 1}, {1, 1}, {1, 4}, {0, 4}});
            for (const Polygon* p : {&sq, &tri, &ell}) {
                Vec2 c = p->centroid();
                std::printf("area %.4f perim %.4f centroid (%.4f, %.4f) convex %d\n", p->area(), p->perimeter(), c.x, c.y, p->is_convex());
            }
            Vec2 probes[] = {{2, 2}, {4, 2}, {5, 2}, {0, 0}, {3, 3}, {0.5, 3}, {2.5, 2.5}};
            for (Vec2 q : probes) std::printf("(%.1f,%.1f): sq %d tri %d ell %d\n", q.x, q.y, sq.contains(q), tri.contains(q), ell.contains(q));
            try { Polygon bad({{0, 0}, {1, 1}}); } catch (const std::invalid_argument&) { std::printf("2-point polygon rejected\n"); }
            Polygon cw({{0, 0}, {0, 2}, {2, 2}, {2, 0}});
            std::printf("clockwise area %.4f\n", cw.area());
        } else if (cmd == "collision") {
            using namespace geo::collision;
            std::printf("dist %.4f %.4f %.4f\n", point_segment_distance({0, 1}, {-1, 0}, {1, 0}), point_segment_distance({3, 4}, {0, 0}, {0, 0}),
                        point_segment_distance({5, 0}, {0, 0}, {2, 0}));
            std::printf("seg %d %d %d %d %d\n", segments_intersect({0, 0}, {2, 2}, {0, 2}, {2, 0}), segments_intersect({0, 0}, {1, 1}, {2, 2}, {3, 3}),
                        segments_intersect({0, 0}, {2, 2}, {2, 2}, {3, 0}), segments_intersect({0, 0}, {2, 0}, {1, 0}, {3, 0}),
                        segments_intersect({0, 0}, {1, 0}, {0, 1}, {1, 1}));
            Polygon a({{0, 0}, {2, 0}, {2, 2}, {0, 2}}), b({{1, 1}, {3, 1}, {3, 3}, {1, 3}}), c({{2, 0}, {3, 0}, {3, 1}}), d({{2.5, 2.5}, {4, 2.5}, {4, 4}});
            std::printf("overlap ab %d ac %d ad %d bd %d\n", convex_overlap(a, b), convex_overlap(a, c), convex_overlap(a, d), convex_overlap(b, d));
            std::printf("kEps %.0e\n", kEps);
        } else if (cmd == "units") {
            std::printf("tu2 total area %.4f, tu2 check %d\n", tu2_total_area(5000), tu2_check());
        }
    }
}
```

## Driver: other.cpp
```cpp
// A second translation unit including the same headers: catches ODR violations at link time.
#include "collision.hpp"
#include "polygon.hpp"
#include "vec2.hpp"

double tu2_total_area(int n) {
    double total = 0;
    for (int i = 1; i <= n; ++i) {
        double r = 1 + i % 7;
        geo::Polygon p({{0, 0}, {r, 0}, {r, r * 0.5}, {0, r}});
        total += p.area() + p.perimeter() * 0.001;
    }
    return total;
}

bool tu2_check() {
    constexpr geo::Vec2 a{1, 2}, b{3, 4};
    static_assert(geo::dot(a, b) == 11 && geo::cross(a, b) == -2, "constexpr helpers");
    return geo::norm(a - b) > 2.8 && geo::collision::segments_intersect({0, 0}, {1, 1}, {0, 1}, {1, 0});
}
```

## Tests
=== sample
polygon
---
area 16.0000 perim 16.0000 centroid (2.0000, 2.0000) convex 1
area 9.0000 perim 15.7082 centroid (2.0000, 1.0000) convex 1
area 7.0000 perim 16.0000 centroid (1.3571, 1.3571) convex 0
(2.0,2.0): sq 1 tri 1 ell 0
(4.0,2.0): sq 1 tri 0 ell 0
(5.0,2.0): sq 0 tri 0 ell 0
(0.0,0.0): sq 1 tri 1 ell 1
(3.0,3.0): sq 1 tri 0 ell 0
(0.5,3.0): sq 1 tri 0 ell 1
(2.5,2.5): sq 1 tri 0 ell 0
2-point polygon rejected
clockwise area 4.0000
=== hidden
collision
---
dist 1.0000 5.0000 3.0000
seg 1 0 1 1 0
overlap ab 1 ac 1 ad 0 bd 1
kEps 1e-09
=== hidden
units
---
tu2 total area 75052.0998, tu2 check 1

## Hints
- In a header, a namespace-scope variable needs `inline` (or `inline constexpr`). Free functions need `inline` or `constexpr`, because `constexpr` functions are implicitly inline. Member functions defined inside the class body are implicitly inline.
- The starter's `vec2.hpp` fails to **link** ("multiple definition of `geo::dot`") the moment two `.cpp` files include it. That's the bug to fix.
- Shoelace: `A = ½ Σ cross(pᵢ, pᵢ₊₁)`. Centroid: `C = Σ (pᵢ + pᵢ₊₁)·cross(pᵢ, pᵢ₊₁) / (6A)`, using the **signed** A.
- SAT for convex polygons: for each edge normal of both polygons, project both polygons onto the axis. If the intervals don't overlap anywhere, the polygons are separated.

## Solution: vec2.hpp
```cpp
#pragma once
#include <cmath>

namespace geo {

inline constexpr double kEps = 1e-9;

struct Vec2 {
    double x = 0, y = 0;
    constexpr Vec2 operator+(Vec2 o) const { return {x + o.x, y + o.y}; }
    constexpr Vec2 operator-(Vec2 o) const { return {x - o.x, y - o.y}; }
    constexpr Vec2 operator*(double s) const { return {x * s, y * s}; }
    constexpr bool operator==(const Vec2&) const = default;
};

constexpr double dot(Vec2 a, Vec2 b) { return a.x * b.x + a.y * b.y; }
constexpr double cross(Vec2 a, Vec2 b) { return a.x * b.y - a.y * b.x; }
inline double norm(Vec2 a) { return std::sqrt(dot(a, a)); }

}  // namespace geo
```

## Solution: polygon.hpp
```cpp
#pragma once
#include <vector>
#include "vec2.hpp"

namespace geo {

class Polygon {
public:
    explicit Polygon(std::vector<Vec2> pts);   // throws std::invalid_argument if fewer than 3 points
    double area() const;                       // absolute area (shoelace)
    double perimeter() const;
    Vec2 centroid() const;
    bool contains(Vec2 p) const;               // boundary counts as inside
    bool is_convex() const;
    const std::vector<Vec2>& points() const { return pts_; }
private:
    std::vector<Vec2> pts_;
};

}  // namespace geo
```

## Solution: collision.hpp
```cpp
#pragma once
#include "polygon.hpp"
#include "vec2.hpp"

namespace geo::collision {

double point_segment_distance(Vec2 p, Vec2 a, Vec2 b);
bool segments_intersect(Vec2 a, Vec2 b, Vec2 c, Vec2 d);    // touching counts
bool convex_overlap(const Polygon& a, const Polygon& b);    // separating axis theorem; touching counts

}  // namespace geo::collision
```

## Solution: polygon.cpp
```cpp
#include "polygon.hpp"

#include <algorithm>
#include <stdexcept>

#include "collision.hpp"

namespace geo {

Polygon::Polygon(std::vector<Vec2> pts) : pts_(std::move(pts)) {
    if (pts_.size() < 3) throw std::invalid_argument("polygon needs at least 3 points");
}

namespace {                                            // internal linkage: private helper
double signed_area(const std::vector<Vec2>& p) {
    double s = 0;
    for (std::size_t i = 0, n = p.size(); i < n; ++i) s += cross(p[i], p[(i + 1) % n]);
    return s / 2.0;
}
}  // namespace

double Polygon::area() const { return std::abs(signed_area(pts_)); }

double Polygon::perimeter() const {
    double s = 0;
    for (std::size_t i = 0, n = pts_.size(); i < n; ++i) s += norm(pts_[(i + 1) % n] - pts_[i]);
    return s;
}

Vec2 Polygon::centroid() const {
    double a = signed_area(pts_), cx = 0, cy = 0;
    for (std::size_t i = 0, n = pts_.size(); i < n; ++i) {
        Vec2 p = pts_[i], q = pts_[(i + 1) % n];
        double c = cross(p, q);
        cx += (p.x + q.x) * c;
        cy += (p.y + q.y) * c;
    }
    return {cx / (6 * a), cy / (6 * a)};
}

bool Polygon::contains(Vec2 p) const {
    const std::size_t n = pts_.size();
    for (std::size_t i = 0; i < n; ++i)                    // boundary check first
        if (collision::point_segment_distance(p, pts_[i], pts_[(i + 1) % n]) < kEps) return true;
    bool inside = false;                                   // even-odd ray casting
    for (std::size_t i = 0, j = n - 1; i < n; j = i++) {
        const Vec2 a = pts_[i], b = pts_[j];
        if ((a.y > p.y) != (b.y > p.y) && p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x) inside = !inside;
    }
    return inside;
}

bool Polygon::is_convex() const {
    int sign = 0;
    for (std::size_t i = 0, n = pts_.size(); i < n; ++i) {
        double c = cross(pts_[(i + 1) % n] - pts_[i], pts_[(i + 2) % n] - pts_[(i + 1) % n]);
        if (std::abs(c) < kEps) continue;
        int s = c > 0 ? 1 : -1;
        if (sign && s != sign) return false;
        sign = s;
    }
    return true;
}

}  // namespace geo
```

## Solution: collision.cpp
```cpp
#include "collision.hpp"

#include <algorithm>
#include <limits>

namespace geo::collision {

double point_segment_distance(Vec2 p, Vec2 a, Vec2 b) {
    Vec2 ab = b - a;
    double len2 = dot(ab, ab);
    double t = len2 < kEps ? 0.0 : std::clamp(dot(p - a, ab) / len2, 0.0, 1.0);
    return norm(p - (a + ab * t));
}

namespace {
int orient(Vec2 a, Vec2 b, Vec2 c) {
    double v = cross(b - a, c - a);
    return v > kEps ? 1 : v < -kEps ? -1 : 0;
}
bool on_segment(Vec2 a, Vec2 b, Vec2 p) {
    return std::min(a.x, b.x) - kEps <= p.x && p.x <= std::max(a.x, b.x) + kEps &&
           std::min(a.y, b.y) - kEps <= p.y && p.y <= std::max(a.y, b.y) + kEps;
}
void project(const Polygon& poly, Vec2 axis, double& lo, double& hi) {
    lo = std::numeric_limits<double>::infinity();
    hi = -lo;
    for (Vec2 p : poly.points()) { double d = dot(p, axis); lo = std::min(lo, d); hi = std::max(hi, d); }
}
bool separated_on_edges_of(const Polygon& a, const Polygon& b) {
    const auto& p = a.points();
    for (std::size_t i = 0, n = p.size(); i < n; ++i) {
        Vec2 e = p[(i + 1) % n] - p[i];
        Vec2 axis{-e.y, e.x};
        double alo, ahi, blo, bhi;
        project(a, axis, alo, ahi);
        project(b, axis, blo, bhi);
        if (ahi < blo - kEps || bhi < alo - kEps) return true;      // a gap: separating axis found
    }
    return false;
}
}  // namespace

bool segments_intersect(Vec2 a, Vec2 b, Vec2 c, Vec2 d) {
    int o1 = orient(a, b, c), o2 = orient(a, b, d), o3 = orient(c, d, a), o4 = orient(c, d, b);
    if (o1 != o2 && o3 != o4) return true;
    if (o1 == 0 && on_segment(a, b, c)) return true;
    if (o2 == 0 && on_segment(a, b, d)) return true;
    if (o3 == 0 && on_segment(c, d, a)) return true;
    if (o4 == 0 && on_segment(c, d, b)) return true;
    return false;
}

bool convex_overlap(const Polygon& a, const Polygon& b) {
    return !separated_on_edges_of(a, b) && !separated_on_edges_of(b, a);
}

}  // namespace geo::collision
```

## Solution
- **Header-only code must be ODR-safe**: `inline constexpr` variables and `constexpr` functions (which are implicitly inline) may appear in every TU. The starter's plain definitions link fine with one `.cpp` file and break with two. This exercise's second translation unit exists exactly to catch that.
- **Declarations in headers, definitions in sources**: `Polygon` and the collision functions are declared once and compiled once. Changing an algorithm recompiles one `.cpp` file, not every includer.
- **Anonymous namespaces** give helpers like `signed_area` and `orient` internal linkage, so they can't clash with another TU's helpers or be called from outside.
- **Namespaces as components** (`geo`, `geo::collision`) mirror the library structure, and the dependency direction is clean: collision depends on polygon and vec2, never the reverse.
- **Robust geometry**: an epsilon-tolerant orientation test, explicit boundary handling in `contains`, and SAT for convex overlap. These are the same building blocks used by collision checkers in planners such as MoveIt's FCL.
