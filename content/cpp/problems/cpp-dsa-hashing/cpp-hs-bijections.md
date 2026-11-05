---
id: cpp-hs-bijections
title: Isomorphic Strings and Word Patterns
difficulty: Easy
order: 4
tags: hashing, bijection, strings, maps
time_limit: 1
---
## Statement
```cpp
bool isomorphic(const std::string& s, const std::string& t);
    // can the characters of s be replaced (consistently, one-to-one) to get t? "egg"/"add" yes, "foo"/"bar" no
bool word_pattern(const std::string& pattern, const std::vector<std::string>& words);
    // does each pattern letter map to exactly one word, and each word to exactly one letter?
```

A **bijection** needs checks in **both** directions. With only `letter → word`, the pattern `ab` would wrongly match `dog dog`. Keep two maps, or compare the first-occurrence index sequences of both sides.

**Input:** lines until the end of input: `iso s t`, or `pat pattern n w1 ... wn`. Print `true`/`false`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool isomorphic(const string& s, const string& t) {
    if (s.size() != t.size()) return false;
    map<char, char> f;
    for (size_t i = 0; i < s.size(); ++i) {
        if (f.count(s[i]) && f[s[i]] != t[i]) return false;
        f[s[i]] = t[i];
    }
    return true;                                   // one direction only
}
bool word_pattern(const string& p, const vector<string>& w) { return p.size() == w.size(); }
```

## Driver
```cpp
int main() {
    string cmd;
    while (cin >> cmd) {
        if (cmd == "iso") { string s, t; cin >> s >> t; cout << (isomorphic(s, t) ? "true" : "false") << '\n'; }
        else {
            string p; int n; cin >> p >> n;
            vector<string> w(n); for (auto& x : w) cin >> x;
            cout << (word_pattern(p, w) ? "true" : "false") << '\n';
        }
    }
}
```

## Tests
=== sample
iso egg add
iso foo bar
iso paper title
iso badc baba
pat abba 4 dog cat cat dog
pat abba 4 dog dog dog dog
---
true
false
true
false
true
false
=== hidden
iso a a
iso ab aa
iso abc ab
pat a 1 x
pat ab 2 dog dog
pat aaa 3 x x y
---
true
false
false
true
false
false
=== hidden
iso c x
iso ccbaa zzxyy
iso cc yy
iso cc yz
pat abbabb 6 w1 w0 w2 w1 w0 w1
pat aab 3 w1 w0 w1
pat bbaa 4 w2 w1 w0 w1
iso baaab yzzzy
pat aabb 4 w0 w1 w1 w0
pat abbaab 6 w0 w0 w0 w1 w0 w0
pat abab 4 w2 w2 w1 w0
pat ba 2 w2 w1
pat aa 2 w1 w0
iso ba yz
pat b 1 w0
iso aabbaa zyzyyy
pat aaa 3 w1 w0 w0
iso ba zyx
iso acaca xyyxz
pat aaaaaa 6 w2 w1 w1 w2 w1 w0
---
true
true
true
false
false
false
false
true
false
false
false
true
false
true
true
false
false
false
false
false
=== hidden
iso a xz
pat abba 4 w2 w2 w2 w0
pat b 1 w2
iso aab zxx
pat bbaaa 5 w0 w2 w1 w1 w0
pat a 1 w1
pat ba 2 w1 w0
iso cbacc xyxyy
iso c y
iso bbaaa zzyyy
pat aabb 4 w0 w2 w2 w1
pat baa 3 w2 w1 w0
pat bb 2 w1 w1
pat b 1 w2
pat aa 2 w1 w1
pat b 1 w2
iso bcbaca zyzxxy
pat abbaa 5 w0 w0 w0 w2 w2
pat babbb 5 w1 w1 w0 w0 w2
iso caa zzz
---
false
false
true
false
false
true
true
false
true
true
false
false
true
true
true
true
false
false
false
false
=== hidden
pat bbabba 6 w0 w1 w2 w1 w2 w0
iso cbabaa zzzxxx
pat aba 3 w2 w2 w0
pat bbabbb 6 w0 w2 w0 w0 w0 w2
iso ac zx
pat bbab 4 w0 w1 w1 w2
iso cccb xzzx
iso ccbccb zyyxyy
iso bbbab zxxyy
pat bbaa 4 w0 w2 w2 w0
pat bbb 3 w2 w2 w0
pat babaa 5 w2 w0 w2 w1 w0
pat aa 2 w2 w0
pat b 1 w1
pat ab 2 w1 w1
pat baabb 5 w1 w2 w1 w2 w1
pat aabb 4 w0 w0 w0 w2
iso cbaac zxyyz
iso bca zzx
pat bbaab 5 w0 w2 w1 w1 w2
---
false
false
false
false
true
false
false
false
false
false
false
false
false
true
false
false
false
true
false
false
=== hidden
@gen 2402387504 big
=== hidden
@gen 2402387505 big
=== hidden
@gen 2402387506 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = []
for _ in range(20 if not big else 4):
    n = r.randint(1, 6) if not big else 300000
    if r.random() < 0.5:
        s = "".join(r.choice("abc") for _ in range(n)); t = "".join(r.choice("xyz") for _ in range(n + (r.random() < 0.1)))
        if r.random() < 0.4: t = s.translate(str.maketrans("abc", "".join(r.sample("xyz", 3))))
        out.append(f"iso {s} {t}")
    else:
        p = "".join(r.choice("ab" if not big else "abcdefgh") for _ in range(n))
        words = ["w" + str(r.randint(0, 2 if not big else 7)) for _ in range(n)]
        out.append(f"pat {p} {len(words)} " + " ".join(words))
print("\n".join(out))
```

