---
id: cpp-ps-xor-and-balance
title: Subarray XOR and Balanced Subarrays
difficulty: Medium
order: 7
tags: prefix xor, hashing, counting, transformations
time_limit: 2
---
## Statement
Two problems that become "prefix + hash map" after a small **transformation**:

```cpp
long long count_xor_k(const std::vector<int>& a, int k);
    // subarrays whose XOR equals k
long long count_balanced(const std::string& s);
    // substrings of a string over {a, b, c} with as many a's as b's (c's don't matter)
```

- **XOR:** `xor(l..r) = X[r+1] ^ X[l]`. You want `X[l] = X[r+1] ^ k`, so count the earlier prefix XORs equal to `current ^ k`.
- **Balanced:** map `a → +1`, `b → −1`, `c → 0`. A balanced substring has a total of 0, which means two equal prefix values. Count the pairs of equal prefix values.

**Input:** cases until the end of input: `xor n k` + values, or `bal s`. n ≤ 10⁶, 0 ≤ a[i], k < 2²⁰.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_xor_k(const vector<int>& a, int k) { return 0; }
long long count_balanced(const string& s) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "xor") {
            int n, k; cin >> n >> k;
            vector<int> a(n); for (auto& x : a) cin >> x;
            cout << count_xor_k(a, k) << '\n';
        } else { string s; cin >> s; cout << count_balanced(s) << '\n'; }
    }
}
```

## Tests
=== sample
xor 5 6
4 2 2 6 4
bal abcab
---
4
7
=== hidden
xor 1 0
0
xor 3 0
0 0 0
bal c
bal ab
bal aaaa
---
1
6
1
1
0
=== hidden
bal acacccbacac
xor 7 0
3 4 6 6 5 2 5
bal baacbcababc
xor 8 1
4 0 1 6 4 6 6 0
xor 8 3
5 6 4 1 7 3 0 0
bal cbaacaabbb
---
19
2
27
3
5
10
=== hidden
xor 7 1
2 6 6 2 2 4 3
bal cbccbbc
xor 3 2
4 2 4
xor 9 4
5 2 7 2 3 5 0 6 3
bal bcbccab
bal aaac
---
1
5
2
6
9
1
=== hidden
xor 12 7
7 5 3 6 1 0 6 6 4 1 3 1
xor 11 3
2 4 3 0 0 7 3 4 4 6 5
bal cbabab
bal bbbaacbac
xor 8 3
6 4 3 5 2 2 0 1
xor 10 5
1 6 7 4 4 4 4 0 4 5
---
12
10
9
13
3
6
=== hidden
@gen 3623221336 big
=== hidden
@gen 3623221337 big
=== hidden
@gen 3623221338 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 12) if not big else 1000000
    if r.random() < 0.5:
        print("xor", n, r.randint(0, 7) if not big else r.randint(0, 2**20 - 1)); print(*[r.randint(0, 7) if not big else r.randint(0, 255) for _ in range(n)])
    else:
        print("bal", "".join(r.choice("abc") for _ in range(n)))
```

## Hints
- XOR prefix: `xor(l..r) = X[r+1] ^ X[l]`. What must `X[l]` be for the result to be k?
- For the balanced count, map `a → +1`, `b → −1`, `c → 0`. A balanced substring has sum 0.
- Sum 0 means two equal prefix values. Count them with an array indexed by `pre + n`.

## Solution
Both are "count pairs of prefixes in a relation":

- **XOR:** `X[r] ^ X[l] = k` is the same as `X[l] = X[r] ^ k`, because XOR is its own inverse. Look that value up among the earlier prefixes.
- **Balanced:** after mapping the characters to +1/−1/0, "#a = #b" means the substring sum is 0. That means `P[r] = P[l]`, so count the earlier equal prefixes.

**Arrays instead of hash maps.** When the keys are small integers (XOR values below 2²⁰, prefix sums in `[−n, n]` shifted by `n`), a plain `vector` is a perfect hash. It's faster than `unordered_map` and immune to collision attacks.

The learning point is the **transformation step**: many "count substrings with property X" problems become "count equal (or related) prefix values" after mapping the elements cleverly.

Complexity: O(n) time.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_xor_k(const vector<int>& a, int k) {
    vector<long long> seen(1 << 20, 0);            // values < 2^20: an array beats a hash map
    seen[0] = 1;
    int pre = 0; long long cnt = 0;
    for (int x : a) {
        pre ^= x;
        cnt += seen[pre ^ k];                      // earlier prefixes X with X ^ pre == k
        ++seen[pre];
    }
    return cnt;
}

long long count_balanced(const string& s) {
    int n = s.size();
    vector<long long> seen(2 * n + 1, 0);          // prefix values lie in [-n, n]: shift by n
    seen[n] = 1;
    int pre = 0; long long cnt = 0;
    for (char c : s) {
        pre += c == 'a' ? 1 : c == 'b' ? -1 : 0;
        cnt += seen[pre + n];                      // equal prefixes => zero-sum substring
        ++seen[pre + n];
    }
    return cnt;
}
```
