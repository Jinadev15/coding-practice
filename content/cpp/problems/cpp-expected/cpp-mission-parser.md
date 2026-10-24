---
id: cpp-mission-parser
title: Mission File Parser with std::expected
difficulty: Medium
order: 1
tags: std::expected, error handling, monadic operations, parsing
---
## Statement
A drone mission file lists waypoints. Parse it with `std::expected` and **no exceptions** (the problem is compiled normally, but your code must not throw).

```cpp
struct Waypoint { double lat, lon, alt; int hold_s; };
struct ParseError { int line; std::string message; };

std::expected<double, std::string> parse_double(std::string_view s);      // whole string must be a number
std::expected<Waypoint, std::string> parse_waypoint(std::string_view line);
std::expected<std::vector<Waypoint>, ParseError> parse_mission(std::string_view text);
std::expected<double, ParseError> mission_length_km(std::string_view text); // parse + compute, via and_then/transform
```

Line format: `WP lat lon alt [hold]`. Fields are separated by spaces, `hold` is optional (default 0), and lines starting with `#` and blank lines are ignored. Validation, with these exact error messages:
- not starting with `WP` → `"expected WP"`
- a wrong number of fields → `"expected 3 or 4 values"`
- an unparsable number → `"bad number 'X'"`
- latitude outside [-90, 90] → `"latitude out of range"`; longitude outside [-180, 180] → `"longitude out of range"`
- altitude outside [0, 500] → `"altitude out of range"`
- hold not an integer in [0, 3600] → `"bad hold"`
- a mission with fewer than 2 waypoints → `"need at least 2 waypoints"` (with line 0)

The mission length is the sum of great-circle (haversine) distances between consecutive waypoints, with Earth radius 6371 km, ignoring altitude. `mission_length_km` must be written as a monadic chain on the result of `parse_mission`.

The input contains missions separated by `%%` lines. Print `ok N waypoints, L km` (L with 3 decimals) or `line N: MESSAGE` for each.

## Starter
```cpp
#include <expected>
#include <string>
#include <string_view>
#include <vector>

struct Waypoint { double lat, lon, alt; int hold_s; };
struct ParseError { int line; std::string message; };

std::expected<std::vector<Waypoint>, ParseError> parse_mission(std::string_view text) { return {}; }
std::expected<double, ParseError> mission_length_km(std::string_view text) { return 0.0; }
```

## Driver
```cpp
#include <iostream>
#include <format>
#include <sstream>

void report(const std::string& text) {
    auto wps = parse_mission(text);
    auto len = mission_length_km(text);
    if (wps && len) std::cout << std::format("ok {} waypoints, {:.3f} km\n", wps->size(), *len);
    else if (!wps) std::cout << std::format("line {}: {}\n", wps.error().line, wps.error().message);
    else std::cout << "inconsistent\n";
}

int main() {
    std::string all, line, cur;
    while (std::getline(std::cin, line)) {
        if (line == "%%") { report(cur); cur.clear(); }
        else cur += line + "\n";
    }
    report(cur);
}
```

## Tests
=== sample
# test flight
WP 12.9716 77.5946 100
WP 12.9800 77.6000 120 30
WP 13.0000 77.6100 80
%%
WP 0 0 10
%%
WP 0 0 10
WP 91 0 10
%%
WP 0 0 10
WAY 1 1 10
%%
WP 0 0 10
WP 1 abc 10
%%
WP 0 0 10
WP 1 1
---
ok 3 waypoints, 3.576 km
line 0: need at least 2 waypoints
line 2: latitude out of range
line 2: expected WP
line 2: bad number 'abc'
line 2: expected 3 or 4 values
=== hidden
WP 0 0 0
WP 0 180 500 3600
%%

# blank and comments only

%%
WP 10 10 10
WP 10 10 10 3601
%%
WP 10 10 10
WP 10 10 10 1.5
%%
WP -90 -180 0
WP 90 180 0
%%
WP 1 1 -1
WP 2 2 2
%%
WP 1 1 1 5 extra
WP 2 2 2
%%
WP 1e1 2.5e0 100
WP 10 2.5 100
---
ok 2 waypoints, 20015.087 km
line 0: need at least 2 waypoints
line 2: bad hold
line 2: bad hold
ok 2 waypoints, 20015.087 km
line 1: altitude out of range
line 1: expected 3 or 4 values
ok 2 waypoints, 0.000 km

## Hints
- `std::from_chars(first, last, double&)` with a check that the whole token was consumed gives an exception-free `parse_double`.
- Split each line into `std::string_view` tokens by scanning for spaces. Views into the original text avoid allocation.
- Inside `parse_mission`, on a waypoint error return `std::unexpected(ParseError{line_no, msg})`.
- `mission_length_km` is a one-liner: `return parse_mission(text).transform([](const auto& wps) { ... sum the legs ... });`.
- Haversine: `a = sin²(Δφ/2) + cos φ1 · cos φ2 · sin²(Δλ/2)`, `d = 2R · asin(√a)`, with angles in radians.

