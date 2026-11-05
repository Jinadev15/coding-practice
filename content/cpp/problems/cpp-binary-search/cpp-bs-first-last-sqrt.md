---
id: cpp-bs-first-last-sqrt
title: First and Last Position, and Integer Square Root
difficulty: Easy
order: 2
tags: binary search, boundaries, overflow
time_limit: 1
---
## Statement
```cpp
std::pair<int,int> first_last(const std::vector<int>& a, int x);   // first and last index of x in sorted a, or {-1,-1}
long long isqrt(long long n);                                      // floor(sqrt(n)) for 0 <= n <= 9.2e18, no floating point
int search_insert(const std::vector<int>& a, int x);               // index of x if present, otherwise where it would be inserted
```

- `first_last` uses two boundary searches: the first index `≥ x`, and the first index `> x`, minus one.
- `isqrt` is binary search on the **answer**: find the last `m` with `m·m ≤ n`. Beware: `m·m` overflows for `m` near 3.04·10⁹ unless you compare `m ≤ n / m` instead.

**Input:** cases until the end of input: `fl n x` + values, `sqrt n`, or `ins n x` + values.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> first_last(const vector<int>& a, int x) {
    for (size_t i = 0; i < a.size(); ++i) if (a[i] == x) return {(int)i, (int)i};
    return {-1, -1};
}
long long isqrt(long long n) { return (long long)sqrt((double)n); }   // double rounding is wrong for big n
int search_insert(const vector<int>& a, int x) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "sqrt") { long long n; cin >> n; cout << isqrt(n) << '\n'; continue; }
        int n, x; cin >> n >> x;
        vector<int> a(n); for (auto& v : a) cin >> v;
        if (cmd == "fl") { auto [f, l] = first_last(a, x); cout << f << ' ' << l << '\n'; }
        else cout << search_insert(a, x) << '\n';
    }
}
```

## Tests
=== sample
fl 6 8
5 7 7 8 8 10
fl 6 6
5 7 7 8 8 10
sqrt 8
sqrt 16
ins 4 5
1 3 5 6
ins 4 2
1 3 5 6
---
3 4
-1 -1
2
4
2
1
=== hidden
fl 0 1
fl 1 2147483647
2147483647
sqrt 0
sqrt 1
sqrt 9223372036854775807
sqrt 9223372030926249001
sqrt 9223372030926249000
ins 0 5
ins 3 9
1 3 5
---
-1 -1
0 0
0
1
3037000499
3037000499
3037000498
0
3
=== hidden
sqrt 4678367220231662736
ins 7 3
1 2 2 4 4 4 5
ins 8 3
1 1 2 2 3 5 6 6
sqrt 8936769306755736576
sqrt 25
sqrt 4237459655315463951
sqrt 60
ins 7 0
0 0 1 1 3 3 6
sqrt 1458239655697187364
sqrt 18
ins 1 7
1
ins 1 6
5
ins 0 -1

ins 2 -1
3 6
ins 4 -1
1 1 4 5
---
2162953356
3
4
2989442976
5
2058509085
7
0
1207575942
4
1
1
0
0
0
=== hidden
sqrt 5858235621856151362
sqrt 4918127624122188025
ins 6 5
0 3 4 5 5 6
ins 4 2
1 2 4 4
fl 1 6
1
fl 2 3
1 5
sqrt 29
fl 3 7
0 1 3
ins 7 7
1 1 1 1 3 4 6
ins 5 5
0 2 2 3 4
fl 4 2
0 3 3 4
ins 6 6
2 2 3 3 4 5
ins 6 2
0 0 1 3 4 5
fl 5 0
0 1 1 1 4
sqrt 3404523459756336240
---
2420379231
2217685195
3
1
-1 -1
-1 -1
5
-1 -1
7
5
-1 -1
6
3
0 0
1845135078
=== hidden
fl 8 -1
1 2 2 3 3 3 3 6
fl 0 7

fl 6 7
2 2 3 4 5 5
ins 6 1
0 2 2 3 3 6
fl 2 0
2 4
sqrt 51
ins 3 2
1 3 3
ins 2 7
1 5
fl 6 -1
0 0 1 3 4 6
fl 7 -1
1 3 3 3 3 4 4
sqrt 21
fl 3 1
0 1 1
ins 4 2
0 2 4 5
ins 3 1
3 4 4
sqrt 51
---
-1 -1
-1 -1
-1 -1
1
-1 -1
7
1
2
-1 -1
-1 -1
4
1 2
1
0
7
=== hidden
@gen 2719972479 big
=== hidden
@gen 2719972480 big
=== hidden
@gen 2719972481 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = []
for _ in range(15 if not big else 3):
    c = r.choice(["fl", "sqrt", "ins"])
    if c == "sqrt":
        out.append(f"sqrt {r.choice([r.randint(0, 100), r.randint(0, 2**63 - 1), r.randint(1, 3037000499)**2 + r.randint(-1, 1)])}")
    else:
        n = r.randint(0, 8) if not big else 1000000
        a = sorted(r.randint(0, 6) if not big else r.randint(0, 10**9) for _ in range(n))
        out.append(f"{c} {n} {r.randint(-1, 7) if not big else r.randint(0, 10**9)}"); out.append(" ".join(map(str, a)))
print("\n".join(out))
```

## Hints
- First occurrence = first index with `a[i] ≥ x`. Last occurrence = (first index with `a[i] ≥ x+1`) − 1.
- isqrt: search for the largest `m` with `m·m ≤ n`. Write the test as `m <= n / m` to avoid overflow.
- When the update is `lo = mid`, compute `mid` rounding up (`lo + (hi − lo + 1)/2`), or the loop can get stuck.

## Solution
**Boundaries.** The first occurrence is `lower_bound(x)`. The last occurrence is one before `lower_bound(x + 1)`, which is `upper_bound(x)` for integers. Use `long long` for `x + 1`, so that `x = INT_MAX` doesn't overflow. The insert position *is* `lower_bound`.

**Integer square root.** "The last `m` with `m² ≤ n`" is binary search on the answer, using the mirrored template: when the search moves `lo = mid`, `mid` must round **up**, or `lo = hi − 1` would loop forever. Comparing `mid ≤ n / mid` instead of `mid·mid ≤ n` avoids overflow (for `mid ≥ 1` they are equivalent with integer division).

The floating-point `sqrt` in the starter fails near perfect squares above 2⁵³: a double can't represent every integer there.

Complexity: O(log n) each.

```cpp
#include <bits/stdc++.h>
using namespace std;

static int first_at_least(const vector<int>& a, long long x) {
    int lo = 0, hi = a.size();
    while (lo < hi) { int mid = lo + (hi - lo) / 2; if (a[mid] >= x) hi = mid; else lo = mid + 1; }
    return lo;
}

pair<int,int> first_last(const vector<int>& a, int x) {
    int f = first_at_least(a, x);
    if (f == (int)a.size() || a[f] != x) return {-1, -1};
    int l = first_at_least(a, (long long)x + 1) - 1;     // last index with a[i] <= x
    return {f, l};
}

long long isqrt(long long n) {
    long long lo = 0, hi = 3037000500LL;                 // sqrt(2^63) < 3037000500
    while (lo < hi) {                                    // last m with m*m <= n  ==  (first m with m*m > n) - 1
        long long mid = lo + (hi - lo + 1) / 2;          // round UP: we move lo = mid
        if (mid <= n / mid) lo = mid; else hi = mid - 1; // mid*mid <= n, written without overflow
    }
    return lo;
}

int search_insert(const vector<int>& a, int x) { return first_at_least(a, x); }
```
