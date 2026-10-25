---
id: cpp-josephus
title: The Josephus Problem
difficulty: Medium
order: 6
tags: recursion, recurrence, recursion to iteration, simulation
time_limit: 1
---
## Statement
`n` people stand in a circle, numbered `1..n`. Starting from person 1, count `k` people clockwise (person 1 counts as the first). The `k`-th person is removed, and counting restarts at the next person. Who is the last one left?

```cpp
long long survivor(long long n, long long k);                  // n <= 10^7, k <= 10^9
std::vector<int> elimination_order(int n, int k);              // n <= 2000: the order people are removed
```

Number the people from 0 for the recurrence. If `J(n)` is the 0-based survivor:

`J(1) = 0`, and `J(n) = (J(n−1) + k) mod n`

because after the first removal, the circle of `n−1` people is the same problem shifted by `k`.

A direct recursive `J(n)` with n = 10⁷ would be 10⁷ frames deep and overflow the stack. **Turn the recurrence into a loop.** For the elimination order, simulating with an index into a `vector` is fine at n ≤ 2000.

**Input:** commands `last n k` and `order n k` until the end of input.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long survivor(long long n, long long k) {
    if (n == 1) return 1;
    return (survivor(n - 1, k) + k - 1) % n + 1;   // correct idea... but how deep does it go?
}
vector<int> elimination_order(int n, int k) { return {}; }
```

## Driver
```cpp
int main() {
    string cmd; long long n, k;
    while (cin >> cmd >> n >> k) {
        if (cmd == "last") cout << survivor(n, k) << '\n';
        else {
            auto v = elimination_order((int)n, (int)k);
            for (size_t i = 0; i < v.size(); ++i) cout << v[i] << (i + 1 < v.size() ? ' ' : '\n');
        }
    }
}
```

## Tests
=== sample
last 7 3
order 7 3
last 1 5
---
4
3 6 2 7 5 1 4
1
=== hidden
last 10000000 2
last 10000000 1000000000
order 1 1
order 5 1
---
3222785
4852115
1
1 2 3 4 5
=== hidden
order 2000 7
last 2000 7
last 41 3
=== hidden
order 25 3
last 23 30
order 28 34
last 20 13
order 30 15
last 26 26
last 27 21
order 11 18
order 4 20
last 7 23
---
3 6 9 12 15 18 21 24 2 7 11 16 20 25 5 13 19 1 10 22 8 23 17 4 14
8
6 13 21 2 14 26 12 1 20 15 9 8 11 19 28 18 10 16 24 17 23 7 3 25 4 5 27 22
17
15 30 16 2 19 6 24 12 3 23 14 8 1 27 25 22 26 29 7 13 28 17 10 11 21 20 9 5 18 4
13
18
7 4 3 6 11 10 5 9 8 2 1
4 2 1 3
3
=== hidden
order 6 17
order 11 19
order 7 8
last 27 35
last 9 8
last 4 27
order 3 35
last 16 10
last 30 38
order 12 7
---
5 1 2 4 6 3
8 6 7 11 5 9 3 1 2 4 10
1 3 6 5 2 7 4
5
3
1
2 3 1
1
25
7 2 10 6 4 3 5 9 1 8 11 12
=== hidden
order 26 12
last 2 11
order 9 33
last 20 22
last 9 13
order 19 7
order 6 15
order 5 28
last 4 16
last 29 15
---
12 24 10 23 11 26 15 4 20 13 5 25 19 17 16 18 22 3 9 6 2 8 7 1 21 14
2
6 7 3 8 2 4 1 5 9
6
2
7 14 2 10 18 8 17 9 1 13 6 4 3 5 12 19 11 15 16
3 2 6 5 1 4
3 2 4 1 5
2
19
=== hidden
order 267 149478713
order 1067 425720023
last 1479 349479610
order 965 342618349
last 501 594258383
last 241 450945900
order 972 703268169
order 400 510399224
order 1038 809150222
order 847 921259796
last 10000000 518000193
=== hidden
order 230 999090943
order 129 973357122
order 1660 344307599
last 338 536188849
last 1204 635854558
order 1521 307426635
order 874 880721124
order 116 222259589
last 1494 455762222
last 69 544717749
last 10000000 414656661
=== hidden
order 157 839183378
order 681 795987218
order 1555 427740552
last 1519 98840218
order 1972 621655756
order 539 347653614
last 431 272358339
order 1582 17668669
last 181 168417641
last 1151 944177657
last 10000000 29285313

## Hints
- The recursive version is right, but n = 10⁷ means 10⁷ nested calls. How big is the stack?
- `J(n)` only needs `J(n−1)`. Loop `m` from 2 to `n` and keep a single variable.
- For the order, after erasing index `i`, the next counting starts at index `i` again (everyone shifted left).

## Solution
**Survivor.** The recurrence only looks at `J(n−1)`, so compute it **bottom-up**: start from `J(1) = 0` and apply `j = (j + k) % m` for `m = 2..n`. That's O(n) time and O(1) memory, with no stack at all.

The starter's recursive version gives correct answers for small `n`, but it crashes with a stack overflow at large `n`. That is a classic interview trap.

Why the recurrence holds: after the first removal (person `(k−1) mod n`), renumber the remaining `n−1` people starting from the one after the removed person. Their survivor is `J(n−1)` in the new numbering, which is `(J(n−1) + k) mod n` in the old one.

**Order.** Keep the current index and remove `people[(idx + k − 1) mod size]`. The next count starts at that same index, because the remaining people shift down.

Complexity: survivor O(n), order O(n²).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long survivor(long long n, long long k) {
    long long j = 0;                      // J(1) = 0 (0-based)
    for (long long m = 2; m <= n; ++m)    // build J(2), J(3), ..., J(n) bottom-up
        j = (j + k) % m;
    return j + 1;                         // back to 1-based
}

vector<int> elimination_order(int n, int k) {
    vector<int> people(n);
    iota(people.begin(), people.end(), 1);
    vector<int> order;
    int idx = 0;
    while (!people.empty()) {
        idx = (int)((idx + (long long)k - 1) % (long long)people.size());
        order.push_back(people[idx]);
        people.erase(people.begin() + idx);   // O(n) each: fine for n <= 2000
    }
    return order;
}
```
