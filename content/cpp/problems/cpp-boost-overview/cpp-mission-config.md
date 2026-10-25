---
id: cpp-mission-config
title: Mission Config Loader with nlohmann/json, fmt and Boost
difficulty: Medium
order: 1
tags: nlohmann/json, fmt, Boost.StringAlgo, parsing, error handling
libs: json, fmt, boost
time_limit: 10
---
## Statement
A robot mission arrives as JSON:

```json
{"name": "dock-survey", "speed": 0.5, "dwell": 2,
 "tags": " Survey, night ,,SURVEY ",
 "waypoints": [{"x": 0, "y": 0}, {"x": 3, "y": 4}, {"x": 3, "y": 10}]}
```

Implement three functions using the real libraries: **nlohmann/json**, **{fmt}** and **Boost.StringAlgo**.

1. `std::vector<std::string> normalize_tags(const std::string& raw)`
   - Split on `,` (use `boost::split`), `boost::trim` and `boost::to_lower` each piece.
   - Drop empty pieces, and remove duplicates while **keeping first-seen order**.
   - For the example: `{"survey", "night"}`.
2. `std::string mission_report(const std::string& text)` returns the two lines below, joined with `\n`:
   - `mission <name>: <n> waypoints, <length:.2f> m, <duration:.1f> s`
   - `tags: [<t1>, <t2>, ...]`

   Definitions:
   - **length** is the sum of the Euclidean distances between consecutive waypoints.
   - **duration** = `length / speed + dwell * n`.
   - `dwell` is optional (default 0). `tags` is optional (default none, shown as `tags: []`).

   Errors, checked **in this order**:
   - Invalid JSON, or a top-level value that is not an object, gives `error: invalid json`.
   - Then, checking `name` (string), `speed` (number) and `waypoints` (array) in that order, the first missing or wrongly typed key gives `error: missing or invalid 'KEY'`.
   - `speed <= 0` gives `error: speed must be positive`.
   - A waypoint without numeric `x` and `y` gives `error: bad waypoint I` (0-based).
3. `std::string report_json(const std::string& text)` returns the compact `dump()` of an object with keys:
   - `name`
   - `waypoints` (count)
   - `length` (rounded to 2 decimals with `std::round(v*100)/100`)
   - `tags` (array)

   nlohmann's default object sorts its keys. For invalid input, return `{"error":"<the message without the 'error: ' prefix>"}`.

## Starter
```cpp
#include <string>
#include <vector>
#include <nlohmann/json.hpp>
#include <fmt/format.h>
#include <boost/algorithm/string.hpp>

std::vector<std::string> normalize_tags(const std::string& raw) {
    std::vector<std::string> out;
    boost::split(out, raw, boost::is_any_of(","));
    return out;
}

std::string mission_report(const std::string& text) {
    auto j = nlohmann::json::parse(text);
    return fmt::format("mission {}", j["name"].get<std::string>());
}

std::string report_json(const std::string& text) { return "{}"; }
```

## Driver
```cpp
#include <cmath>
#include <iostream>

static std::string show(const std::vector<std::string>& v) {
    std::string s = "[";
    for (size_t i = 0; i < v.size(); ++i) s += (i ? "|" : "") + v[i];
    return s + "]";
}

int main() {
    const std::string base = R"({"name": "dock-survey", "speed": 0.5, "dwell": 2,
        "tags": " Survey, night ,,SURVEY ",
        "waypoints": [{"x": 0, "y": 0}, {"x": 3, "y": 4}, {"x": 3, "y": 10}]})";
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "tags") {
            std::cout << show(normalize_tags(" Survey, night ,,SURVEY ")) << "\n"
                      << show(normalize_tags("")) << "\n"
                      << show(normalize_tags(" , ,")) << "\n"
                      << show(normalize_tags("B,a,b,A,c ,  C")) << "\n";
        } else if (cmd == "report") {
            std::cout << mission_report(base) << "\n";
            std::cout << mission_report(R"({"name":"hop","speed":2,"waypoints":[{"x":1.5,"y":-2}]})") << "\n";
        } else if (cmd == "errors") {
            for (const char* t : {R"({"name": "x", )", R"([1,2])", R"({"speed":1,"waypoints":[]})",
                                  R"({"name":"a","speed":"fast","waypoints":[]})", R"({"name":"a","speed":1})",
                                  R"({"name":"a","speed":0,"waypoints":[]})",
                                  R"({"name":"a","speed":1,"waypoints":[{"x":0,"y":0},{"x":1}]})",
                                  R"({"name":"a","speed":1,"waypoints":[{"x":0,"y":0},{"x":1,"y":"2"}]})"})
                std::cout << mission_report(t) << "\n";
        } else if (cmd == "json") {
            std::cout << report_json(base) << "\n"
                      << report_json(R"({"name":"a","speed":-1,"waypoints":[]})") << "\n"
                      << report_json("not json") << "\n";
        } else if (cmd == "big") {
            int n; std::cin >> n;
            nlohmann::json m = {{"name", "spiral"}, {"speed", 1.25}, {"dwell", 0.5}, {"tags", "Lidar,lidar, MAP,map ,Night"}};
            auto& w = m["waypoints"] = nlohmann::json::array();
            for (int i = 0; i < n; ++i) {
                double a = i * 0.01, r = 0.001 * i;
                w.push_back({{"x", r * std::cos(a)}, {"y", r * std::sin(a)}});
            }
            std::string text = m.dump();
            std::cout << mission_report(text) << "\n" << report_json(text).substr(0, 60) << "\n";
        }
    }
}
```

