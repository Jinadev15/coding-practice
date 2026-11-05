---
id: cpp-nested-list-weights
title: Nested List Weight Sums
difficulty: Medium
order: 5
tags: recursion, parsing, recursive descent, nested structures
time_limit: 1
---
## Statement
A nested list is written like `[1,[4,[6]],-2]`. Every element is an integer or another nested list. The **depth** of an integer is how many brackets enclose it: in the example, `1` and `-2` have depth 1, `4` has depth 2, and `6` has depth 3.

Compute two weighted sums:

- **Depth sum:** Σ value × depth. For the example, 1·1 + 4·2 + 6·3 + (−2)·1 = 25.
- **Inverse depth sum:** Σ value × (maxDepth − depth + 1), so the deepest integers get weight 1. For the example (maxDepth = 3), 1·3 + 4·2 + 6·1 + (−2)·3 = 11.

```cpp
std::pair<long long, long long> weights(const std::string& s);   // {depth sum, inverse depth sum}
```

Parse the string **recursively**: a list is `[`, then zero or more elements separated by commas, then `]`. An element is either a number or a list. Empty lists like `[]` and `[[],[]]` are allowed. The input has no spaces, and values fit in `int`.

Nesting can be up to 2000 levels deep, which is fine for recursion. The total length is up to 2·10⁵ characters.

**Input:** one nested list per line. Print `depthSum inverseSum` for each. When the outer list contains no integers at all, maxDepth is 0 and both sums are 0.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<long long, long long> weights(const string& s) {
    return {0, 0};
}
```

## Driver
```cpp
int main() {
    string line;
    while (getline(cin, line)) {
        if (line.empty()) continue;
        auto [a, b] = weights(line);
        cout << a << ' ' << b << '\n';
    }
}
```

## Tests
=== sample
[1,[4,[6]],-2]
[[1,1],2,[1,1]]
[]
---
25 11
10 8
0 0
=== hidden
[[[[[]]]]]
[5]
[[],[[]],[[-7]]]
[0,[0,[0]]]
---
0 0
5 5
-21 -7
0 0
=== hidden
[]
[31]
[[495,-455,[]],436,[-493]]
[370]
[]
---
0 0
31 31
-470 419
370 370
0 0
=== hidden
[-614,-389,[],57]
[-21,642,185]
[408]
[]
[-564,-236,-578,901]
---
-946 -946
806 806
408 408
0 0
-477 -477
=== hidden
[536]
[-140]
[[[],814,736,[[-675,82],259]],781,-494,[]]
[194,[[[643,[],[583,-683,[]]]],[797,602,141]],-293]
[-962,[[],[[37,[]]]],-918]
---
536 536
-140 -140
1792 5723
6593 5311
-1732 -7483
=== hidden
@gen 3417359844 big
=== hidden
@gen 3417359845 big
=== hidden
@gen 3417359846 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
sys.setrecursionlimit(10000)
def make(depth, budget):
    parts = []
    k = r.randint(0, 4 if not big else 40)
    for _ in range(k):
        if budget[0] <= 0: break
        budget[0] -= 1
        if r.random() < 0.3 and depth < (6 if not big else 1500): parts.append(make(depth + 1, budget))
        else: parts.append(str(r.randint(-1000, 1000)))
    return "[" + ",".join(parts) + "]"
lines = []
for _ in range(5 if not big else 2):
    lines.append(make(1, [30 if not big else 20000]))
if big:
    d = 1900; lines.append("[" * d + "7" + "]" * d)
print("\n".join(lines))
```

## Hints
- Write `list(depth)`. Skip `[`, then loop until `]`: if you see `[`, call `list(depth+1)`, otherwise parse a number (it may start with `-`). Skip a comma after each element.
- Keep the cursor index in one shared place (a struct member, or a reference parameter), so the recursive calls advance it.
- For the inverse sum, expand `Σ v·(maxD − d + 1)`. You only need `Σv`, `Σv·d` and `maxD`.

## Solution
**Recursive descent.** `list(depth)` consumes `[`, then repeatedly parses an element (a nested `list(depth + 1)`, or a number at this depth) and skips commas, until it meets `]`. The cursor `i` is shared through the parser object, so every call continues where the previous one stopped.

**One pass for both sums.** The inverse sum seems to need `maxDepth` before you start, but it doesn't. Expand it:

`Σ v·(maxD − d + 1) = (maxD + 1)·Σ v − Σ v·d`

So collect `Σ v`, `Σ v·d` and `maxDepth` during the single parse, then combine them at the end.

Complexity: O(length) time, O(maximum depth) recursion stack.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Parser {
    const string& s; size_t i = 0;
    long long depthSum = 0, plain = 0;   // plain = Σ value
    long long weighted = 0;              // Σ value * depth again, kept for the identity below
    int maxDepth = 0;
    explicit Parser(const string& str) : s(str) {}

    void list(int depth) {               // s[i] == '['
        ++i;
        while (s[i] != ']') {
            if (s[i] == '[') list(depth + 1);
            else number(depth);
            if (s[i] == ',') ++i;
        }
        ++i;                             // skip ']'
    }
    void number(int depth) {
        size_t j = i;
        if (s[j] == '-') ++j;
        while (j < s.size() && isdigit((unsigned char)s[j])) ++j;
        long long v = stoll(s.substr(i, j - i));
        i = j;
        depthSum += v * depth;
        plain += v;
        maxDepth = max(maxDepth, depth);
    }
};

pair<long long, long long> weights(const string& s) {
    Parser p(s);
    p.list(1);
    // Σ v·(maxD − d + 1) = (maxD + 1)·Σ v − Σ v·d   → one pass is enough
    long long inverse = (long long)(p.maxDepth + 1) * p.plain - p.depthSum;
    if (p.maxDepth == 0) inverse = 0;
    return {p.depthSum, inverse};
}
```
