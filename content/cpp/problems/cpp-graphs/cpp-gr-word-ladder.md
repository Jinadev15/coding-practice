---
id: cpp-gr-word-ladder
title: Word Ladder (BFS on an Implicit Graph)
difficulty: Hard
order: 9
tags: BFS, implicit graph, hashing, wildcard buckets, strings
time_limit: 2
---
## Statement
A **word ladder** turns `begin` into `end` by changing **one letter at a time**, where every intermediate word (and `end`) must be in the dictionary. Return the number of words in the **shortest** ladder, counting both `begin` and `end`, or `0` if no ladder exists. `begin` does not need to be in the dictionary; `begin ≠ end`.

```cpp
int ladder_length(const std::string& begin, const std::string& end, const std::vector<std::string>& dict);
```

Nobody gives you the edges. Two words are adjacent when they differ in exactly one position, and comparing all pairs costs O(n²·L), which is 2.5·10⁹ for 5·10⁴ words. Generate neighbours instead: either try all 25 replacement letters at each position and look the result up in a hash set, or group words into **wildcard buckets** (`h*t` holds `hot`, `hit`, `hat`) so that each bucket is a clique of neighbours.

**Input:** cases until the end of input: `n L`, then `begin`, `end`, then `n` dictionary words. All words are lowercase with length exactly `L` (1 ≤ n ≤ 5·10⁴, 1 ≤ L ≤ 10). The dictionary may contain duplicates.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int ladder_length(const string& begin, const string& end, const vector<string>& dict) {
    // O(n^2 * L): compares every pair of words. Correct but far too slow for 5e4 words.
    vector<string> w = dict; w.push_back(begin);
    int n = w.size();
    vector<int> d(n, 0); d[n - 1] = 1;
    vector<int> q{n - 1};
    for (size_t h = 0; h < q.size(); ++h) {
        int u = q[h];
        if (w[u] == end) return d[u];
        for (int v = 0; v < n; ++v) {
            if (d[v]) continue;
            int diff = 0; for (size_t k = 0; k < w[u].size(); ++k) diff += w[u][k] != w[v][k];
            if (diff == 1) { d[v] = d[u] + 1; q.push_back(v); }
        }
    }
    return 0;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, L;
    while (cin >> n >> L) {
        string b, e; cin >> b >> e;
        vector<string> d(n);
        for (auto& w : d) cin >> w;
        cout << ladder_length(b, e, d) << '\n';
    }
}
```

## Tests
=== sample
6 3
hit
cog
hot
dot
dog
lot
log
cog
---
5
=== sample
5 3
hit
cog
hot
dot
dog
lot
log
---
0
=== hidden
1 1
a
c
c
---
2
=== hidden
2 2
ab
cd
cb
cd
---
3
=== hidden
3 3
abc
abd
xyz
xyz
abd
---
2
=== hidden
4 1
b
a
a
b
a
a
7 1
a
b
a
b
b
b
b
b
b
6 3
aba
aaa
bab
bbb
bbb
bab
bba
aaa
5 3
bab
abb
aaa
bab
bab
abb
abb
6 1
b
c
c
a
b
a
a
c
---
2
2
2
0
2
=== hidden
10 2
bc
aa
ca
cb
ba
cb
aa
ab
ab
ca
cb
aa
6 2
ba
bb
ab
ab
ba
aa
aa
ba
8 2
ac
bb
bc
ac
bb
ac
aa
bc
aa
bb
3 1
b
a
a
a
a
2 3
bbb
bbc
aaa
bbc
---
3
0
3
2
2
=== hidden
3 3
bba
cbb
ccb
bab
cbb
9 3
ccb
aba
bbb
aca
cbb
cca
aab
acc
abc
aab
aba
6 2
bc
ba
cc
ac
ac
ab
ba
ba
6 3
abb
bbb
aba
baa
aaa
aab
aab
bbb
10 1
a
b
a
a
a
a
a
a
a
a
a
a
---
0
4
2
2
0
=== hidden
@gen 3935760829 big
=== hidden
@gen 3935760830 big
=== hidden
@gen 3935760831 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    if not big:
        L = r.randint(1, 3); al = "abc"[:r.randint(2, 3)]
        n = r.randint(1, 10)
        rw = lambda: "".join(r.choice(al) for _ in range(L))
        b = rw(); e = rw()
        while e == b: e = rw()
        d = [rw() for _ in range(n)]
        if r.random() < 0.6: d.append(e)
        print(len(d), L); print(b); print(e)
        for w in d: print(w)
    else:
        L = 10; n = 50000
        # mostly 2-letter alphabet in the first 6 positions: a big connected cluster, long ladders
        def rw(): return "".join(r.choice("ab") for _ in range(8)) + "".join(r.choice("abcdefghijklmnopqrstuvwxyz"[:3]) for _ in range(2))
        d = [rw() for _ in range(n)]
        b = "a" * 10; e = "b" * 8 + "cc"; d.append(e)
        print(len(d), L); print(b); print(e)
        for w in d: print(w)
```

