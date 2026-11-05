---
id: cpp-tp-boats
title: Boats to Save People
difficulty: Medium
order: 9
tags: two pointers, greedy, sorting
time_limit: 2
---
## Statement
Each boat carries **at most two people** and at most `limit` kilograms. People weigh `w[i] ≤ limit`. What is the minimum number of boats needed to carry everyone?

```cpp
int min_boats(std::vector<int> w, int limit);
```

`w = [3,2,2,1]`, `limit = 3` needs 3 boats: (1,2), (2) and (3).

**Greedy with two pointers.** Sort the weights. The heaviest remaining person must take a boat. Pair them with the lightest remaining person if the two fit together, and otherwise they go alone. Think about why pairing the heaviest with the lightest is never worse than any other pairing.

**Input:** cases until the end of input: `n limit` + weights (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int min_boats(vector<int> w, int limit) { return (int)w.size(); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, limit;
    while (cin >> n >> limit) {
        vector<int> w(n);
        for (auto& x : w) cin >> x;
        cout << min_boats(w, limit) << '\n';
    }
}
```

## Tests
=== sample
2 3
1 2
4 3
3 2 2 1
4 5
3 5 3 4
---
1
3
4
=== hidden
1 10
10
5 6
3 3 3 3 3
6 10
1 9 2 8 3 7
3 4
4 4 4
---
1
3
3
3
=== hidden
3 3
1 1 1
4 2
2 2 1 2
2 9
3 1
1 3
2
4 7
4 5 5 7
5 1
1 1 1 1 1
---
2
4
1
1
4
5
=== hidden
3 4
1 1 3
5 8
8 5 1 1 4
8 5
2 1 2 2 3 1 3 2
2 7
1 7
1 4
4
1 10
9
---
2
3
4
2
1
1
=== hidden
5 1
1 1 1 1 1
1 10
2
6 7
7 3 7 1 2 1
6 8
8 8 2 3 6 4
8 7
6 5 3 4 1 7 7 5
5 1
1 1 1 1 1
---
5
1
4
4
6
5
=== hidden
@gen 2330731040 big
=== hidden
@gen 2330731041 big
=== hidden
@gen 2330731042 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 8) if not big else 1000000
    lim = r.randint(1, 10) if not big else 10**9
    print(n, lim); print(*[r.randint(1, lim) for _ in range(n)])
```

## Hints
- Sort the weights. Who definitely needs a boat right now?
- Try to pair the heaviest remaining person with the lightest remaining one.
- If they fit, both leave (`L++`, `R--`). Otherwise only the heaviest leaves. Count one boat either way.

## Solution
The heaviest person `R` needs a boat regardless.

- If even the **lightest** person `L` can't share with them, nobody can, so `R` goes alone.
- If `L` fits, put `L` with `R`. This is an **exchange argument**: take any optimal plan where `R` rides with someone else, or alone. Swapping `L` into `R`'s boat can't break the weight limit anywhere. `L`'s old partner is lighter than `R`, so they fit wherever `L` was. So pairing `R` with `L` is always safe.

Each boat removes `R`, and sometimes `L` as well, so the pointers meet after at most n boats.

Complexity: O(n log n) for the sort, then O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

int min_boats(vector<int> w, int limit) {
    sort(w.begin(), w.end());
    int L = 0, R = (int)w.size() - 1, boats = 0;
    while (L <= R) {
        if (L < R && (long long)w[L] + w[R] <= limit) ++L;   // lightest rides with the heaviest
        --R;                                                 // heaviest always leaves
        ++boats;
    }
    return boats;
}
```
