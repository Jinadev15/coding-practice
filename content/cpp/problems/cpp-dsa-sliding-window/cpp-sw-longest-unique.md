---
id: cpp-sw-longest-unique
title: Longest Substring Without Repeating Characters
difficulty: Medium
order: 2
tags: sliding window, strings, frequency array, hashing
time_limit: 2
---
## Statement
```cpp
std::pair<int,int> longest_unique(const std::string& s);
    // {length, start} of the longest substring with all-distinct characters; leftmost on ties
```

`"abcabcbb"` gives `{3, 0}` ("abc"), `"pwwkew"` gives `{3, 2}` ("wke"), and `""` gives `{0, 0}`.

Grow the window with `R`. While the new character already occurs in the window, shrink from the left. The characters are any bytes with codes 33–126.

**Bonus technique (optional):** instead of shrinking one step at a time, store the **last index** of each character and jump `L` directly past the previous occurrence: `L = max(L, last[c] + 1)`.

**Input:** one string per line (n ≤ 10⁶). Print the length, the start, and the substring itself if it is at most 40 characters long.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> longest_unique(const string& s) {
    return {0, 0};
}
```

## Driver
```cpp
int main() {
    string s;
    while (getline(cin, s)) {
        if (!s.empty() && s.back() == '\r') s.pop_back();
        auto [len, st] = longest_unique(s);
        cout << len << ' ' << st;
        if (len <= 40) cout << " \"" << s.substr(st, len) << '"';
        cout << '\n';
    }
}
```

## Tests
=== sample
abcabcbb
bbbbb
pwwkew
---
3 0 "abc"
1 0 "b"
3 2 "wke"
=== hidden
a
abba
dvdf
tmmzuxt
---
1 0 "a"
2 0 "ab"
3 1 "vdf"
5 2 "mzuxt"
=== hidden
cbaab!cbda
aba!!aa!!!bc
bacaca!b
!c!!bd
!acda!!a!!ddddb
ccaa
bbdaa!!b!!bc!
c
---
5 5 "!cbda"
3 1 "ba!"
4 4 "ca!b"
3 3 "!bd"
4 0 "!acd"
2 1 "ca"
3 1 "bda"
1 0 "c"
=== hidden
!!bb
bcaacacba
ddd!!b
adcda!ddbcbaa
!ccbc!aadb!
bbdaaa!b!!
bbda!!
bbdb!ba!dd!dbd
---
2 1 "!b"
3 0 "bca"
2 2 "d!"
4 2 "cda!"
4 3 "bc!a"
3 1 "bda"
4 1 "bda!"
4 5 "ba!d"
=== hidden
!c!!cdccdb
b!dccc!adb
bc!d!acdacac!dd
!cdbcca
badddc
c
b
db!!c!bd!!
---
3 3 "!cd"
5 5 "c!adb"
4 0 "bc!d"
4 0 "!cdb"
3 0 "bad"
1 0 "c"
1 0 "b"
4 4 "c!bd"
=== hidden
@gen 1484260888 big
=== hidden
@gen 1484260889 big
=== hidden
@gen 1484260890 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    for _ in range(8): print("".join(r.choice("abcd!") for _ in range(r.randint(1, 15))))
else:
    print("".join(chr(r.randint(33, 126)) for _ in range(1000000)))
    print("".join(r.choice("ab") for _ in range(1000000)))
```

## Hints
- Maintain a window `[L, R]` with no repeated characters. Extend `R` one step at a time.
- If `s[R]` already occurs inside the window, the window must start after that earlier occurrence.
- Store the last index of every character (an array of 256 ints). Only jump if that index is `≥ L`.

## Solution
**Invariant:** `s[L..R]` has no repeated character.

When `s[R]` was last seen at index `p ≥ L`, the window now contains it twice, and every window that starts at or before `p` would keep both copies. So the new left edge must be `p + 1`. Storing the last index of every byte makes this a jump instead of a step-by-step shrink.

`last[c] >= L` matters: a stale occurrence *before* the window must not move `L` backwards.

Recording only strictly longer windows (`>`) keeps the **leftmost** answer on ties.

Complexity: O(n) time, O(alphabet) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> longest_unique(const string& s) {
    array<int, 256> last;
    last.fill(-1);                                   // last index where each byte was seen
    int best = 0, start = 0, L = 0;
    for (int R = 0; R < (int)s.size(); ++R) {
        unsigned char c = s[R];
        if (last[c] >= L) L = last[c] + 1;           // jump past the previous copy inside the window
        last[c] = R;
        if (R - L + 1 > best) { best = R - L + 1; start = L; }
    }
    return {best, start};
}
```