## Hints
- Check both directions: letter → target and target → letter.
- A pair (a, b) is fine if both are unseen, or if a already maps to b **and** b maps back to a.
- Different lengths can never match.

## Solution
A one-to-one correspondence fails in two ways:

1. a letter maps to two different targets (`fwd` catches this);
2. two letters map to the same target (`bwd` catches this).

So record both directions. A pair is acceptable if it is new on **both** sides, or it is exactly the existing pairing on both sides.

For bytes, `array<int,256>` tables are the fastest perfect hash. For words, use `unordered_map<string,char>` in the reverse direction.

An equivalent trick: two sequences are isomorphic exactly when their **first-occurrence index sequences** match (`egg → 0 1 1`, `add → 0 1 1`). That's the canonical key from the grouping problem.

Complexity: O(n) (O(total word length) for the patterns).

```cpp
#include <bits/stdc++.h>
using namespace std;

bool isomorphic(const string& s, const string& t) {
    if (s.size() != t.size()) return false;
    array<int, 256> fwd, bwd;
    fwd.fill(-1); bwd.fill(-1);
    for (size_t i = 0; i < s.size(); ++i) {
        unsigned char a = s[i], b = t[i];
        if (fwd[a] == -1 && bwd[b] == -1) { fwd[a] = b; bwd[b] = a; }    // new pair on both sides
        else if (fwd[a] != b || bwd[b] != a) return false;               // conflicts in either direction
    }
    return true;
}

bool word_pattern(const string& p, const vector<string>& w) {
    if (p.size() != w.size()) return false;
    unordered_map<char, string> fwd;
    unordered_map<string, char> bwd;
    for (size_t i = 0; i < p.size(); ++i) {
        auto f = fwd.find(p[i]);
        auto b = bwd.find(w[i]);
        if (f == fwd.end() && b == bwd.end()) { fwd[p[i]] = w[i]; bwd[w[i]] = p[i]; }
        else if (f == fwd.end() || b == bwd.end() || f->second != w[i] || b->second != p[i]) return false;
    }
    return true;
}
```