## Hints
- Each word is a vertex, and words differing in exactly one letter are adjacent; BFS gives the shortest ladder.
- Don't compare all pairs. From a word, generate the 25·L candidates by changing one letter and look them up in a hash set.
- Count words, not moves: `begin` has distance 1. Return 0 if `end` isn't in the dictionary.

## Solution
**An implicit graph.** Vertices are words; edges join words at Hamming distance 1. The shortest ladder is a BFS shortest path, plus one because the answer counts words, not steps.

**Generating neighbours.** Never build the O(n²) edge list. From a word of length `L`, the only possible neighbours are the `25·L` strings obtained by changing one letter. Look each one up in a hash map from word to id: O(L) per lookup to hash, so O(25·L²) work per word, about 2500 operations, and 1.25·10⁸ for 5·10⁴ words in the worst case, which is fine in C++.

**Alternative: wildcard buckets.** Map each pattern like `h*t` to the list of words matching it. Neighbours of `hot` are the members of `*ot`, `h*t`, `ho*`. After a bucket is used once, clear it, since every word in it has been reached at that BFS level. That bound is O(n·L) bucket insertions, better when the alphabet is large.

**Details.** `begin` gets an id even if it isn't in the dictionary (it can be the start but not a destination of others unless listed). Duplicates collapse to one id. Check `end ∈ dict` first. A bidirectional BFS (expanding the smaller frontier from both ends) is a common speed-up on huge dictionaries.

Complexity: O(n·L·25·L) with neighbour generation.

```cpp
#include <bits/stdc++.h>
using namespace std;

int ladder_length(const string& begin, const string& end, const vector<string>& dict) {
    unordered_map<string, int> id;                 // word -> vertex id (dedups the dictionary)
    id.reserve(dict.size() * 2 + 2);
    vector<string> words;
    auto get = [&](const string& w) {
        auto [it, fresh] = id.emplace(w, (int)words.size());
        if (fresh) words.push_back(w);
        return it->second;
    };
    for (auto& w : dict) get(w);
    if (!id.count(end)) return 0;                  // end must be a dictionary word
    int s = get(begin), t = id[end];
    vector<int> dist(words.size(), 0);
    dist[s] = 1;                                   // ladder length counts words, so begin is 1
    vector<int> q{s};
    for (size_t h = 0; h < q.size(); ++h) {
        int u = q[h];
        if (u == t) return dist[u];
        string w = words[u];
        for (size_t k = 0; k < w.size(); ++k) {
            char orig = w[k];
            for (char c = 'a'; c <= 'z'; ++c) {    // generate neighbours on the fly
                if (c == orig) continue;
                w[k] = c;
                auto it = id.find(w);
                if (it != id.end() && dist[it->second] == 0) {
                    dist[it->second] = dist[u] + 1;
                    q.push_back(it->second);
                }
            }
            w[k] = orig;
        }
    }
    return 0;
}
```
