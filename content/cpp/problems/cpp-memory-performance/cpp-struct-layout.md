---
id: cpp-struct-layout
title: Struct Layout and Padding Analyzer
difficulty: Medium
order: 1
tags: alignment, padding, sizeof, offsetof, data layout
---
## Statement
Write the tool every performance engineer wants (a mini `pahole`): given struct definitions, compute the exact layout a compiler produces on x86-64 Linux (System V ABI), show every padding hole, and find the **best member order**.

Input lines:

```
struct NAME
TYPE member            (one member per line)
TYPE member[N]         (array of N, N >= 1)
alignas(K) TYPE member (K a power of two; the alignment becomes max(K, natural))
end
layout NAME
```

| Type | size / alignment |
|---|---|
| `bool`, `char`, `int8` | 1 / 1 |
| `short`, `int16` | 2 / 2 |
| `int`, `int32`, `float` | 4 / 4 |
| `long`, `int64`, `double`, `ptr` | 8 / 8 |
| a previously defined struct | its size / alignment |

The layout rules:
- Each member goes at the next offset that's a multiple of its alignment.
- The struct's alignment is the maximum member alignment, and its size is rounded up to a multiple of it.
- An empty struct has size 1 and alignment 1.
- An array has the element's alignment and N × the element size.

If a member's type is unknown, discard the struct and print `error: unknown type T in NAME` at its `end` line. `layout` of an undefined struct prints `error: no struct NAME`.

`layout NAME` prints:

```
layout NAME: size S, align A, padding P
  OFF: TYPE member (SIZE)          one line per member; arrays print as TYPE member[N]
  OFF: [K padding]                 for each hole, including tail padding
  best: m1 m2 ... -> size S2 (saves X)
```

The best order sorts the members by **decreasing alignment**, keeping declaration order for equal alignments. That's the standard heuristic. When every member's size is a multiple of its alignment (true for all plain types), it leaves no interior padding.

## Starter
```cpp
#include <iostream>
#include <string>

int main() {
    std::string line;
    while (std::getline(std::cin, line)) {
        // TODO
    }
}
```

## Tests
=== sample
struct Bad
char tag
double value
char flag
end
layout Bad
struct Pose
float x
float y
float theta
end
layout Pose
---
layout Bad: size 24, align 8, padding 14
  0: char tag (1)
  1: [7 padding]
  8: double value (8)
  16: char flag (1)
  17: [7 padding]
  best: value tag flag -> size 16 (saves 8)
layout Pose: size 12, align 4, padding 0
  0: float x (4)
  4: float y (4)
  8: float theta (4)
  best: x y theta -> size 12 (saves 0)
=== hidden
struct Empty
end
layout Empty
struct Inner
short a
char b
end
layout Inner
struct Outer
char c
Inner in
int x
Inner arr[3]
bool done
end
layout Outer
struct Cache
alignas(64) long counter
char tag
end
layout Cache
struct Mixed
char a
int64 b
short c[3]
alignas(16) int d
ptr p
bool e
float f
end
layout Mixed
struct Broken
int ok
quaternion q
end
layout Broken
layout Nope
struct Nested
Cache c
char x
end
layout Nested
---
layout Empty: size 1, align 1, padding 1
  best: -> size 1 (saves 0)
layout Inner: size 4, align 2, padding 1
  0: short a (2)
  2: char b (1)
  3: [1 padding]
  best: a b -> size 4 (saves 0)
layout Outer: size 28, align 4, padding 6
  0: char c (1)
  1: [1 padding]
  2: Inner in (4)
  6: [2 padding]
  8: int x (4)
  12: Inner arr[3] (12)
  24: bool done (1)
  25: [3 padding]
  best: x in arr c done -> size 24 (saves 4)
layout Cache: size 64, align 64, padding 55
  0: long counter (8)
  8: char tag (1)
  9: [55 padding]
  best: counter tag -> size 64 (saves 0)
layout Mixed: size 64, align 16, padding 32
  0: char a (1)
  1: [7 padding]
  8: int64 b (8)
  16: short c[3] (6)
  22: [10 padding]
  32: int d (4)
  36: [4 padding]
  40: ptr p (8)
  48: bool e (1)
  49: [3 padding]
  52: float f (4)
  56: [8 padding]
  best: d b p f c a e -> size 48 (saves 16)
error: unknown type quaternion in Broken
error: no struct Broken
error: no struct Nope
layout Nested: size 128, align 64, padding 63
  0: Cache c (64)
  64: char x (1)
  65: [63 padding]
  best: c x -> size 128 (saves 0)

## Hints
- Round up: `(off + a - 1) / a * a`.
- Keep a map from name to `{size, align}`. A struct type used as a member is just another entry.
- Compute the layout as a function of a member list, then call it twice: once in declaration order and once on a `std::stable_sort` copy ordered by decreasing alignment.
- Padding = struct size − the sum of the member sizes.

