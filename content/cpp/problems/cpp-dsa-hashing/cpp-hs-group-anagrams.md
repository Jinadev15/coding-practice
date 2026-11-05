---
id: cpp-hs-group-anagrams
title: Grouping by a Canonical Key
difficulty: Medium
order: 2
tags: hashing, grouping, canonical form, strings
time_limit: 1
---
## Statement
Group words that belong together. Each mode needs a different **canonical key**: a value that is equal exactly when two words belong to the same group.

```cpp
std::vector<std::vector<std::string>> group(const std::vector<std::string>& words, const std::string& mode);
```

- `anagram`: same letters with the same counts ("eat", "tea", "ate").
- `shift`: equal up to shifting every letter by the same amount, with wrap-around ("abc", "bcd", "xyz", "zab").
- `pattern`: the same repetition structure ("egg", "add", "foo" all share `abb`; "paper" and "title" share `abacd`).

**Output order (the driver relies on it):** inside each group, keep the input order. Order the groups by the input position of their **first** word.

**Input:** `mode n`, then `n` lowercase words (total length ≤ 10⁶), repeated until the end of input. The driver prints the number of groups, then each group on its own line (or the sizes only, for big inputs).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<vector<string>> group(const vector<string>& words, const string& mode) {
    vector<vector<string>> g;
    for (auto& w : words) g.push_back({w});        // every word alone
    return g;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string mode; int n;
    while (cin >> mode >> n) {
        vector<string> w(n);
        for (auto& x : w) cin >> x;
        auto g = group(w, mode);
        cout << g.size() << " groups\n";
        if (n <= 30) for (auto& grp : g) { for (size_t i = 0; i < grp.size(); ++i) cout << grp[i] << (i + 1 < grp.size() ? ' ' : '\n'); }
        else { long long h = 0; for (auto& grp : g) h = (h * 1000003 + grp.size()) % 998244353; cout << "sizes-hash " << h << '\n'; }
    }
}
```

## Tests
=== sample
anagram 6
eat tea tan ate nat bat
shift 6
abc bcd xyz zab az ba
pattern 5
egg add foo paper title
---
3 groups
eat tea ate
tan nat
bat
2 groups
abc bcd xyz zab
az ba
2 groups
egg add foo
paper title
=== hidden
anagram 1
a
shift 3
a z q
pattern 4
ab aa ba bb
anagram 4
ab ba abc cab
---
1 groups
a
1 groups
a z q
2 groups
ab ba
aa bb
2 groups
ab ba
abc cab
=== hidden
anagram 3
aa b baa
shift 10
cc bba abb bba ab ac cb c acb c
pattern 3
a bca b
---
3 groups
aa
b
baa
8 groups
cc
bba bba
abb
ab
ac
cb
c c
acb
2 groups
a b
bca
=== hidden
anagram 8
c c ab cb aa abb cb ba
shift 4
cab aab a ac
pattern 6
bcc ac cbc b ab b
---
5 groups
c c
ab ba
cb cb
aa
abb
4 groups
cab
aab
a
ac
4 groups
bcc
ac ab
cbc
b b
=== hidden
anagram 5
cc b aca a ca
shift 4
a aac cba b
pattern 6
ca c ca a a c
---
5 groups
cc
b
aca
a
ca
3 groups
a b
aac
cba
2 groups
ca ca
c a a c
=== hidden
@gen 660072958 big
=== hidden
@gen 660072959 big
=== hidden
@gen 660072960 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for mode in ["anagram", "shift", "pattern"]:
    n = r.randint(1, 10) if not big else 100000
    ws = ["".join(r.choice("abc" if not big else "abcdefgh") for _ in range(r.randint(1, 3 if not big else 6))) for _ in range(n)]
    print(mode, n); print(*ws)
```

## Hints
- Think about what stays the same within a group and changes between groups. That's the key.
- Anagram: letter counts. Shift: differences between consecutive letters, mod 26 (plus the length). Pattern: replace each letter by when it first appeared.
- Use `unordered_map<string,int>` from key to group index, and create groups in the order their first word appears.

## Solution
Grouping = "hash by a canonical key". The whole skill is designing the key:

- **Anagram:** letter counts. They're invariant under rearrangement and differ otherwise. Encoding 26 counts is O(L). Sorting the word also works, in O(L log L).
- **Shift:** shifting every letter by the same amount keeps the **differences between neighbouring letters** (mod 26 for the wrap-around). Prefix the length so that a one-letter word and the empty difference string don't collide with different lengths.
- **Pattern:** rename each letter by the order of its first appearance (`paper → abacd`). Two words share a structure exactly when their renamings are equal. This is the bijection idea in canonical form.

Mapping key → group index, in first-seen order, gives the required output order with no sorting.

Complexity: O(total length) expected (O(L log L) per word if you sort for anagrams).

```cpp
#include <bits/stdc++.h>
using namespace std;

static string key_of(const string& w, const string& mode) {
    if (mode == "anagram") {                       // 26 counts encoded as a string
        array<int, 26> c{};
        for (char ch : w) ++c[ch - 'a'];
        string k;
        for (int x : c) { k += to_string(x); k += ','; }
        return k;
    }
    if (mode == "shift") {                         // differences between neighbours, mod 26
        string k;
        for (size_t i = 1; i < w.size(); ++i) k += char('a' + (w[i] - w[i - 1] + 26) % 26);
        return to_string(w.size()) + ":" + k;
    }
    // pattern: replace each letter by the order of its first appearance
    array<int, 26> first; first.fill(-1);
    string k; int next = 0;
    for (char ch : w) {
        int& f = first[ch - 'a'];
        if (f < 0) f = next++;
        k += char('a' + f);
    }
    return k;
}

vector<vector<string>> group(const vector<string>& words, const string& mode) {
    unordered_map<string, int> gid;                // key -> group index (in first-seen order)
    vector<vector<string>> out;
    for (auto& w : words) {
        auto [it, fresh] = gid.try_emplace(key_of(w, mode), (int)out.size());
        if (fresh) out.emplace_back();
        out[it->second].push_back(w);
    }
    return out;
}
```
