---
id: cpp-str-palindromic-substrings
title: Longest and Counting Palindromic Substrings
difficulty: Medium
order: 2
tags: strings, palindromes, expand around center
time_limit: 1
---
## Statement
```cpp
std::pair<int,int> longest_palindrome(const std::string& s);   // {start, length}; leftmost on ties
long long count_palindromes(const std::string& s);              // palindromic substrings (by position)
```

`"babad"` gives `{0, 3}` ("bab", which comes before "aba"). `"aaa"` contains 6 palindromic substrings.

**Expand around centres.** There are `2n − 1` centres: every character (odd lengths) and every gap between neighbours (even lengths). Expanding from a centre while `s[l] == s[r]` finds every palindrome with that centre, so each successful step is one palindrome to count.

|s| ≤ 5000, so O(n²) is fine.

**Input:** one string per line (printable characters, no spaces).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> longest_palindrome(const string& s) { return {0, s.empty() ? 0 : 1}; }
long long count_palindromes(const string& s) { return (long long)s.size(); }
```

## Driver
```cpp
int main() {
    string s;
    while (cin >> s) {
        auto [st, len] = longest_palindrome(s);
        cout << st << ' ' << len << ' ' << s.substr(st, min(len, 40)) << ' ' << count_palindromes(s) << '\n';
    }
}
```

## Tests
=== sample
babad
cbbd
aaa
---
0 3 bab 7
1 2 bb 5
0 3 aaa 6
=== hidden
a
ab
racecar
abacdfgdcaba
---
0 1 a 1
0 1 a 2
0 7 racecar 10
0 3 aba 14
=== hidden
abbbabaabb
abbbbababaaa
bbabababbb
bbabbb
bababbbbbaaa
babbbbab
---
0 5 abbba 19
0 6 abbbba 28
0 9 bbabababb 24
0 5 bbabb 12
3 7 abbbbba 30
0 8 babbbbab 18
=== hidden
baabbbbaaabb
aaaabbabbbaa
babababbabbb
abbabaab
abbbaa
bbbbbbabbab
---
1 8 aabbbbaa 28
4 5 bbabb 27
0 7 bababab 29
0 4 abba 14
0 5 abbba 11
0 6 bbbbbb 32
=== hidden
bbabaababb
abbababb
abbbabaabb
babba
aabab
aababa
---
0 10 bbabaababb 21
1 7 bbababb 16
0 5 abbba 19
1 4 abba 8
1 3 aba 8
1 5 ababa 11
=== hidden
@gen 2477877967 big
=== hidden
@gen 2477877968 big
=== hidden
@gen 2477877969 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 12) if not big else 5000
    print("".join(r.choice("ab" if not big or r.random() < 0.5 else "a") for _ in range(n)))
```

## Hints
- A palindrome mirrors around its centre, which is a character or a gap. There are 2n − 1 centres.
- From each centre, expand while the characters at `l` and `r` match. Each match is one more palindrome.
- Track the longest (start, length), preferring the smaller start on ties.

## Solution
**Every palindrome has a unique centre:** a character for odd lengths, a gap for even lengths. Expanding from each of the `2n − 1` centres while the end characters match visits every palindromic substring exactly once. So counting the successful steps counts them all, and the last successful step from each centre is the longest palindrome with that centre.

Encoding both kinds of centre as `c = 0..2n−2` (`l = c/2`, `r = l + c%2`) avoids two separate loops.

**Ties:** compare the start index explicitly. Expanding centres from left to right doesn't guarantee that equal-length palindromes are found in order of their start.

Complexity: O(n²) worst case (all equal characters), O(1) extra space. Manacher's algorithm achieves O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> longest_palindrome(const string& s) {
    int n = s.size(), bestL = 0, bestLen = n ? 1 : 0;
    auto expand = [&](int l, int r) {
        while (l >= 0 && r < n && s[l] == s[r]) { --l; ++r; }
        int len = r - l - 1;                                // the loop overshoots by one on each side
        if (len > bestLen || (len == bestLen && l + 1 < bestL)) { bestLen = len; bestL = l + 1; }
    };
    for (int c = 0; c < n; ++c) { expand(c, c); expand(c, c + 1); }
    return {bestL, bestLen};
}

long long count_palindromes(const string& s) {
    int n = s.size(); long long cnt = 0;
    for (int c = 0; c < 2 * n - 1; ++c) {                   // centre c: chars at c/2 and c/2 + c%2
        int l = c / 2, r = l + c % 2;
        while (l >= 0 && r < n && s[l] == s[r]) { ++cnt; --l; ++r; }
    }
    return cnt;
}
```