## Solution
```cpp
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <algorithm>

struct Member { std::string type, name; long count; long size, align; };
struct Info { long size, align; std::vector<Member> members; };

static std::map<std::string, std::pair<long, long>> types = {
    {"bool", {1, 1}}, {"char", {1, 1}}, {"int8", {1, 1}}, {"short", {2, 2}}, {"int16", {2, 2}},
    {"int", {4, 4}}, {"int32", {4, 4}}, {"float", {4, 4}},
    {"long", {8, 8}}, {"int64", {8, 8}}, {"double", {8, 8}}, {"ptr", {8, 8}},
};
static std::map<std::string, Info> structs;

static long round_up(long x, long a) { return (x + a - 1) / a * a; }

// offsets for members in the given order; returns {size, align}
static std::pair<long, long> compute(const std::vector<Member>& ms, std::vector<long>* offs) {
    long off = 0, align = 1;
    for (const auto& m : ms) {
        off = round_up(off, m.align);
        if (offs) offs->push_back(off);
        off += m.size;
        align = std::max(align, m.align);
    }
    if (ms.empty()) return {1, 1};
    return {round_up(off, align), align};
}

int main() {
    std::string line, cur, bad_type;
    std::vector<Member> ms;
    bool in_struct = false;
    while (std::getline(std::cin, line)) {
        std::istringstream ss(line);
        std::string w;
        if (!(ss >> w)) continue;
        if (w == "struct") {
            ss >> cur; ms.clear(); bad_type.clear(); in_struct = true;
        } else if (w == "end") {
            in_struct = false;
            if (!bad_type.empty()) { std::cout << "error: unknown type " << bad_type << " in " << cur << "\n"; continue; }
            auto [size, align] = compute(ms, nullptr);
            structs[cur] = {size, align, ms};
            types[cur] = {size, align};
        } else if (w == "layout") {
            std::string name; ss >> name;
            auto it = structs.find(name);
            if (it == structs.end()) { std::cout << "error: no struct " << name << "\n"; continue; }
            const Info& info = it->second;
            std::vector<long> offs;
            compute(info.members, &offs);
            long used = 0;
            for (auto& m : info.members) used += m.size;
            std::cout << "layout " << name << ": size " << info.size << ", align " << info.align
                      << ", padding " << info.size - used << "\n";
            long end = 0;
            for (size_t i = 0; i < info.members.size(); ++i) {
                const auto& m = info.members[i];
                if (offs[i] > end) std::cout << "  " << end << ": [" << offs[i] - end << " padding]\n";
                std::cout << "  " << offs[i] << ": " << m.type << " " << m.name;
                if (m.count > 1 || m.count == -1) std::cout << "[" << (m.count == -1 ? 1 : m.count) << "]";
                std::cout << " (" << m.size << ")\n";
                end = offs[i] + m.size;
            }
            if (!info.members.empty() && info.size > end)
                std::cout << "  " << end << ": [" << info.size - end << " padding]\n";
            auto best = info.members;
            std::stable_sort(best.begin(), best.end(), [](const Member& a, const Member& b) { return a.align > b.align; });
            auto [bsize, balign] = compute(best, nullptr);
            std::cout << "  best:";
            for (auto& m : best) std::cout << " " << m.name;
            std::cout << " -> size " << bsize << " (saves " << info.size - bsize << ")\n";
        } else if (in_struct) {
            long forced = 1;
            std::string type = w, name;
            if (w.rfind("alignas(", 0) == 0) {
                forced = std::stol(w.substr(8, w.size() - 9));
                ss >> type;
            }
            ss >> name;
            long count = 1; bool array = false;
            if (auto b = name.find('['); b != std::string::npos) {
                count = std::stol(name.substr(b + 1, name.size() - b - 2));
                name = name.substr(0, b);
                array = true;
            }
            auto t = types.find(type);
            if (t == types.end()) { if (bad_type.empty()) bad_type = type; continue; }
            ms.push_back({type, name, array ? (count == 1 ? -1 : count) : 1,
                          t->second.first * count, std::max(t->second.second, forced)});
        }
    }
}
```

Every compiler implements the same three rules: align each member, take the struct's alignment from its strictest member, and pad the size to a multiple of that alignment so array elements stay aligned. The tool makes the consequences visible:
- `Bad` wastes 14 of its 24 bytes; reordered, it needs 16.
- `alignas(64)` (used against false sharing) inflates a struct to a full cache line.
- Nesting propagates alignment: `Nested` contains a `Cache`, so it's 64-aligned and 128 bytes even though it adds only one `char`.

In real code, check layouts with `static_assert(sizeof(T) == …)` and `offsetof`, `pahole` on the compiled binary, or `-Wpadded`. Sorting members by decreasing alignment is the standard fix, but keep fields that are accessed together on the same cache line, which sometimes matters more than the bytes saved.
