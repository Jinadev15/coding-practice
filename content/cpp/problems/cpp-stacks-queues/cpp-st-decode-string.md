---
id: cpp-st-decode-string
title: Decode Nested Repetitions
difficulty: Medium
order: 7
tags: stack, nesting, strings, recursion to iteration
time_limit: 1
---
## Statement
```cpp
std::string decode(const std::string& s);
```

An encoded string uses `k[body]` to mean `body` repeated `k` times (1 ≤ k ≤ 999, possibly several digits). Bodies can nest and can be mixed with plain lowercase letters: `3[a2[bc]]` → `abcbcabcbcabcbc`, `2[ab]3[c]d` → `ababcccd`, `x10[]y` → `xy` (an empty body is allowed).

The input is valid and the decoded length is at most 10⁶.

**Input:** one encoded string per line until the end of input (encoded length ≤ 2·10⁵ per line). Print the decoded string (an empty result prints an empty line).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string decode(const string& s) {
    return s;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string s;
    while (cin >> s) cout << decode(s) << '\n';
}
```

## Tests
=== sample
3[a2[bc]]
2[ab]3[c]d
x10[]y
---
abcbcabcbcabcbc
ababcccd
xy
=== hidden
abc
1[1[1[z]]]
12[q]
2[a2[b2[c]]]d
---
abc
z
qqqqqqqqqqqq
abccbccabccbccd
=== hidden
c
4[2[caa]]4[]a
4[2[b]]3[b]
acbcca
bb4[baccac]
b
---
c
caacaacaacaacaacaacaacaaa
bbbbbbbbbbb
acbcca
bbbaccacbaccacbaccacbaccac
b
=== hidden
aaa4[a2[3[]b2[]]4[]]
cbaab4[3[3[]c]]
aaa3[aab]a
c
bab
bac1[b1[2[cb]]3[b]]
---
aaaabbabbabbabb
cbaabcccccccccccc
aaaaabaabaaba
c
bab
bacbcbcbbbb
=== hidden
3[baa]3[baa]
4[2[3[]]ca3[]]
c
aacb1[2[ac]abaa]
2[abcb]4[aa]2[c]
c
---
baabaabaabaabaabaa
cacacaca
c
aacbacacabaa
abcbabcbaaaaaaaacc
c
=== hidden
bacaaaaca8[11[acaaabcbc12[aaabacccbaaabacbbc6[8[babc2[cccbbab]1[b]]ba]baaa]]1[b]11[ac]c4[]11[]cab]2[8[]9[]9[]11[]ba9[]6[]8[]]8[]a
=== hidden
aacbbab7[abcbbaa6[11[6[12[baacab]1[9[acc]9[bac]12[bccabcaaaabcc]babcab5[aaacaccbbaacac]9[]]5[]9[]c2[]b]7[]]abab]7[ccbbbb11[ac]7[7[]8[]b]bb]bbaaac]10[]1[4[]9[]8[]1[b]]
=== hidden
1[5[cabbacacccb6[12[acbccaaacbaaaccbbabccba]]bcc9[caccb12[bbb3[10[ccaccabbccbaaaccacc]]12[7[aabccbbbbbcabab]]3[]1[ba]]10[a]5[]c]caabbb]]

## Hints
- When you meet `[`, the text you were building must be put aside until the matching `]`. What else must be remembered with it?
- Push `(text so far, k)` at `[` and start an empty string. At `]`, pop, and append the inner string `k` times to the popped text.
- Counts can have several digits: `k = k * 10 + d`. Reset `k` after pushing.

## Solution
The natural solution is recursive: decode the body, repeat it, continue. The stack version makes the recursion's saved state explicit. At each `[` you **suspend** the current level, exactly what a function call does with its local variables:

- `cur`: the text of the level being built,
- the stack: for every open `[`, the text that was built *before* it and the repeat count that goes with it.

At `]`, the inner level is complete: pop its parent, append `cur` `k` times, and that becomes the new `cur`.

```text
3[a2[bc]]
3[     push ("", 3)          cur ""
a      cur "a"
2[     push ("a", 2)         cur ""
bc     cur "bc"
]      pop ("a",2): cur = "a" + "bcbc" = "abcbc"
]      pop ("",3):  cur = "abcbcabcbcabcbc"
```

Counts can have several digits, so accumulate `k = 10k + digit`, and reset it at `[`. `std::move` avoids copying the saved strings.

Complexity: each `]` copies its result once into the parent, so the work is O(encoded length + decoded length × nesting depth) in the worst case, and O(output) in typical inputs.

```cpp
#include <bits/stdc++.h>
using namespace std;

string decode(const string& s) {
    vector<pair<string,int>> st;       // (text built before this '[', repeat count of this '[')
    string cur;                        // text of the innermost open level
    int k = 0;
    for (char c : s) {
        if (isdigit((unsigned char)c)) k = k * 10 + (c - '0');
        else if (c == '[') {
            st.push_back({std::move(cur), k});      // save the outer level, start a fresh one
            cur.clear(); k = 0;
        } else if (c == ']') {
            auto [outer, times] = std::move(st.back()); st.pop_back();
            outer.reserve(outer.size() + cur.size() * times);
            for (int i = 0; i < times; ++i) outer += cur;
            cur = std::move(outer);                 // the finished level becomes part of its parent
        } else cur += c;
    }
    return cur;
}
```
