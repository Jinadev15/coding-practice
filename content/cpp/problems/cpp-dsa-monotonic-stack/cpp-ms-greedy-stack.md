---
id: cpp-ms-greedy-stack
title: Greedy Stacks - Remove K Digits and Smallest Distinct Subsequence
difficulty: Medium
order: 7
tags: monotonic stack, greedy, lexicographic order, strings
time_limit: 1
---
## Statement
```cpp
std::string remove_k_digits(const std::string& num, int k);
    // delete exactly k digits from num (keeping the order of the rest) so the result is the
    // SMALLEST number; strip leading zeros; an empty result is "0"
std::string smallest_distinct_subsequence(const std::string& s);
    // the lexicographically smallest subsequence of s that contains every distinct letter of s
    // exactly once
```

- `remove_k_digits("1432219", 3)` = `"1219"`; `("10200", 1)` = `"200"`; `("10", 2)` = `"0"`.
- `smallest_distinct_subsequence("cbacdcbc")` = `"acdb"`; `("bcabc")` = `"abc"`.

Both run in **O(n)**.

**Input:** commands until the end of input:

- `rk num k`: num is 1..10⁶ digits (it may start with `0`), 0 ≤ k ≤ |num|,
- `sd s`: s is 1..10⁶ lowercase letters.

Print one result per line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string remove_k_digits(const string& num, int k) {
    return num;
}
string smallest_distinct_subsequence(const string& s) {
    return s;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd, s;
    while (cin >> cmd >> s) {
        if (cmd == "rk") { int k; cin >> k; cout << remove_k_digits(s, k) << '\n'; }
        else cout << smallest_distinct_subsequence(s) << '\n';
    }
}
```

## Tests
=== sample
rk 1432219 3
rk 10200 1
rk 10 2
sd cbacdcbc
sd bcabc
---
1219
200
0
acdb
abc
=== hidden
rk 9 0
rk 9 1
rk 112 1
rk 0000 2
rk 123456 2
rk 654321 3
sd a
sd zyxzyx
sd abacb
---
9
0
11
0
1234
321
a
xzy
abc
=== hidden
sd a
rk 9089 0
sd aaaaaaaa
rk 07 1
sd ababbabbaa
sd bb
---
a
9089
a
0
ab
b
=== hidden
sd aaaaa
sd bbbababcbc
sd aacccbaaba
rk 090 0
sd aaaaaaaaaaa
sd bbbaaccb
---
a
abc
acb
90
a
acb
=== hidden
sd abbb
rk 0019024908 0
rk 38 1
rk 2156476701 4
sd acd
sd aaaababa
---
ab
19024908
3
146701
acd
ab
=== hidden
@gen 2337975417 big
=== hidden
@gen 2337975418 big
=== hidden
@gen 2337975419 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    if r.random() < 0.5:
        n = r.randint(1, 12) if not big else 1000000
        num = "".join(r.choice("0123456789" if r.random() < 0.7 else "019") for _ in range(n))
        print("rk", num, r.randint(0, n))
    else:
        n = r.randint(1, 12) if not big else 1000000
        alpha = "abcdefghijklmnopqrstuvwxyz"[:r.randint(1, 5 if not big else 26)]
        print("sd", "".join(r.choice(alpha) for _ in range(n)))
```

## Hints
- A digit followed by a smaller digit should be deleted first. Scan left to right and pop bigger digits from a stack while `k > 0`.
- Leftover deletions come off the end, then strip leading zeros (empty means "0").
- For the distinct version, pop the top only if it is bigger and occurs again later; skip letters already on the stack.

## Solution
**Remove k digits.** Earlier digits matter more. If some digit is followed by a **smaller** digit, deleting the bigger one makes the number smaller, and that is the best possible use of a deletion at that position. So scan left to right with a stack: while you still may delete and the top is bigger than the incoming digit, pop it. The stack stays non-decreasing.

```text
1432219, k=3
1     [1]
4     [1 4]
3     4>3 pop (k=2)  [1 3]
2     3>2 pop (k=1)  [1 2]
2     [1 2 2]
1     2>1 pop (k=0)  [1 2 1]
9     [1 2 1 9]  -> "1219"
```

If deletions remain at the end, the stack is non-decreasing, so the largest digits are at the end: cut them. Then strip leading zeros.

**Smallest distinct subsequence.** Same idea with one extra constraint: a letter may be popped only if it **appears again later** (otherwise the result would lose it). Precompute the last occurrence of each letter, and skip letters already in the stack: the copy already placed is at an earlier, better position.

```text
cbacdcbc
c  [c]
b  c>b and c appears later: pop   [b]
a  b>a, b later: pop              [a]
c  [a c]
d  [a c d]
c  already in: skip
b  d>b but no d later: keep       [a c d b]
c  skip                           -> acdb
```

Both are O(n): every character is pushed and popped at most once.

```cpp
#include <bits/stdc++.h>
using namespace std;

string remove_k_digits(const string& num, int k) {
    string st;                                     // a string used as a stack: digits non-decreasing
    st.reserve(num.size());
    for (char c : num) {
        while (k > 0 && !st.empty() && st.back() > c) { st.pop_back(); --k; }   // a bigger digit before a smaller one: drop it
        st.push_back(c);
    }
    st.resize(st.size() - k);                      // still owe deletions: cut from the (largest) end
    size_t z = st.find_first_not_of('0');
    return z == string::npos ? "0" : st.substr(z);
}

string smallest_distinct_subsequence(const string& s) {
    array<int, 26> last{};
    for (int i = 0; i < (int)s.size(); ++i) last[s[i] - 'a'] = i;
    array<bool, 26> in{};
    string st;
    for (int i = 0; i < (int)s.size(); ++i) {
        int c = s[i] - 'a';
        if (in[c]) continue;                       // already placed, at a better (earlier) position
        while (!st.empty() && st.back() > s[i] && last[st.back() - 'a'] > i) {   // it reappears later
            in[st.back() - 'a'] = false;
            st.pop_back();
        }
        st.push_back(s[i]);
        in[c] = true;
    }
    return st;
}
```
