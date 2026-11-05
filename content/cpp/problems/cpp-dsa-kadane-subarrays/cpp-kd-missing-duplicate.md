---
id: cpp-kd-missing-duplicate
title: Missing and Duplicate Numbers In Place
difficulty: Medium
order: 5
tags: cyclic sort, sign marking, index as hash, O(1) space
time_limit: 2
---
## Statement
An array of length `n` should contain each of `1..n` exactly once. Instead, some values are **missing** and some are **duplicated**: every value lies in `1..n`, but there can be several missing values.

```cpp
std::vector<int> find_missing(std::vector<int> a);       // all missing values, increasing
std::vector<int> find_duplicates(std::vector<int> a);    // all values that appear more than once, increasing
```

Use only O(1) extra memory besides the output (you may modify your copy of `a`). The index range `0..n−1` matches the value range `1..n`, so **the array can be its own hash table**:

- **Cyclic sort:** swap each value `v` into slot `v−1`. Afterwards, a slot `i` with `a[i] != i+1` means `i+1` is missing and `a[i]` is a duplicate.
- **Or sign marking:** negate `a[|v|−1]` to mark "seen v".

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> find_missing(vector<int> a) { return {}; }
vector<int> find_duplicates(vector<int> a) { return {}; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        auto m = find_missing(a), d = find_duplicates(a);
        long long hm = 0, hd = 0;
        for (int x : m) hm = (hm * 1000003 + x) % 998244353;
        for (int x : d) hd = (hd * 1000003 + x) % 998244353;
        cout << m.size() << " missing:";
        for (size_t i = 0; i < min<size_t>(m.size(), 10); ++i) cout << ' ' << m[i];
        cout << " (" << hm << ") | " << d.size() << " dup:";
        for (size_t i = 0; i < min<size_t>(d.size(), 10); ++i) cout << ' ' << d[i];
        cout << " (" << hd << ")\n";
    }
}
```

## Tests
=== sample
8
4 3 2 7 8 2 3 1
4
1 3 3 2
---
2 missing: 5 6 (5000021) | 2 dup: 2 3 (2000009)
1 missing: 4 (4) | 1 dup: 3 (3)
=== hidden
1
1
2
2 2
5
1 2 3 4 5
6
6 6 6 6 6 6
---
0 missing: (0) | 0 dup: (0)
1 missing: 1 (1) | 1 dup: 2 (2)
0 missing: (0) | 0 dup: (0)
5 missing: 1 2 3 4 5 (408082135) | 1 dup: 6 (6)
=== hidden
9
1 8 5 3 7 9 2 4 6
1
1
8
2 3 1 4 4 6 6 3
1
1
7
6 5 7 6 4 1 3
9
6 8 5 6 2 9 4 1 3
---
0 missing: (0) | 0 dup: (0)
0 missing: (0) | 0 dup: (0)
3 missing: 5 7 8 (829280250) | 3 dup: 3 4 6 (297719280)
0 missing: (0) | 0 dup: (0)
1 missing: 2 (2) | 1 dup: 6 (6)
1 missing: 7 (7) | 1 dup: 6 (6)
=== hidden
3
1 3 2
5
1 1 2 4 4
1
1
6
2 6 3 3 2 2
10
9 9 9 9 10 7 8 6 2 3
8
8 4 5 1 7 6 3 6
---
0 missing: (0) | 0 dup: (0)
2 missing: 3 5 (3000014) | 2 dup: 1 4 (1000007)
0 missing: (0) | 0 dup: (0)
3 missing: 1 4 5 (767402673) | 2 dup: 2 3 (2000009)
3 missing: 1 4 5 (767402673) | 1 dup: 9 (9)
1 missing: 2 (2) | 1 dup: 6 (6)
=== hidden
8
5 1 6 6 3 1 3 2
3
1 3 1
5
5 3 4 1 2
4
3 1 3 4
1
1
3
1 2 1
---
3 missing: 4 7 8 (65877594) | 3 dup: 1 3 6 (766402671)
1 missing: 2 (2) | 1 dup: 1 (1)
0 missing: (0) | 0 dup: (0)
1 missing: 2 (2) | 1 dup: 3 (3)
0 missing: (0) | 0 dup: (0)
1 missing: 3 (3) | 1 dup: 1 (1)
=== hidden
@gen 1306117850 big
=== hidden
@gen 1306117851 big
=== hidden
@gen 1306117852 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else 1000000
    if r.random() < 0.5:
        a = list(range(1, n + 1)); r.shuffle(a)
        for _ in range(r.randint(0, 3 if not big else 1000)): a[r.randrange(n)] = r.randint(1, n)
    else:
        a = [r.randint(1, n) for _ in range(n)]
    print(n); print(*a)
```

## Hints
- Values 1..n match indices 0..n−1: value v "belongs" at index v−1.
- Cyclic sort: while `a[i]` isn't in its slot and its slot doesn't already hold the same value, swap it there.
- To count occurrences in place, add n+1 to slot v−1 for each v. Then `slot % (n+1)` is the original value and `slot / (n+1)` is the count.

## Solution
**Cyclic sort.** Each swap puts one value into its own slot permanently, so there are at most `n` swaps in total, despite the inner "keep swapping at `i`" behaviour. When the target slot already holds the same value, the current value is a duplicate, so leave it and move on.

After sorting, every value that is present sits in its slot. The slots that don't hold their own index (+1) mark missing numbers, and their contents are the extra copies.

**Counting in place (for duplicates).** To count occurrences without extra memory, add `n+1` to slot `v−1` for each `v`. The original value is still recoverable as `a[i] % (n+1)`, and the occurrence count is `a[i] / (n+1)`. This "encode two numbers in one" trick is the same idea as Game of Life's bit packing. Sign marking alone tells "seen at least once", but it can't tell twice from three times.

Complexity: O(n) time, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

static void cyclic_sort(vector<int>& a) {
    for (int i = 0; i < (int)a.size(); ) {
        int want = a[i] - 1;                         // slot where a[i] belongs
        if (a[want] != a[i]) swap(a[i], a[want]);    // place it (stop if that slot already holds a copy)
        else ++i;
    }
}

vector<int> find_missing(vector<int> a) {
    cyclic_sort(a);
    vector<int> out;
    for (int i = 0; i < (int)a.size(); ++i) if (a[i] != i + 1) out.push_back(i + 1);
    return out;
}

vector<int> find_duplicates(vector<int> a) {
    for (int i = 0; i < (int)a.size(); ++i) {        // sign marking: a[v-1] < 0 means "v seen"
        int v = abs(a[i]);
        if (a[v - 1] > 0) a[v - 1] = -a[v - 1];
    }
    // second pass: count again, using a separate +n marker for "seen twice"
    int n = a.size();
    for (auto& x : a) x = abs(x);
    for (int i = 0; i < n; ++i) {
        int v = a[i] % (n + 1);                      // original value hidden under added multiples
        a[v - 1] += n + 1;
    }
    vector<int> out;
    for (int i = 0; i < n; ++i) if (a[i] / (n + 1) >= 2) out.push_back(i + 1);
    return out;
}
```
