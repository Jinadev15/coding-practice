---
id: cpp-super-digit
title: Super Digit
difficulty: Easy
order: 1
tags: recursion, digit sum, math
time_limit: 1
---
## Statement
The **super digit** of a number is defined recursively:

- a single digit is its own super digit;
- otherwise, the super digit of `x` is the super digit of the sum of `x`'s digits.

For example, `9875 → 9+8+7+5 = 29 → 2+9 = 11 → 1+1 = 2`.

Given a number `n` as a string (up to 10⁵ digits) and a count `k` (up to 10⁹), find the super digit of the number formed by writing `n` **k times in a row**.

```cpp
int super_digit(const std::string& n, long long k);
```

You can't build the repeated string, because it could have 10¹⁴ digits. Use the fact that the digit sum of `n` repeated `k` times is `k × digitsum(n)`, then recurse on that number.

**Input:** `t`, then `t` lines `n k`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int super_digit(const string& n, long long k) {
    return 0;
}
```

## Driver
```cpp
int main() {
    int t; cin >> t;
    while (t--) {
        string n; long long k;
        cin >> n >> k;
        cout << super_digit(n, k) << '\n';
    }
}
```

## Tests
=== sample
3
9875 4
148 3
0 1
---
8
3
0
=== hidden
4
7 1
9 1000000000
123 1000000000
99999999999999999999 999999999
---
7
9
6
9
=== hidden
20
9607947 11
7334345 12
93050010 8
2 12
26 18
6938 14
586326 1
29706 20
548393 12
24822280 6
7975565 12
59836 28
3375038 5
7 27
13946504 12
883 10
80507 6
3 10
7603360 19
61 18
---
3
6
9
6
9
4
3
3
6
6
6
4
1
9
6
1
3
3
7
9
=== hidden
20
7439 20
89047 18
795 27
8 29
355099 18
79 30
5124 17
24 4
56286 9
913107 21
45 17
28745466 1
1895333 13
599 12
41371344 7
6 7
6390052 24
282 23
4121 11
5 7
---
1
9
9
7
9
3
6
6
9
9
9
6
2
6
9
6
6
6
7
8
=== hidden
20
84 6
5 13
2 21
935 11
17441423 6
16 9
736201 21
7065533 26
349615 5
984 10
89074 29
49325918 15
147174 19
480 10
5 14
9580040 5
470 13
5 5
2 1
1 22
---
9
2
6
7
3
9
3
7
5
3
2
3
6
3
7
4
8
7
2
4
=== hidden
@gen 1997127314 big
=== hidden
@gen 1997127315 big
=== hidden
@gen 1997127316 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
t = 20; print(t)
for _ in range(t):
    if sys.argv[2] == "small":
        print(str(r.randint(1, 10**r.randint(1, 8))), r.randint(1, 30))
    else:
        print("".join(r.choice("0123456789") for _ in range(5000)).lstrip("0") or "7", r.randint(1, 10**9))
```

## Hints
- Don't build the repeated string. What is the digit sum of `n` written `k` times?
- After the first step you have an ordinary `long long`. Write a recursive `super_of(x)` with base case `x < 10`.
- Check the overflow bound: 10⁵ digits × 9 × 10⁹ is still below 9.2·10¹⁸.

## Solution
The digit sum of the concatenation is `k · digitsum(n)`, because every copy contributes the same digits. That number is at most 9·10⁵ · 10⁹ < 10¹⁵, so it fits in a `long long`, and from there ordinary recursion on the digit sum finishes in a handful of calls. Each call shrinks the number to at most `9 × (number of digits)`.

(Shortcut, for comparison: the super digit is `1 + (x − 1) mod 9` for `x > 0`, the "digital root". The recursive version is the point of this exercise.)

Complexity: O(|n|) to sum the digits, then O(log x) per recursive step, with only a few steps.

```cpp
#include <bits/stdc++.h>
using namespace std;

static int super_of(long long x) {                 // recursion on an ordinary number
    if (x < 10) return (int)x;                     // base case: a single digit
    long long s = 0;
    while (x > 0) { s += x % 10; x /= 10; }
    return super_of(s);                            // the problem shrinks quickly
}

int super_digit(const string& n, long long k) {
    long long s = 0;
    for (char c : n) s += c - '0';                 // at most 9·10^5
    return super_of(s * k);                        // at most 9·10^14: fits in long long
}
```
