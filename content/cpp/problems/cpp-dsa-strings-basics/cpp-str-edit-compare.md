---
id: cpp-str-edit-compare
title: Backspace Compare and One Edit Away
difficulty: Medium
order: 6
tags: strings, two pointers, O(1) space, comparison
time_limit: 1
---
## Statement
```cpp
bool backspace_equal(const std::string& s, const std::string& t);
    // '#' deletes the previous character (if any); are the typed results equal?  O(1) extra memory
bool one_edit_away(const std::string& a, const std::string& b);
    // can a become b with EXACTLY one insert, delete or replace? (equal strings: false)
```

`"ab#c"` and `"ad#c"` both type `"ac"`, so they are equal. `"a#c"` and `"b"` are not.

- **Backspaces:** scan both strings **from the right**, keeping a "pending deletes" counter for each, to find the next character that survives. Compare the surviving characters pair by pair. Don't build the resulting strings.
- **One edit:** the lengths differ by at most 1. Walk both strings until the first mismatch. Then the rest must match exactly after skipping one character in the longer string (insert/delete), or one in each (replace).

**Input:** lines `bs s t` or `edit a b` (use `-` for an empty string). Lengths ≤ 10⁶.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool backspace_equal(const string& s, const string& t) { return s == t; }
bool one_edit_away(const string& a, const string& b) { return a.size() == b.size() && a != b; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd, a, b;
    while (cin >> cmd >> a >> b) {
        if (a == "-") a.clear();
        if (b == "-") b.clear();
        bool r = cmd == "bs" ? backspace_equal(a, b) : one_edit_away(a, b);
        cout << (r ? "true" : "false") << '\n';
    }
}
```

## Tests
=== sample
bs ab#c ad#c
bs ab## c#d#
bs a#c b
edit pale ple
edit pales pale
edit pale bale
edit pale bake
---
true
true
false
true
true
true
false
=== hidden
bs - -
bs ### -
bs a## -
bs bxj##tw bxo#j##tw
edit a a
edit - a
edit - ab
edit ab ba
---
true
true
true
true
false
true
false
false
=== hidden
bs bb b#
edit - -
bs a bbab#b
bs b#aba -
edit abbb abbb
edit b b
edit abb aabb
bs #b baa#aa
edit baab baab
edit baab baab
edit aaabab abaabab
bs ab#a#b a
edit b b
edit baa aa
edit - -
bs baa#ba -
bs a ababb
bs a#a #ba
bs aaaba a#aa
edit bbba babbb
---
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
true
false
false
false
false
false
false
=== hidden
edit aaabb aaabbb
bs b#a#a aaabb
edit - -
edit baaab baaab
bs bb ##a##a
bs b#ab#b #aa
bs abb#b -
bs #b## a
bs babb a
edit aaaba aaba
edit baaaaa baaaaa
edit abba aabba
bs #bb aaab
bs aa# -
edit ab ab
bs b b#aa#
edit bbbabb bbabb
bs - #bab
edit baabab baaba
bs ab #a#
---
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
true
false
false
false
false
true
false
true
false
=== hidden
bs #bb b
edit a ba
edit ab aab
bs - -
bs bab##b baa#
edit - -
edit ba a
edit aaab aab
bs - b#
edit baaab babaab
bs - bbbbb
edit aab aab
edit ababa ababaa
bs ab aa
bs - #bbba
edit bbaa bbaa
edit b b
bs ba#aa# bbbaaa
bs #ba#b b#a#a
bs b#b#a abbb
---
false
true
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
true
false
false
false
false
false
false
false
=== hidden
@gen 2269744059 big
=== hidden
@gen 2269744060 big
=== hidden
@gen 2269744061 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = []
for _ in range(20 if not big else 3):
    n = r.randint(0, 6) if not big else 500000
    if r.random() < 0.5:
        s = "".join(r.choice("ab#") for _ in range(n)) or "-"; t = "".join(r.choice("ab#") for _ in range(r.randint(0, 6) if not big else n)) or "-"
        out.append(f"bs {s} {t}")
    else:
        a = "".join(r.choice("ab") for _ in range(n))
        b = list(a); k = r.choice([0, 1, 1, 2])
        for _ in range(k):
            op = r.randrange(3)
            if op == 0: b.insert(r.randint(0, len(b)), r.choice("ab"))
            elif op == 1 and b: b.pop(r.randrange(len(b)))
            elif b: b[r.randrange(len(b))] = r.choice("ab")
        out.append(f"edit {a or '-'} {''.join(b) or '-'}")
print("\n".join(out))
```

## Hints
- A '#' deletes to its left, so scanning from the right lets you know whether each character survives. Keep a skip counter.
- Find the next surviving character in each string and compare them, until both are exhausted.
- One edit: make `a` the shorter string, skip the common prefix, then compare the remaining suffixes according to the length difference.

## Solution
**Backspaces from the right.** A `#` only affects characters to its **left**, so scanning right-to-left tells you immediately whether a character survives. Count the pending deletes, and skip characters while the count is positive. `next_kept` finds the next survivor in each string, and the two are compared one pair at a time. That's O(n) time and O(1) memory, without building either result.

**One edit.** Make `a` the shorter string. A length difference above 1 needs at least two edits. Skip the common prefix:

- **equal lengths:** one replace, so the suffixes after the mismatch must be equal (and there must *be* a mismatch);
- **lengths differ by one:** insert the extra character, so `a[i..]` must equal `b[i+1..]`.

`string::compare` with offsets checks a suffix without copying it.

Complexity: O(n) time, O(1) extra space for both.

```cpp
#include <bits/stdc++.h>
using namespace std;

static int next_kept(const string& s, int i) {        // index of the next surviving char at or before i, or -1
    int skip = 0;
    for (; i >= 0; --i) {
        if (s[i] == '#') ++skip;
        else if (skip > 0) --skip;                    // deleted by a later '#'
        else return i;
    }
    return -1;
}

bool backspace_equal(const string& s, const string& t) {
    int i = (int)s.size() - 1, j = (int)t.size() - 1;
    while (true) {
        i = next_kept(s, i); j = next_kept(t, j);
        if (i < 0 || j < 0) return i < 0 && j < 0;    // both exhausted at the same time?
        if (s[i] != t[j]) return false;
        --i; --j;
    }
}

bool one_edit_away(const string& a, const string& b) {
    if (a.size() > b.size()) return one_edit_away(b, a);       // ensure |a| <= |b|
    if (b.size() - a.size() > 1) return false;
    size_t i = 0;
    while (i < a.size() && a[i] == b[i]) ++i;                  // common prefix
    if (a.size() == b.size()) {                                // must be exactly one replace
        if (i == a.size()) return false;                       // identical
        return a.compare(i + 1, string::npos, b, i + 1, string::npos) == 0;
    }
    return a.compare(i, string::npos, b, i + 1, string::npos) == 0;   // insert b[i] into a
}
```