## Tests
=== sample
tags
report
---
[survey|night]
[]
[]
[b|a|c]
mission dock-survey: 3 waypoints, 11.00 m, 28.0 s
tags: [survey, night]
mission hop: 1 waypoints, 0.00 m, 0.0 s
tags: []
=== hidden
errors
---
error: invalid json
error: invalid json
error: missing or invalid 'name'
error: missing or invalid 'speed'
error: missing or invalid 'waypoints'
error: speed must be positive
error: bad waypoint 1
error: bad waypoint 1
=== hidden
json
---
{"length":11.0,"name":"dock-survey","tags":["survey","night"],"waypoints":3}
{"error":"speed must be positive"}
{"error":"invalid json"}
=== hidden
big 200000
---
mission spiral: 200000 waypoints, 199997.61 m, 259998.1 s
tags: [lidar, map, night]
{"length":199997.61,"name":"spiral","tags":["lidar","map","n

## Hints
- `boost::split(parts, raw, boost::is_any_of(","))`, then `boost::trim(p); boost::to_lower(p);` on each piece. Track seen tags in a `std::unordered_set`.
- `nlohmann::json::parse(text, nullptr, false)` returns a *discarded* value instead of throwing: test it with `j.is_discarded()`.
- Type checks: `j.is_object()`, `j.contains("speed")`, `j["speed"].is_number()`. Use `j.value("dwell", 0.0)` for the optional key.
- `fmt::format("{:.2f}", x)`, and `fmt::join(tags, ", ")` from `<fmt/ranges.h>`.
- Share one `parse_mission` helper that returns either a struct or an error string, so both reports use the same validation.

## Solution
```cpp
#include <cmath>
#include <optional>
#include <string>
#include <unordered_set>
#include <variant>
#include <vector>
#include <nlohmann/json.hpp>
#include <fmt/format.h>
#include <fmt/ranges.h>
#include <boost/algorithm/string.hpp>

std::vector<std::string> normalize_tags(const std::string& raw) {
    std::vector<std::string> parts, out;
    boost::split(parts, raw, boost::is_any_of(","));
    std::unordered_set<std::string> seen;
    for (auto& p : parts) {
        boost::trim(p);
        boost::to_lower(p);
        if (!p.empty() && seen.insert(p).second) out.push_back(p);
    }
    return out;
}

struct Mission {
    std::string name;
    std::size_t count = 0;
    double length = 0, duration = 0;
    std::vector<std::string> tags;
};

static std::variant<Mission, std::string> parse_mission(const std::string& text) {
    using nlohmann::json;
    json j = json::parse(text, nullptr, /*allow_exceptions=*/false);
    if (j.is_discarded() || !j.is_object()) return std::string("invalid json");
    if (!j.contains("name") || !j["name"].is_string()) return std::string("missing or invalid 'name'");
    if (!j.contains("speed") || !j["speed"].is_number()) return std::string("missing or invalid 'speed'");
    if (!j.contains("waypoints") || !j["waypoints"].is_array()) return std::string("missing or invalid 'waypoints'");
    const double speed = j["speed"].get<double>();
    if (speed <= 0) return std::string("speed must be positive");
    Mission m;
    m.name = j["name"].get<std::string>();
    const auto& w = j["waypoints"];
    double px = 0, py = 0;
    for (std::size_t i = 0; i < w.size(); ++i) {
        const auto& p = w[i];
        if (!p.is_object() || !p.contains("x") || !p.contains("y") || !p["x"].is_number() || !p["y"].is_number())
            return fmt::format("bad waypoint {}", i);
        const double x = p["x"].get<double>(), y = p["y"].get<double>();
        if (i) m.length += std::hypot(x - px, y - py);
        px = x; py = y;
    }
    m.count = w.size();
    m.duration = m.length / speed + j.value("dwell", 0.0) * static_cast<double>(m.count);
    if (j.contains("tags") && j["tags"].is_string()) m.tags = normalize_tags(j["tags"].get<std::string>());
    return m;
}

std::string mission_report(const std::string& text) {
    auto r = parse_mission(text);
    if (auto* e = std::get_if<std::string>(&r)) return "error: " + *e;
    const auto& m = std::get<Mission>(r);
    return fmt::format("mission {}: {} waypoints, {:.2f} m, {:.1f} s\ntags: [{}]",
                       m.name, m.count, m.length, m.duration, fmt::join(m.tags, ", "));
}

std::string report_json(const std::string& text) {
    auto r = parse_mission(text);
    if (auto* e = std::get_if<std::string>(&r)) return nlohmann::json{{"error", *e}}.dump();
    const auto& m = std::get<Mission>(r);
    nlohmann::json out = {{"name", m.name}, {"waypoints", m.count},
                          {"length", std::round(m.length * 100) / 100}, {"tags", m.tags}};
    return out.dump();
}
```

- `parse(text, nullptr, false)` turns malformed input into a **discarded** value instead of an exception. That suits a validation path where bad input is expected.
- **One parser, two views**: `std::variant<Mission, std::string>` carries either the result or the error, so the text and JSON reports can never disagree about what's valid.
- **`fmt::join`** formats ranges without building intermediate strings. `{:.2f}` follows the same rules as `std::format`, which was standardized from {fmt}.
- **Boost.StringAlgo** covers what `std::string` still lacks: `trim`, `to_lower` and `split` on a character set.