## Solution
```cpp
#include <expected>
#include <string>
#include <string_view>
#include <vector>
#include <charconv>
#include <cmath>
#include <numbers>
#include <format>

struct Waypoint { double lat, lon, alt; int hold_s; };
struct ParseError { int line; std::string message; };

std::expected<double, std::string> parse_double(std::string_view s) {
    double v;
    auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || p != s.data() + s.size()) return std::unexpected(std::format("bad number '{}'", s));
    return v;
}

static std::vector<std::string_view> split(std::string_view s) {
    std::vector<std::string_view> out;
    std::size_t i = 0;
    while (i < s.size()) {
        while (i < s.size() && s[i] == ' ') ++i;
        std::size_t j = i;
        while (j < s.size() && s[j] != ' ') ++j;
        if (j > i) out.push_back(s.substr(i, j - i));
        i = j;
    }
    return out;
}

std::expected<Waypoint, std::string> parse_waypoint(std::string_view line) {
    auto f = split(line);
    if (f.empty() || f[0] != "WP") return std::unexpected(std::string("expected WP"));
    if (f.size() != 4 && f.size() != 5) return std::unexpected(std::string("expected 3 or 4 values"));
    Waypoint w{};
    double* targets[] = {&w.lat, &w.lon, &w.alt};
    for (int k = 0; k < 3; ++k) {
        auto v = parse_double(f[k + 1]);
        if (!v) return std::unexpected(v.error());
        *targets[k] = *v;
    }
    if (w.lat < -90 || w.lat > 90) return std::unexpected(std::string("latitude out of range"));
    if (w.lon < -180 || w.lon > 180) return std::unexpected(std::string("longitude out of range"));
    if (w.alt < 0 || w.alt > 500) return std::unexpected(std::string("altitude out of range"));
    if (f.size() == 5) {
        int h;
        auto [p, ec] = std::from_chars(f[4].data(), f[4].data() + f[4].size(), h);
        if (ec != std::errc{} || p != f[4].data() + f[4].size() || h < 0 || h > 3600)
            return std::unexpected(std::string("bad hold"));
        w.hold_s = h;
    }
    return w;
}

std::expected<std::vector<Waypoint>, ParseError> parse_mission(std::string_view text) {
    std::vector<Waypoint> wps;
    int line_no = 0;
    std::size_t pos = 0;
    while (pos < text.size()) {
        std::size_t nl = text.find('\n', pos);
        if (nl == std::string_view::npos) nl = text.size();
        std::string_view line = text.substr(pos, nl - pos);
        pos = nl + 1;
        ++line_no;
        auto first = line.find_first_not_of(' ');
        if (first == std::string_view::npos || line[first] == '#') continue;
        auto wp = parse_waypoint(line);
        if (!wp) return std::unexpected(ParseError{line_no, wp.error()});
        wps.push_back(*wp);
    }
    if (wps.size() < 2) return std::unexpected(ParseError{0, "need at least 2 waypoints"});
    return wps;
}

static double haversine_km(const Waypoint& a, const Waypoint& b) {
    constexpr double R = 6371.0, deg = std::numbers::pi / 180.0;
    double dphi = (b.lat - a.lat) * deg, dlam = (b.lon - a.lon) * deg;
    double h = std::sin(dphi / 2) * std::sin(dphi / 2) +
               std::cos(a.lat * deg) * std::cos(b.lat * deg) * std::sin(dlam / 2) * std::sin(dlam / 2);
    return 2 * R * std::asin(std::sqrt(std::min(1.0, h)));
}

std::expected<double, ParseError> mission_length_km(std::string_view text) {
    return parse_mission(text).transform([](const std::vector<Waypoint>& wps) {
        double total = 0;
        for (std::size_t i = 1; i < wps.size(); ++i) total += haversine_km(wps[i - 1], wps[i]);
        return total;
    });
}
```

- **Errors are values:** every failure travels up as `std::unexpected(...)`, and the function signatures *say* they can fail. There's no hidden control flow, no `try` anywhere, and the code would work unchanged with `-fno-exceptions`, which matters for flight controllers.
- **Composition:** `mission_length_km` reuses the parser and only adds the computation through `.transform`. If parsing failed, the error flows through untouched, carrying its line number.
- **Validation order** follows the statement: structure first (keyword, field count), then syntax (numbers), then semantics (ranges).
- `std::from_chars` is the exception-free, locale-independent number parser that makes this style practical.
