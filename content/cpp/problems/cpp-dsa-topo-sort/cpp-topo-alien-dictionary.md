---
id: cpp-topo-alien-dictionary
title: Alien Dictionary
difficulty: Medium
order: 4
tags: topological sort, building the graph, strings, min-heap, invalid input
time_limit: 2
---
## Statement
An alien language uses some of the letters `a … z`, in an unknown order. You get a list of words that is **sorted** according to that alien order (ordinary dictionary rules: compare letter by letter; a proper prefix comes before the longer word). Recover an order of **all letters that appear** in the words that is consistent with the list.

Several orders may be consistent; return the one that is **smallest in ordinary alphabetical comparison** (as a string). If no order is consistent, return the empty string.

```cpp
std::string alien_order(const std::vector<std::string>& words);
```

The graph is not given; you build it. Only **adjacent** words carry information, and only at their **first differing position**: `"wrt"` before `"wrf"` says `t` comes before `f` and nothing else. If there is no differing position, the shorter word must come first: `"abc"` listed before `"ab"` is impossible. Then the letters are vertices, and a valid alphabet is a topological order.

**Input:** cases until the end of input: `n`, then `n` lowercase words (1 ≤ n ≤ 10⁵, total length ≤ 5·10⁵).

**Output (printed by the driver):** the alphabet, or `INVALID`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string alien_order(const vector<string>& words) {
    // TODO: just lists the letters in normal order
    array<bool, 26> seen{};
    for (auto& w : words) for (char c : w) seen[c - 'a'] = true;
    string s; for (int i = 0; i < 26; ++i) if (seen[i]) s += char('a' + i);
    return s;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<string> w(n);
        for (auto& x : w) cin >> x;
        string s = alien_order(w);
        cout << (s.empty() ? "INVALID" : s) << '\n';
    }
}
```

## Tests
=== sample
5
wrt
wrf
er
ett
rftt
---
wertf
=== sample
3
z
x
z
---
INVALID
=== sample
2
abc
ab
---
INVALID
=== hidden
1
hello
---
ehlo
=== hidden
2
ab
abc
---
abc
=== hidden
3
ca
cb
ba
---
acb
=== hidden
4
b
b
a
a
---
ba
=== hidden
3
a
ba
bc
---
abc
=== hidden
4
c
cd
eccd
eaba
3
bab
ba
a
3
a
aaaa
aaaa
6
aaa
a
aaa
a
aaaa
aaa
4
a
aaab
bb
baaa
3
ba
ddba
cada
5
b
bbb
baab
a
aaa
4
a
dcb
dbc
ab
---
bcade
INVALID
a
INVALID
INVALID
abdc
ba
INVALID
=== hidden
4
bb
aa
b
bab
5
ed
a
a
c
abe
2
abbc
cba
1
acb
4
bcdb
d
dc
cdba
6
c
cc
cc
cac
ac
aabb
3
aa
cc
dc
6
add
b
cab
ab
abc
ad
---
INVALID
INVALID
abc
abc
abdc
bca
acd
INVALID
=== hidden
5
b
bbe
bba
aec
abb
6
b
bcb
cbcb
ccac
a
ab
6
de
dcba
bdda
aecc
cddd
cda
6
ccba
cab
b
a
abc
aac
6
aa
a
a
aa
aa
aaaa
2
cb
baab
1
bdcb
2
c
dbc
---
ceba
bca
dbaec
cba
INVALID
acb
bcd
bcd
=== hidden
@gen 1258911151 big
=== hidden
@gen 1258911152 big
=== hidden
@gen 1258911153 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    if not big:
        al = "abcde"[:r.randint(1, 5)]
        order = list(al); r.shuffle(order); rk = {c: i for i, c in enumerate(order)}
        n = r.randint(1, 6)
        ws = ["".join(r.choice(al) for _ in range(r.randint(1, 4))) for _ in range(n)]
        if r.random() < 0.75: ws.sort(key=lambda w: [rk[c] for c in w])     # mostly valid lists
        print(n)
        for w in ws: print(w)
    else:
        order = list("abcdefghijklmnopqrstuvwxyz"); r.shuffle(order); rk = {c: i for i, c in enumerate(order)}
        n = 100000
        ws = ["".join(r.choice(order) for _ in range(r.randint(1, 6))) for _ in range(n)]
        ws.sort(key=lambda w: [rk[c] for c in w])
        if r.random() < 0.3: i = r.randrange(n - 1); ws[i], ws[i + 1] = ws[i + 1], ws[i]
        print(n)
        for w in ws: print(w)
```

## Hints
- Only adjacent words matter, and only at their first differing position: that gives one "letter x before letter y" edge.
- If there is no differing position, the longer word must not come first, or the input is invalid.
- Topologically sort the letters that appear; use a min-heap to get the alphabetically smallest valid alphabet, and detect cycles by counting.

## Solution
**What a sorted list tells you.** Compare two adjacent words. Up to their first differing position they agree, so nothing is learned there; at that position the earlier word's letter must come first in the alphabet; after it, the letters are unconstrained. Comparing non-adjacent words gives nothing new, because sortedness is transitive: if `w₁ ≤ w₂ ≤ w₃`, the constraints from the two adjacent pairs already imply `w₁ ≤ w₃`.

**The prefix trap.** If one word is a prefix of the next, the pair is fine when the shorter comes first and **impossible** when the longer comes first. Forgetting this check is the classic bug.

**Topological sort.** Letters are vertices, constraints are edges, and a valid alphabet is exactly a topological order of the letters that appear. A cycle (`a<b`, `b<c`, `c<a`) means the list is contradictory. Because the statement asks for the alphabetically smallest consistent alphabet, run Kahn's algorithm with a min-heap.

**Cost.** Building the graph scans each word at most twice: O(total length). The graph has at most 26 vertices and 650 edges, so the sort is negligible. Deduplicate edges, or count them consistently, so in-degrees are right.

Complexity: O(total length).

```cpp
#include <bits/stdc++.h>
using namespace std;

string alien_order(const vector<string>& words) {
    array<bool, 26> present{};
    for (auto& w : words) for (char c : w) present[c - 'a'] = true;
    array<array<bool, 26>, 26> edge{};          // dedupe: at most 26*25 distinct edges
    array<int, 26> indeg{};
    for (size_t i = 0; i + 1 < words.size(); ++i) {
        const string &a = words[i], &b = words[i + 1];
        size_t k = 0, L = min(a.size(), b.size());
        while (k < L && a[k] == b[k]) ++k;
        if (k == L) {                           // one is a prefix of the other
            if (a.size() > b.size()) return ""; // "abc" before "ab": impossible
            continue;
        }
        int x = a[k] - 'a', y = b[k] - 'a';     // the ONLY fact this pair gives: x before y
        if (!edge[x][y]) { edge[x][y] = true; ++indeg[y]; }
    }
    priority_queue<int, vector<int>, greater<int>> pq;   // smallest available letter first
    int total = 0;
    for (int c = 0; c < 26; ++c) if (present[c]) { ++total; if (indeg[c] == 0) pq.push(c); }
    string res;
    while (!pq.empty()) {
        int c = pq.top(); pq.pop();
        res += char('a' + c);
        for (int d = 0; d < 26; ++d) if (edge[c][d] && --indeg[d] == 0) pq.push(d);
    }
    return (int)res.size() == total ? res : "";          // leftover letters: contradictory cycle
}
```
