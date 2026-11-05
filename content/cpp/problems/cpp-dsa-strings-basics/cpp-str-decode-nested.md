---
id: cpp-str-decode-nested
title: Decoding Nested Repetitions
difficulty: Medium
order: 4
tags: strings, stack, recursion, parsing
time_limit: 1
---
## Statement
An encoded string uses `k[...]` to mean "the text inside the brackets, repeated k times". Brackets can nest:

- `3[a]2[bc]` decodes to `aaabcbc`
- `3[a2[c]]` decodes to `accaccacc`
- `2[abc]3[cd]ef` decodes to `abcabccdcdcdef`

```cpp
std::string decode(const std::string& s);           // the full decoded string
long long decoded_length(const std::string& s);     // its length, WITHOUT building it (can be up to 10^18)
```

`k` is a positive integer of up to 9 digits, and letters are lowercase. The input is always valid.

- **Decode** with a stack (push the current text and `k` at `[`, then pop and combine at `]`) or with recursion. The tests keep the decoded output below 10⁶ characters.
- **Length** only: compute lengths instead of strings, the same way. Use `long long`. The answer fits.

**Input:** one encoded string per line (length ≤ 10⁵). Print the length, then the decoded text if it is at most 60 characters long (otherwise `...`).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string decode(const string& s) { string r; for (char c : s) if (isalpha((unsigned char)c)) r += c; return r; }
long long decoded_length(const string& s) { return (long long)decode(s).size(); }
```

## Driver
```cpp
int main() {
    string s;
    while (cin >> s) {
        long long len = decoded_length(s);
        cout << len << ' ';
        if (len <= 60) cout << decode(s) << '\n'; else cout << "...\n";
    }
}
```

## Tests
=== sample
3[a]2[bc]
3[a2[c]]
2[abc]3[cd]ef
---
7 aaabcbc
9 accaccacc
14 abcabccdcdcdef
=== hidden
a
1[a]
10[a]
2[2[2[2[b]]]]
100000000[a]
2[ab3[c]]d
---
1 a
1 a
10 aaaaaaaaaa
16 bbbbbbbbbbbbbbbb
100000000 ...
11 abcccabcccd
=== hidden
cbca
b
b
1[3[2[bbcb]c]]
2[bbcaab]cc
bcaab
---
4 cbca
1 b
1 b
27 bbcbbbcbcbbcbbbcbcbbcbbbcbc
14 bbcaabbbcaabcc
5 bcaab
=== hidden
baa
1[2[acba]cb3[cab2[aabcc]c]]
acbb
3[2[cbccaba]2[cb]]2[abbbb3[2[bbacba]]]cca
acaca
aaab
---
3 baa
52 acbaacbacbcabaabccaabccccabaabccaabccccabaabccaabccc
4 acbb
139 ...
5 acaca
4 aaab
=== hidden
abc1[bbcac]b
3[2[cac]cbc]2[3[bbbcccac]baa3[c]]aa
2[bba1[2[cc]3[a]aac]2[1[bbbbb]2[abcca]]]
acc1[2[3[caabbaab]b]1[3[caa]bc]ba]
a3[3[aac1[caabc]1[aabb]]aa]aaa
ab
---
9 abcbbcacb
89 ...
86 ...
66 ...
118 ...
2 ab
=== hidden
a7[ab1[acc]8[bbbaaa]]2[7[3[acaaab2[ac]]7[6[babbca]aa]]9[6[cbcabc]cbb]8[baaa]]
cbab
5[9[aa]3[2[5[a]1[caa]]]]
---
5282 ...
4 cbab
330 ...
=== hidden
acc
cb4[3[8[cb2[bcb]ccb]]3[5[aaca6[aab]]]]aab
a8[ca6[9[8[aaca]]]cba]c
---
3 acc
2381 ...
13866 ...
=== hidden
bbc
ba
6[cb]8[5[cbba]]cc
---
3 bbc
2 ba
174 ...

## Hints
- Use a stack of (text so far, repeat count). Push at `[` and start a new string.
- At `]`, pop, repeat the current string k times, and append it to the popped text.
- For the length only, run the same algorithm on numbers: a letter adds 1, and `]` gives `prev + inner·k`.

## Solution
**The stack mirrors the nesting.** At `[`, the text built so far and the pending repeat count are saved, and a fresh inner text starts. At `]`, the inner text is repeated and appended to the saved outer text, which becomes the current text again. Digits accumulate into `k` (counts can have several digits).

**Length without building.** Exactly the same structure, but each "text" is replaced by its length: a letter adds 1, and `]` computes `prev + inner × k`. This works even when the decoded string would be astronomically long. It shows how to compute *properties* of a recursive structure without materialising it, like the Hanoi k-th move.

A recursive-descent version (`parse()` reads letters and `k[parse()]` groups until `]`) is equally good.

Complexity: O(input + output) for decoding, O(input) for the length.

```cpp
#include <bits/stdc++.h>
using namespace std;

string decode(const string& s) {
    vector<pair<string, long long>> st;          // (text before '[', repeat count)
    string cur; long long k = 0;
    for (char c : s) {
        if (isdigit((unsigned char)c)) k = k * 10 + (c - '0');
        else if (c == '[') { st.push_back({cur, k}); cur.clear(); k = 0; }
        else if (c == ']') {
            auto [prev, times] = st.back(); st.pop_back();
            string rep; rep.reserve(prev.size() + cur.size() * times);
            rep = prev;
            for (long long t = 0; t < times; ++t) rep += cur;
            cur = std::move(rep);
        } else cur += c;
    }
    return cur;
}

long long decoded_length(const string& s) {
    vector<pair<long long, long long>> st;       // (length before '[', repeat count)
    long long cur = 0, k = 0;
    for (char c : s) {
        if (isdigit((unsigned char)c)) k = k * 10 + (c - '0');
        else if (c == '[') { st.push_back({cur, k}); cur = 0; k = 0; }
        else if (c == ']') { auto [prev, times] = st.back(); st.pop_back(); cur = prev + cur * times; }
        else ++cur;
    }
    return cur;
}
```
