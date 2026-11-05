---
id: cpp-sw-anagram-windows
title: Find All Anagram Windows
difficulty: Medium
order: 6
tags: sliding window, fixed window, frequency counting, strings
time_limit: 2
---
## Statement
```cpp
std::vector<int> anagram_starts(const std::string& s, const std::string& p);
    // every start index i such that s.substr(i, |p|) is a permutation of p, in increasing order
```

Lowercase letters only. |s|, |p| ≤ 10⁶.

Comparing two 26-letter count arrays at every position costs 26 per step, which is fine. But learn the O(1)-per-step technique: keep `matched`, the number of letters (out of 26) whose window count equals their count in `p`. Adding or removing one letter changes `matched` by at most one. The window is an anagram exactly when `matched == 26`.

**Input:** pairs of lines `s` and `p`, until the end of input. Print the number of starts and the first 20 of them.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> anagram_starts(const string& s, const string& p) {
    vector<int> out;
    string sp = p; sort(sp.begin(), sp.end());
    for (size_t i = 0; i + p.size() <= s.size(); ++i) {
        string t = s.substr(i, p.size()); sort(t.begin(), t.end());   // O(n · k log k)
        if (t == sp) out.push_back(i);
    }
    return out;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string s, p;
    while (getline(cin, s) && getline(cin, p)) {
        auto v = anagram_starts(s, p);
        cout << v.size() << ':';
        for (size_t i = 0; i < min<size_t>(v.size(), 20); ++i) cout << ' ' << v[i];
        cout << '\n';
    }
}
```

## Tests
=== sample
cbaebabacd
abc
abab
ab
---
2: 0 6
3: 0 1 2
=== hidden
a
a
a
aa
aaaaa
aa
abcdefg
gfedcba
---
1: 0
0:
4: 0 1 2 3
1: 0
=== hidden
cba
a
cbacccacacccb
aabb
bcbccababcaacc
cbac
bbacbab
abaa
babacccabbacb
ccca
abcabacbab
bcb
---
1: 2
0:
2: 2 3
0:
2: 3 4
0:
=== hidden
ccbcbb
a
caaccacacbaac
a
baba
cbac
aabbaaacbcababa
abc
bcacaacbbcb
ab
abaaab
bb
---
0:
6: 1 2 5 7 10 11
0:
3: 6 8 9
0:
0:
=== hidden
bbbcc
caac
bba
ba
acbbabcaca
b
bcbbc
ccac
ccccbcaa
c
cca
b
---
0:
1: 1
3: 2 3 5
0:
5: 0 1 2 3 5
0:
=== hidden
@gen 4221210549 big
=== hidden
@gen 4221210550 big
=== hidden
@gen 4221210551 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    for _ in range(6):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 15))); p = "".join(r.choice("abc") for _ in range(r.randint(1, 4)))
        print(s); print(p)
else:
    print("".join(r.choice("ab") for _ in range(1000000))); print("".join(r.choice("ab") for _ in range(1000)))
    print("".join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(1000000))); print("abc")
```

## Hints
- Use a fixed window of length |p|, with counts `have[26]` against `need[26]`.
- Comparing the two arrays every step works (26 operations). For O(1), track how many letters currently match exactly.
- When a count changes by one, only that letter's matched/unmatched status can flip. Check the boundary cases `== need` and `== need + 1`.

## Solution
**Fixed window of length |p|:** add `s[R]`, and remove `s[R − k]` once the window is too long.

**The `matched` counter.** A letter is "matched" when its window count equals its count in `p`. Changing one letter's count by one can only switch *that* letter between matched and unmatched:

- **Add:** if the new count equals the target, it just became matched. If it is one above the target, it was matched before and isn't any more.
- **Remove** (checked before decrementing): if the current count equals the target, it is about to become unmatched. If it is one above the target, it is about to become matched.

`matched == 26` means every letter has exactly the right count: the window is an anagram. Each step is O(1) regardless of alphabet size, which matters for big alphabets (a hash map of counts plus the same counter).

Complexity: O(|s| + |p|) time, O(alphabet) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> anagram_starts(const string& s, const string& p) {
    vector<int> out;
    int n = s.size(), k = p.size();
    if (k == 0 || k > n) return out;
    array<int, 26> need{}, have{};
    for (char c : p) ++need[c - 'a'];
    int matched = 0;                                  // letters with have[c] == need[c]
    for (int x : need) matched += x == 0;             // the empty window matches every absent letter
    for (int R = 0; R < n; ++R) {
        int c = s[R] - 'a';
        if (++have[c] == need[c]) ++matched;          // reached the target count
        else if (have[c] == need[c] + 1) --matched;   // just went over it
        if (R >= k) {
            int d = s[R - k] - 'a';
            if (have[d] == need[d]) --matched;        // about to drop below the target
            else if (have[d] == need[d] + 1) ++matched;   // about to come back to it
            --have[d];
        }
        if (R >= k - 1 && matched == 26) out.push_back(R - k + 1);
    }
    return out;
}
```
