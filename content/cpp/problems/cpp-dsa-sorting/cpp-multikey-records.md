---
id: cpp-multikey-records
title: Sorting Records by Several Keys
difficulty: Easy
order: 5
tags: sorting, comparators, stability, stable_sort, tuples
time_limit: 1
---
## Statement
A leaderboard holds records `name score time`. Implement two orderings:

```cpp
struct Rec { std::string name; int score; int time; int id; };   // id = original position

void rank_board(std::vector<Rec>& v);
    // score DESCENDING, then time ASCENDING, then name ASCENDING; any remaining ties keep input order
void group_by_score(std::vector<Rec>& v);
    // score ASCENDING only; records with equal scores must keep their ORIGINAL order (stability!)
```

Use one comparator per ordering, or compare tuples of keys, and choose between `sort` and `stable_sort` correctly. A comparator must be a **strict** weak ordering: never return `true` for equal elements, so never use `<=`.

**Input:** cases until the end of input: `rank n` or `group n`, then `n` lines `name score time` (n ≤ 2·10⁵). The driver prints the first 10 names in order, then a checksum of the full order of ids.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct Rec { string name; int score; int time; int id; };

void rank_board(vector<Rec>& v) {
    sort(v.begin(), v.end(), [](const Rec& a, const Rec& b) { return a.score >= b.score; });   // two bugs
}
void group_by_score(vector<Rec>& v) {
    sort(v.begin(), v.end(), [](const Rec& a, const Rec& b) { return a.score < b.score; });
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n;
    while (cin >> cmd >> n) {
        vector<Rec> v(n);
        for (int i = 0; i < n; ++i) { cin >> v[i].name >> v[i].score >> v[i].time; v[i].id = i; }
        if (cmd == "rank") rank_board(v); else group_by_score(v);
        for (int i = 0; i < min(n, 10); ++i) cout << v[i].name << ' ';
        unsigned long long h = 1469598103934665603ULL;
        for (auto& r : v) h = (h ^ (unsigned)r.id) * 1099511628211ULL;
        cout << "| " << h << '\n';
    }
}
```

## Tests
=== sample
rank 5
ann 90 30
bob 95 50
cat 90 20
dan 90 30
eve 95 50
group 5
ann 90 30
bob 95 50
cat 90 20
dan 90 30
eve 80 50
---
bob eve cat ann dan | 15454295055105475781
eve ann cat dan bob | 10791640031828024855
=== hidden
rank 1
solo 1 1
group 4
d 1 1
c 1 1
b 1 1
a 1 1
rank 4
zed 5 5
amy 5 5
amy 5 5
bob 5 4
---
solo | 4953163356653287321
d c b a | 2932290448510678823
bob amy amy zed | 6487137877693248473
=== hidden
group 6
eve 5 1
bob 0 2
cat 1 3
dan 0 1
fay 5 2
hal 2 1
group 7
gus 2 2
eve 0 5
gus 4 0
bob 2 1
fay 1 5
dan 0 2
gus 2 4
rank 4
dan 5 3
ann 2 2
bob 4 0
cat 2 2
rank 1
gus 5 1
---
bob dan cat hal eve fay | 939567791181888994
eve dan fay gus bob gus gus | 12607587965442376570
dan bob ann cat | 4801920911348289657
gus | 4953163356653287321
=== hidden
group 8
hal 0 3
dan 5 3
eve 4 1
dan 3 5
gus 3 5
dan 4 1
hal 2 1
gus 4 4
group 5
gus 0 2
cat 3 3
bob 4 3
gus 0 2
fay 5 4
rank 8
ann 0 2
bob 0 1
hal 0 0
gus 4 3
gus 4 2
gus 0 3
fay 3 1
gus 5 3
group 8
fay 2 1
hal 4 3
cat 0 4
gus 1 2
hal 2 2
dan 1 3
hal 4 5
bob 3 1
---
hal hal dan gus eve dan gus dan | 16321372192581156499
gus gus cat bob fay | 2094214290163438699
gus gus gus fay hal bob ann gus | 7698692486090430195
cat gus dan fay hal bob hal hal | 10503287868741454219
=== hidden
rank 9
fay 5 3
ann 2 5
fay 5 2
hal 5 3
cat 3 0
cat 0 2
hal 3 2
hal 3 1
fay 2 1
rank 6
hal 1 3
dan 2 3
fay 3 1
dan 4 2
eve 4 1
gus 2 1
group 4
dan 5 2
ann 3 1
fay 3 0
fay 5 5
group 1
dan 3 2
---
fay fay hal cat hal hal fay ann cat | 6123321560058520787
eve dan fay gus dan hal | 14696128772817566334
ann fay dan fay | 9225245158639696997
dan | 4953163356653287321
=== hidden
@gen 200695227 big
=== hidden
@gen 200695228 big
=== hidden
@gen 200695229 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
names = ["ann","bob","cat","dan","eve","fay","gus","hal"]
for _ in range(4 if not big else 1):
    n = r.randint(1, 10) if not big else 200000
    print(r.choice(["rank","group"]), n)
    for _ in range(n): print(r.choice(names) + ("" if not big else str(r.randint(0, 50))), r.randint(0, 5 if not big else 100), r.randint(0, 5 if not big else 100))
```

## Hints
- `tie(x1, x2, x3) < tie(y1, y2, y3)` compares lexicographically. For a descending key, put the other record's field on the left.
- Never use `<=` or `>=` in a comparator.
- "Equal records keep their input order" means you need `stable_sort` (or the original index as a last tiebreak).

## Solution
**Several keys, one comparator.** Compare the first key, and only if it is equal compare the next one. `std::tie(...)` builds tuples of references that compare lexicographically, which does exactly that. To make one key **descending**, swap which record it is taken from (`b.score` on the left side, `a.score` on the right).

**Stability.** `std::sort` may reorder equal elements arbitrarily. When "ties keep the input order" is part of the specification, use `stable_sort`. (Alternatively, add `id` as a final tiebreak key.) `group_by_score` is the textbook case: stable sorting by one key preserves any order that was already there.

**The starter's bugs:**

1. `>=` returns true for equal elements, which breaks strict weak ordering. That is undefined behaviour, and `std::sort` may even read out of bounds.
2. It only compares scores, ignoring the other keys.

Complexity: O(n log n · cost of a comparison).

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Rec { string name; int score; int time; int id; };

void rank_board(vector<Rec>& v) {
    stable_sort(v.begin(), v.end(), [](const Rec& a, const Rec& b) {
        // tie(...) builds tuples of references; tuples compare lexicographically
        return tie(b.score, a.time, a.name) < tie(a.score, b.time, b.name);   // score desc, time asc, name asc
    });
}

void group_by_score(vector<Rec>& v) {
    stable_sort(v.begin(), v.end(), [](const Rec& a, const Rec& b) { return a.score < b.score; });
}
```
