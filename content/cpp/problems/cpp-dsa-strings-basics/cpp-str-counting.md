---
id: cpp-str-counting
title: Counting Letters: Anagrams and Ransom Notes
difficulty: Easy
order: 1
tags: strings, frequency counting, anagrams
time_limit: 2
---
## Statement
Lowercase letters only.

```cpp
bool is_anagram(const std::string& a, const std::string& b);
bool can_construct(const std::string& note, const std::string& magazine);   // each magazine letter used at most once
int min_steps_to_anagram(const std::string& s, const std::string& t);
    // |s| == |t|: fewest characters of t to REPLACE so that t becomes an anagram of s
```

All three compare **26-entry frequency arrays**. For the last one: after counting, every letter that `t` has in excess must be replaced, so the answer is the sum of the positive differences `cnt_t[c] − cnt_s[c]`.

**Input:** lines `ana a b`, `ransom note magazine` or `steps s t`, until the end of input (lengths ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool is_anagram(const string& a, const string& b) { return a.size() == b.size(); }
bool can_construct(const string& note, const string& magazine) { return note.size() <= magazine.size(); }
int min_steps_to_anagram(const string& s, const string& t) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd, a, b;
    while (cin >> cmd >> a >> b) {
        if (cmd == "ana") cout << (is_anagram(a, b) ? "true" : "false") << '\n';
        else if (cmd == "ransom") cout << (can_construct(a, b) ? "true" : "false") << '\n';
        else cout << min_steps_to_anagram(a, b) << '\n';
    }
}
```

## Tests
=== sample
ana anagram nagaram
ana rat car
ransom aa aab
ransom aa ab
steps bab aba
steps leetcode practice
---
true
false
true
false
1
5
=== hidden
ana a a
ana a ab
ransom a b
steps abc abc
steps aaa bbb
---
true
false
false
0
3
=== hidden
ransom abcccabc aa
steps b a
steps abbccc cbcbcc
steps aaaacac bcbccba
ana acaaabb cbc
ransom accb cbbbcca
ana ba ab
ransom baaabb ac
ana cbaaacb abcabca
ana baaab ababa
ransom aabcaa cacabacbb
ana b b
ana bbaccabc cbbcbbc
ransom b b
steps cacbb accac
---
false
1
1
4
false
true
true
false
true
true
false
true
false
true
2
=== hidden
ransom bacc accbabc
ransom aaab bcc
ransom a ac
ransom cba bbbaac
ransom acb accbbb
ana cac cca
steps cbbccc cbbabb
steps baaaccab bbcbbaaa
ana ca ac
ana ccbcbbab abcbcbcb
ransom abacacbc caacab
steps ccccbb aacbbb
ana aaaaaab abab
ransom caaaab aabbc
ana abcbab ca
---
true
false
true
true
true
true
3
2
true
true
false
3
false
false
false
=== hidden
ana cba acbb
ransom bbbcabab abbbabaaba
ransom cabccbab cacbccccbc
steps acc ccb
steps accaaaca abbcbabb
ana a a
ransom ccbac caa
steps cabc baac
ana c cbc
ana baccbab cbaba
ransom bacabb ab
steps cba acb
steps cbaab aabcc
ransom aab cabcbb
ransom aaacbbab bcbc
---
false
false
false
1
5
true
false
1
false
false
false
0
1
false
false
=== hidden
@gen 992160560 big
=== hidden
@gen 992160561 big
=== hidden
@gen 992160562 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = []
for _ in range(15 if not big else 3):
    n = r.randint(1, 8) if not big else 1000000
    cmd = r.choice(["ana", "ransom", "steps"])
    a = "".join(r.choice("abc") for _ in range(n))
    if cmd == "steps": b = "".join(r.choice("abc") for _ in range(n))
    elif cmd == "ana" and r.random() < 0.5: b = "".join(r.sample(a, len(a)))
    else: b = "".join(r.choice("abc") for _ in range(r.randint(1, n + 3)))
    out.append(f"{cmd} {a} {b}")
print("\n".join(out))
```

## Hints
- Count the letters with `array<int,26>`, using `ch − 'a'` as the index.
- Increment for the first string and decrement for the second. A negative count reveals a surplus.
- For the replacements, sum the positive differences between the two count arrays.

## Solution
Two strings are anagrams exactly when their letter multisets are equal, and a 26-entry array is the multiset. Counting **up** with one string and **down** with the other means a single array suffices. A negative count means the second string used a letter more often than the first.

For the replacement count, the total excess of `t` equals the total shortage, because the lengths are equal. Every excess letter of `t` must be replaced by a missing one, and that is also enough.

Complexity: O(n) time, O(1) space (26 counters).

```cpp
#include <bits/stdc++.h>
using namespace std;

bool is_anagram(const string& a, const string& b) {
    if (a.size() != b.size()) return false;
    array<int, 26> c{};
    for (char ch : a) ++c[ch - 'a'];
    for (char ch : b) if (--c[ch - 'a'] < 0) return false;    // b has more of ch than a
    return true;
}

bool can_construct(const string& note, const string& magazine) {
    array<int, 26> avail{};
    for (char ch : magazine) ++avail[ch - 'a'];
    for (char ch : note) if (--avail[ch - 'a'] < 0) return false;
    return true;
}

int min_steps_to_anagram(const string& s, const string& t) {
    array<int, 26> c{};
    for (char ch : s) ++c[ch - 'a'];
    for (char ch : t) --c[ch - 'a'];
    int steps = 0;
    for (int x : c) if (x > 0) steps += x;    // letters s needs that t lacks = letters t has in excess
    return steps;
}
```
