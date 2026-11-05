---
id: cpp-str-zigzag-prefix
title: Zigzag Conversion and Longest Common Prefix
difficulty: Medium
order: 8
tags: strings, simulation, sorting
time_limit: 2
---
## Statement
```cpp
std::string zigzag(const std::string& s, int rows);
    // write s in a zigzag over `rows` rows (down, then diagonally up, ...), then read row by row
std::string longest_common_prefix(std::vector<std::string> words);
```

Zigzag example: `"PAYPALISHIRING"` with 3 rows is written as

```text
P   A   H   N
A P L S I I G
Y   I   R
```

and read as `"PAHNAPLSIIGYIR"`. Simulate it with one buffer per row and a direction that flips at the top and bottom rows. With `rows = 1`, the string is unchanged.

**Longest common prefix:** compare column by column. (A cute alternative: after sorting, only the first and last words matter. Why?)

**Input:** lines `zig rows s` or `lcp n w1 ... wn`. Print `-` for an empty prefix.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string zigzag(const string& s, int rows) { return s; }
string longest_common_prefix(vector<string> words) { return words.empty() ? "" : words[0]; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "zig") {
            int r; string s; cin >> r >> s;
            string z = zigzag(s, r);
            cout << (z.size() <= 70 ? z : z.substr(0, 70) + "...") << '\n';
        } else {
            int n; cin >> n; vector<string> w(n); for (auto& x : w) cin >> x;
            string p = longest_common_prefix(w);
            cout << (p.empty() ? "-" : p) << '\n';
        }
    }
}
```

## Tests
=== sample
zig 3 PAYPALISHIRING
zig 4 PAYPALISHIRING
lcp 3 flower flow flight
lcp 3 dog racecar car
---
PAHNAPLSIIGYIR
PINALSIGYAHRPI
fl
-
=== hidden
zig 1 AB
zig 2 A
zig 5 ABC
lcp 1 solo
lcp 2 ab abc
lcp 3 aaa aa a
---
AB
A
ABC
solo
ab
a
=== hidden
zig 4 CCDAACBBAA
lcp 4 aabaaa aaba aababb aabab
zig 1 DCACCBCAABBCDAC
lcp 4 ba bb a bba
zig 4 A
lcp 3 baba bbbb bbbb
zig 3 CDADADACDA
lcp 2 bbaaab bba
lcp 4 ab bba a a
zig 3 ADABBCDCABCDDD
---
CBCCBDAAAA
aaba
DCACCBCAABBCDAC
-
A
b
CADDDDCAAA
bba
-
ABADDBCCBDDADC
=== hidden
lcp 2 aabb aabba
lcp 3 ab abba abb
lcp 2 baba baba
lcp 3 baa b baab
lcp 2 abba abb
zig 2 BADB
lcp 5 baabb ba baa baab baaba
zig 2 AAAACCC
lcp 1 aa
lcp 5 aab aabbab aabab aababb aab
---
aabb
ab
baba
b
abb
BDAB
ba
AACCAAC
aa
aab
=== hidden
zig 5 ABCDABCACBDB
zig 3 ACAC
lcp 3 aa aabab aaaa
zig 5 DACACD
lcp 2 ababa abaa
lcp 1 aba
zig 4 ACCCDC
lcp 2 bab a
zig 4 C
zig 1 AADABBBC
---
ACBABCCDDBBA
ACCA
aa
DACADC
aba
aba
ACCCDC
-
C
AADABBBC
=== hidden
@gen 3761069174 big
=== hidden
@gen 3761069175 big
=== hidden
@gen 3761069176 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = []
for _ in range(10 if not big else 2):
    if r.random() < 0.5:
        out.append(f"zig {r.randint(1, 5 if not big else 1000)} " + "".join(r.choice("ABCD") for _ in range(r.randint(1, 15 if not big else 1000000))))
    else:
        n = r.randint(1, 5) if not big else 100000
        base = "".join(r.choice("ab") for _ in range(r.randint(0, 4)))
        ws = [base + "".join(r.choice("ab") for _ in range(r.randint(0, 3))) or "a" for _ in range(n)]
        out.append(f"lcp {n} " + " ".join(ws))
print("\n".join(out))
```

## Hints
- Zigzag: keep one string per row, and walk the row index down and up, flipping direction at row 0 and row rows−1.
- Special case: with one row (or at least as many rows as characters), the string is unchanged.
- LCP: the common prefix of the smallest and largest words (lexicographically) is the common prefix of all of them.

## Solution
**Zigzag by simulation.** Characters go to rows `0, 1, …, rows−1, rows−2, …, 1, 0, 1, …`. One buffer per row and a direction that flips at the edges reproduces the picture exactly, and concatenating the rows reads it back. (There is also a direct index formula, with a cycle length of `2·rows − 2`, if you want O(1) extra memory.)

**Longest common prefix via the extremes.** The common prefix of all the words is the common prefix of the lexicographically **smallest** and **largest** words. Every other word lies between them in sorted order, so it shares whatever prefix the two extremes share. `minmax_element` finds them in O(total length) without a full sort.

Complexity: O(n) for zigzag, O(total characters) for the LCP.

```cpp
#include <bits/stdc++.h>
using namespace std;

string zigzag(const string& s, int rows) {
    if (rows == 1 || rows >= (int)s.size()) return s;
    vector<string> line(rows);
    int r = 0, dir = 1;
    for (char c : s) {
        line[r] += c;
        if (r == 0) dir = 1;                     // bounce off the top
        else if (r == rows - 1) dir = -1;        // bounce off the bottom
        r += dir;
    }
    string out;
    out.reserve(s.size());
    for (auto& l : line) out += l;
    return out;
}

string longest_common_prefix(vector<string> words) {
    if (words.empty()) return "";
    auto [mn, mx] = minmax_element(words.begin(), words.end());   // lexicographic extremes
    size_t k = 0;
    while (k < mn->size() && k < mx->size() && (*mn)[k] == (*mx)[k]) ++k;
    return mn->substr(0, k);
}
```
