---
id: cpp-ms-stock-spanner
title: Online Stock Spanner
difficulty: Easy
order: 2
tags: monotonic stack, online algorithm, design, previous greater element
time_limit: 1
---
## Statement
Prices arrive one per day. The **span** of today is the number of consecutive days, ending today and going backwards, on which the price was **≤ today's price** (today included).

```cpp
class StockSpanner {
public:
    int next(int price);   // record today's price and return today's span
};
```

Prices `100 80 60 70 60 75 85` give spans `1 1 1 2 1 4 6`.

This is an **online** problem: `next` must answer before it sees later prices. Each call must be O(1) amortized.

**Input:** `q`, then `q` prices (q ≤ 10⁶, 1 ≤ price ≤ 10⁹). Print the spans on one line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class StockSpanner {
    vector<int> prices;
public:
    int next(int price) {
        prices.push_back(price);
        int j = (int)prices.size() - 1;
        while (j >= 0 && prices[j] <= price) --j;      // walks back day by day: O(n) per call
        return (int)prices.size() - 1 - j;
    }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    StockSpanner sp;
    string out;
    for (int i = 0; i < q; ++i) { int p; cin >> p; if (i) out += ' '; out += to_string(sp.next(p)); }
    cout << out << '\n';
}
```

## Tests
=== sample
7
100 80 60 70 60 75 85
---
1 1 1 2 1 4 6
=== hidden
1
5
5
3 3 3 3 3
6
1 2 3 4 5 6
6
6 5 4 3 2 1
---
1
=== hidden
5
6 6 6 1 5
---
1 2 3 1 2
=== hidden
12
3 4 4 2 5 2 3 6 2 1 4 4
---
1 2 3 1 5 1 2 8 1 1 3 4
=== hidden
4
5 2 2 5
---
1 1 2 4
=== hidden
@gen 826238578 big
=== hidden
@gen 826238579 big
=== hidden
@gen 826238580 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(1, 15) if not big else 1000000
if big and r.random() < 0.6:
    a = sorted(r.randint(1, 10**9) for _ in range(q))
else:
    a = [r.randint(1, 6) if not big else r.randint(1, 10**9) for _ in range(q)]
print(q); print(*a)
```

## Hints
- The span stops at the previous day with a strictly greater price.
- Once today's price is known, earlier days with smaller or equal prices will never be a boundary again. Merge them.
- Stack `(price, span)` pairs. Pop while `top.price <= price`, adding the popped spans.

## Solution
The span reaches back to the **previous strictly greater** price. Once a price `p` arrives, every earlier price `≤ p` can never be the boundary for any later day: a later day either stops at `p` or jumps past it. So those days can be **merged into `p`**.

Keep a stack of `(price, span)` with strictly decreasing prices. A new price pops every entry with price `≤` it and adds their spans to its own, which is exactly the number of days they covered:

```text
100        [(100,1)]                 span 1
80         [(100,1) (80,1)]          span 1
60         [... (60,1)]              span 1
70         pop (60,1): span 2        [(100,1) (80,1) (70,2)]
60         push                      span 1
75         pop 60 (+1), pop 70 (+2): span 4
85         pop 75 (+4), pop 80 (+1): span 6
```

Each day is pushed once and popped at most once: O(1) amortized per call, O(n) memory in the worst case (strictly decreasing prices).

```cpp
#include <bits/stdc++.h>
using namespace std;

class StockSpanner {
    vector<pair<int,int>> st;      // (price, span): prices strictly decreasing from bottom to top
public:
    int next(int price) {
        int span = 1;
        while (!st.empty() && st.back().first <= price) {   // absorb every day it dominates
            span += st.back().second;
            st.pop_back();
        }
        st.push_back({price, span});
        return span;
    }
};
```
