---
id: cpp-time-of-day
title: TimeOfDay Constructors
difficulty: Medium
order: 1
tags: constructors, delegating constructors, explicit, exceptions
---
## Statement
Implement a value class `TimeOfDay` (a time within one day, with one-second resolution) with this set of constructors:

```cpp
class TimeOfDay {
public:
    TimeOfDay();                                   // 00:00:00
    TimeOfDay(int h, int m, int s);                // validates 0<=h<24, 0<=m<60, 0<=s<60
    explicit TimeOfDay(int seconds_since_midnight);   // validates 0..86399
    explicit TimeOfDay(const std::string& hhmmss);    // exactly "HH:MM:SS" (8 chars, digits), then validated
    int seconds() const;                           // seconds since midnight
    std::string str() const;                       // "HH:MM:SS" zero-padded
    TimeOfDay plus(int secs) const;                // wraps around midnight; secs may be negative
};
```

Every invalid input must throw `std::invalid_argument`. Use **delegating constructors** so the validation logic exists in only one place. The two single-argument constructors must be `explicit`: the driver checks this at compile time.

Each input line is one of `def`, `hms H M S`, `sec N` or `str TEXT`, followed by an integer `K`. For each valid time the driver prints `str() seconds() plus(K).str()`; for an invalid one it prints `invalid`.

## Starter
```cpp
#include <string>
#include <stdexcept>

class TimeOfDay {
public:
    TimeOfDay() {}
    TimeOfDay(int h, int m, int s) {}
    explicit TimeOfDay(int seconds_since_midnight) {}
    explicit TimeOfDay(const std::string& hhmmss) {}
    int seconds() const { return 0; }
    std::string str() const { return "00:00:00"; }
    TimeOfDay plus(int secs) const { return *this; }
};
```

## Driver
```cpp
#include <iostream>
#include <type_traits>

static_assert(!std::is_convertible_v<int, TimeOfDay>, "TimeOfDay(int) must be explicit");
static_assert(!std::is_convertible_v<std::string, TimeOfDay>, "TimeOfDay(string) must be explicit");
static_assert(std::is_default_constructible_v<TimeOfDay>);

int main() {
    std::string kind;
    while (std::cin >> kind) {
        try {
            TimeOfDay t;
            if (kind == "hms") { int h, m, s; std::cin >> h >> m >> s; t = TimeOfDay(h, m, s); }
            else if (kind == "sec") { int n; std::cin >> n; t = TimeOfDay(n); }
            else if (kind == "str") { std::string x; std::cin >> x; t = TimeOfDay(x); }
            int k; std::cin >> k;
            std::cout << t.str() << ' ' << t.seconds() << ' ' << t.plus(k).str() << '\n';
        } catch (const std::invalid_argument&) {
            int k; std::cin >> k;
            std::cout << "invalid\n";
        }
    }
}
```

## Tests
=== sample
def 61
hms 13 5 9 3600
sec 86399 1
str 07:30:00 -27000
hms 24 0 0 5
str 7:30:00 0
---
00:00:00 0 00:01:01
13:05:09 47109 14:05:09
23:59:59 86399 00:00:00
07:30:00 27000 00:00:00
invalid
invalid
=== hidden
sec -1 0
sec 86400 0
hms 0 60 0 0
hms 0 0 60 0
hms -1 0 0 0
hms 23 59 59 86400
str 23:59:59 -86401
str 12:3a:00 0
str 12:30:000 0
str 12-30-00 0
str 99:00:00 0
str 00:00:00 1000000007
sec 0 -1
def -86399
---
invalid
invalid
invalid
invalid
invalid
23:59:59 86399 23:59:59
23:59:59 86399 23:59:58
invalid
invalid
invalid
invalid
00:00:00 0 01:46:47
00:00:00 0 23:59:59
00:00:00 0 00:00:01

## Hints
- Make `TimeOfDay(int seconds)` the "primary" constructor that validates and stores, and have `TimeOfDay(h, m, s)` delegate to it after checking the component ranges.
- The string constructor can delegate to the `(h, m, s)` one via a static helper that parses and throws on a bad format.
- Wrapping with negative numbers: `((x % 86400) + 86400) % 86400`. Use `long long` for the intermediate value, since `secs` can be large.

## Solution
```cpp
#include <string>
#include <stdexcept>
#include <cctype>
#include <cstdio>

class TimeOfDay {
public:
    TimeOfDay() : TimeOfDay(0) {}
    TimeOfDay(int h, int m, int s) : TimeOfDay(checked(h, m, s)) {}
    explicit TimeOfDay(int seconds_since_midnight) : secs_(seconds_since_midnight) {
        if (secs_ < 0 || secs_ >= 86400) throw std::invalid_argument("seconds out of range");
    }
    explicit TimeOfDay(const std::string& t) : TimeOfDay(parse(t)) {}

    int seconds() const { return secs_; }
    std::string str() const {
        char buf[9];
        std::snprintf(buf, sizeof buf, "%02d:%02d:%02d", secs_ / 3600, secs_ / 60 % 60, secs_ % 60);
        return buf;
    }
    TimeOfDay plus(int secs) const {
        long long x = (static_cast<long long>(secs_) + secs) % 86400;
        return TimeOfDay(static_cast<int>((x + 86400) % 86400));
    }

private:
    static int checked(int h, int m, int s) {
        if (h < 0 || h >= 24 || m < 0 || m >= 60 || s < 0 || s >= 60)
            throw std::invalid_argument("component out of range");
        return h * 3600 + m * 60 + s;
    }
    static int parse(const std::string& t) {
        if (t.size() != 8 || t[2] != ':' || t[5] != ':') throw std::invalid_argument("format");
        for (int i : {0, 1, 3, 4, 6, 7})
            if (!std::isdigit(static_cast<unsigned char>(t[i]))) throw std::invalid_argument("format");
        auto two = [&](int i) { return (t[i] - '0') * 10 + (t[i + 1] - '0'); };
        return checked(two(0), two(3), two(6));
    }
    int secs_;
};
```

All validation of the final value lives in one constructor, `TimeOfDay(int)`, and every other constructor delegates to it. The static helpers `checked` and `parse` run *before* delegation (in the initialiser list), so they can't touch members, which is why they're `static`. Marking the single-argument constructors `explicit` stops `TimeOfDay t = 5;` or passing `"12:00:00"` where a `TimeOfDay` is expected from compiling silently.
