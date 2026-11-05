---
id: cpp-largest-number
title: Largest Number from Concatenation
difficulty: Medium
order: 9
tags: sorting, custom comparator, strings, greedy
time_limit: 1
---
## Statement
Arrange non-negative integers so that their concatenation forms the **largest** possible number, and return it as a string:

```cpp
std::string largest_number(const std::vector<long long>& a);
std::string smallest_number(const std::vector<long long>& a);  // the smallest concatenation (leading zeros allowed, e.g. "0012")
```

`[3, 30, 34, 5, 9]` gives `"9534330"` as the largest and `"3033459"` as the smallest.

Ordering by numeric value or by plain string order is wrong: `"3"` vs `"30"` are equal as prefixes, yet `"330" > "303"`. The right comparator is: **x comes before y if x+y > y+x** (as strings). This rule is transitive, so it is a valid strict weak ordering.

Edge case: if the largest concatenation starts with `0`, every number is zero, so return `"0"`.

**Input:** cases until the end of input: `n` followed by `n` integers in `[0, 10¹⁸]` (n ≤ 10⁵). Print both strings, shortened to their first 30 characters plus the length when longer.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string largest_number(const vector<long long>& a) {
    vector<long long> b = a; sort(b.rbegin(), b.rend());
    string s; for (auto x : b) s += to_string(x); return s;
}
string smallest_number(const vector<long long>& a) {
    vector<long long> b = a; sort(b.begin(), b.end());
    string s; for (auto x : b) s += to_string(x); return s;
}
```

## Driver
```cpp
static string brief(const string& s) { return s.size() <= 30 ? s : s.substr(0, 30) + "...(" + to_string(s.size()) + ")"; }
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<long long> a(n);
        for (auto& x : a) cin >> x;
        cout << brief(largest_number(a)) << ' ' << brief(smallest_number(a)) << '\n';
    }
}
```

## Tests
=== sample
5
3 30 34 5 9
3
0 0 0
---
9534330 3033459
0 000
=== hidden
1
1000000000000000000
4
121 12 1 0
3
824 8247 82
2
10 2
---
1000000000000000000 1000000000000000000
1212110 0112112
828248247 824782482
210 102
=== hidden
1
906
1
413
6
5 6 121 0 1212 0
6
6 4 2 8 1 121
1
12
---
906 906
413 413
65121212100 00121121256
86421211 11212468
12 12
=== hidden
3
140 0 1212
3
301 0 5
1
1
1
8
2
909 0
---
14012120 01212140
53010 03015
1 1
8 8
9090 0909
=== hidden
4
9 584 0 9
4
8 0 0 384
5
259 1212 6 5 0
4
121 1212 1 0
2
4 459
---
995840 058499
838400 003848
6525912120 0121225956
121212110 011211212
4594 4459
=== hidden
@gen 1676827784 big
=== hidden
@gen 1676827785 big
=== hidden
@gen 1676827786 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    for _ in range(5):
        n = r.randint(1, 6); print(n); print(*[r.choice([0, r.randint(0, 9), r.randint(0, 999), r.choice([1, 12, 121, 1212])]) for _ in range(n)])
else:
    n = 100000; print(n); print(*[r.choice([r.randint(0, 99), r.randint(0, 10**18)]) for _ in range(n)])
```

## Hints
- Comparing numerically fails on `[3, 30]`: `"330"` beats `"303"`.
- Compare two candidates by which concatenation is bigger: `x + y` vs `y + x`.
- Handle the all-zeros case: return `"0"`, not `"000"`.

## Solution
**Exchange argument.** In an optimal arrangement, look at any two neighbours `x` and `y`. Swapping them changes only that part of the string, from `x+y` to `y+x`. So in the best order, `x+y ≥ y+x` for every adjacent pair. Sorting with that comparator puts every adjacent pair in the right order at once.

The comparator `x + y > y + x` is a strict weak ordering. Intuitively, it compares the infinite repetitions `xxxx…` and `yyyy…`, which is a total order on strings. So `std::sort` is safe to use with it.

**Edge case:** `[0, 0]` would give `"00"`. If the best string starts with `'0'`, everything is zero, so return `"0"`.

Complexity: O(n log n · L) where L is the number length (at most 19 digits).

```cpp
#include <bits/stdc++.h>
using namespace std;

static vector<string> as_strings(const vector<long long>& a) {
    vector<string> s;
    s.reserve(a.size());
    for (auto x : a) s.push_back(to_string(x));
    return s;
}

string largest_number(const vector<long long>& a) {
    auto s = as_strings(a);
    sort(s.begin(), s.end(), [](const string& x, const string& y) { return x + y > y + x; });
    string out;
    for (auto& t : s) out += t;
    if (!out.empty() && out[0] == '0') return "0";       // all zeros
    return out;
}

string smallest_number(const vector<long long>& a) {
    auto s = as_strings(a);
    sort(s.begin(), s.end(), [](const string& x, const string& y) { return x + y < y + x; });
    string out;
    for (auto& t : s) out += t;
    return out;
}
```
