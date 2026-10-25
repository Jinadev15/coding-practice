---
id: cpp-master-theorem
title: Master Theorem Classifier
difficulty: Easy
order: 1
tags: complexity, recurrences, master theorem
time_limit: 1
---
## Statement
Divide-and-conquer algorithms have running times of the form

**T(n) = a · T(n / b) + Θ(n^d)**

where `a ≥ 1` is the number of subproblems, `b ≥ 2` is how much smaller each one is, and `n^d` is the work done outside the recursive calls.

Implement

```cpp
std::string master(long long a, long long b, int d);
```

It returns the case number and the tight bound, in exactly this format:

| Situation | Output |
|---|---|
| d < log_b a | `case 1: Theta(n^K)`, where K = log_b a. Print K as an integer if it is one, otherwise with exactly 3 decimals (e.g. `n^1.585`). Write `n^1` as `n`. |
| d = log_b a | `case 2: Theta(n^d log n)`. Write it as `Theta(log n)` when d = 0 and `Theta(n log n)` when d = 1. |
| d > log_b a | `case 3: Theta(n^d)`, written as `Theta(n)` when d = 1. |

Compare `d` with `log_b a` **exactly**, using integers (`b^d` vs `a`), never with floating point.

**Input:** a number `t`, then `t` lines `a b d` with 1 ≤ a ≤ 10⁹, 2 ≤ b ≤ 10, 0 ≤ d ≤ 9. Print one line per recurrence.

**Example:** merge sort (`2 2 1`) prints `case 2: Theta(n log n)`, and Karatsuba (`3 2 1`) prints `case 1: Theta(n^1.585)`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string master(long long a, long long b, int d) {
    // compare b^d with a, then build the answer string
    return "";
}
```

## Driver
```cpp
int main() {
    int t; cin >> t;
    while (t--) {
        long long a, b; int d;
        cin >> a >> b >> d;
        cout << master(a, b, d) << '\n';
    }
}
```

## Tests
=== sample
4
2 2 1
3 2 1
1 2 0
2 2 2
---
case 2: Theta(n log n)
case 1: Theta(n^1.585)
case 2: Theta(log n)
case 3: Theta(n^2)
=== hidden
9
4 2 1
8 2 2
8 2 3
7 2 2
1 3 0
1 10 2
9 3 2
16 4 2
1000000000 10 9
---
case 1: Theta(n^2)
case 1: Theta(n^3)
case 2: Theta(n^3 log n)
case 1: Theta(n^2.807)
case 2: Theta(log n)
case 3: Theta(n^2)
case 2: Theta(n^2 log n)
case 2: Theta(n^2 log n)
case 2: Theta(n^9 log n)
=== hidden
6
5 3 1
27 3 3
27 3 2
64 4 3
2 10 0
100 10 1
---
case 1: Theta(n^1.465)
case 2: Theta(n^3 log n)
case 1: Theta(n^3)
case 2: Theta(n^3 log n)
case 1: Theta(n^0.301)
case 1: Theta(n^2)
=== hidden
30
716742 9 4
717879 5 3
9 3 0
4096 4 6
256 4 2
904114 4 5
392234 7 1
1 6 0
904075 8 4
458569 9 1
64 8 2
1 7 4
178011 8 1
8 2 3
101498 4 4
512 8 1
269451 3 1
283626 5 5
1 10 5
32 2 5
1024 4 1
147516 7 0
81 3 4
300692 5 0
714994 2 3
103795 4 3
109695 8 5
949141 10 1
963326 8 1
4096 4 3
---
case 1: Theta(n^6.136)
case 1: Theta(n^8.378)
case 1: Theta(n^2)
case 2: Theta(n^6 log n)
case 1: Theta(n^4)
case 1: Theta(n^9.893)
case 1: Theta(n^6.619)
case 2: Theta(log n)
case 1: Theta(n^6.595)
case 1: Theta(n^5.933)
case 2: Theta(n^2 log n)
case 3: Theta(n^4)
case 1: Theta(n^5.814)
case 2: Theta(n^3 log n)
case 1: Theta(n^8.316)
case 1: Theta(n^3)
case 1: Theta(n^11.382)
case 1: Theta(n^7.801)
case 3: Theta(n^5)
case 2: Theta(n^5 log n)
case 1: Theta(n^5)
case 1: Theta(n^6.116)
case 2: Theta(n^4 log n)
case 1: Theta(n^7.837)
case 1: Theta(n^19.448)
case 1: Theta(n^8.332)
case 1: Theta(n^5.581)
case 1: Theta(n^5.977)
case 1: Theta(n^6.626)
case 1: Theta(n^6)
=== hidden
30
476536 8 3
998243 4 5
486371 4 5
270463 4 0
375655 8 2
969449 8 4
49422 4 4
542800 2 6
611394 10 5
6561 9 4
236029 8 2
313568 6 3
321443 10 6
1000 10 3
910488 8 3
18788 2 5
817787 6 3
402995 4 4
100000 10 2
779642 10 5
100000 10 5
15625 5 6
2401 7 4
163670 7 1
6561 9 2
4096 8 0
64 4 2
294575 4 1
81 9 1
216 6 2
---
case 1: Theta(n^6.287)
case 1: Theta(n^9.965)
case 1: Theta(n^9.446)
case 1: Theta(n^9.023)
case 1: Theta(n^6.173)
case 1: Theta(n^6.629)
case 1: Theta(n^7.796)
case 1: Theta(n^19.050)
case 1: Theta(n^5.786)
case 2: Theta(n^4 log n)
case 1: Theta(n^5.950)
case 1: Theta(n^7.063)
case 3: Theta(n^6)
case 2: Theta(n^3 log n)
case 1: Theta(n^6.599)
case 1: Theta(n^14.198)
case 1: Theta(n^7.598)
case 1: Theta(n^9.310)
case 1: Theta(n^5)
case 1: Theta(n^5.892)
case 2: Theta(n^5 log n)
case 2: Theta(n^6 log n)
case 2: Theta(n^4 log n)
case 1: Theta(n^6.170)
case 1: Theta(n^4)
case 1: Theta(n^4)
case 1: Theta(n^3)
case 1: Theta(n^9.084)
case 1: Theta(n^2)
case 1: Theta(n^3)
=== hidden
30
772774 7 6
2 2 3
3125 5 5
1 9 0
343 7 3
343 7 3
1 5 3
679833 2 5
16 4 0
759376 10 1
729 9 3
362750 9 5
1 9 1
1296 6 4
256 4 2
268043 5 3
249621 3 5
117649 7 6
1 6 2
5 5 5
898563 2 2
442072 10 5
8 2 3
1296 6 5
807687 5 1
1 9 5
16 2 4
881640 7 2
599288 9 1
32 2 4
---
case 1: Theta(n^6.967)
case 3: Theta(n^3)
case 2: Theta(n^5 log n)
case 2: Theta(log n)
case 2: Theta(n^3 log n)
case 2: Theta(n^3 log n)
case 3: Theta(n^3)
case 1: Theta(n^19.375)
case 1: Theta(n^2)
case 1: Theta(n^5.880)
case 2: Theta(n^3 log n)
case 1: Theta(n^5.826)
case 3: Theta(n)
case 2: Theta(n^4 log n)
case 1: Theta(n^4)
case 1: Theta(n^7.766)
case 1: Theta(n^11.312)
case 2: Theta(n^6 log n)
case 3: Theta(n^2)
case 3: Theta(n^5)
case 1: Theta(n^19.777)
case 1: Theta(n^5.645)
case 2: Theta(n^3 log n)
case 3: Theta(n^5)
case 1: Theta(n^8.451)
case 3: Theta(n^5)
case 2: Theta(n^4 log n)
case 1: Theta(n^7.035)
case 1: Theta(n^6.055)
case 1: Theta(n^5)
=== hidden
30
16 4 2
187632 6 6
100000 10 5
4 4 6
6561 9 4
512 8 3
197611 7 2
4 2 2
198375 5 5
46656 6 5
81 9 2
32 2 5
64 8 1
804438 7 5
117649 7 6
867552 6 4
755767 9 6
15625 5 6
677413 3 1
790143 9 0
974890 6 0
422239 6 0
710809 7 6
19762 6 0
2 2 1
877015 2 4
700864 8 4
190524 6 0
289100 5 2
456095 9 6
---
case 2: Theta(n^2 log n)
case 1: Theta(n^6.777)
case 2: Theta(n^5 log n)
case 3: Theta(n^6)
case 2: Theta(n^4 log n)
case 2: Theta(n^3 log n)
case 1: Theta(n^6.267)
case 2: Theta(n^2 log n)
case 1: Theta(n^7.579)
case 1: Theta(n^6)
case 2: Theta(n^2 log n)
case 2: Theta(n^5 log n)
case 1: Theta(n^2)
case 1: Theta(n^6.988)
case 2: Theta(n^6 log n)
case 1: Theta(n^7.631)
case 1: Theta(n^6.160)
case 2: Theta(n^6 log n)
case 1: Theta(n^12.221)
case 1: Theta(n^6.181)
case 1: Theta(n^7.696)
case 1: Theta(n^7.229)
case 1: Theta(n^6.924)
case 1: Theta(n^5.521)
case 2: Theta(n log n)
case 1: Theta(n^19.742)
case 1: Theta(n^6.473)
case 1: Theta(n^6.785)
case 1: Theta(n^7.813)
case 3: Theta(n^6)
=== hidden
30
273036 3 2
343 7 0
729 3 2
64 8 2
63209 3 0
409616 9 0
125 5 3
1 6 4
492145 6 5
879739 5 1
1 4 0
9 9 6
306407 2 5
4096 4 1
256 4 6
891269 2 0
884237 3 5
526027 7 1
49 7 2
444627 9 6
43128 4 5
27 3 4
729 9 3
454564 6 1
348370 4 2
4096 4 6
134287 9 3
353070 8 4
4096 8 2
1000 10 3
---
case 1: Theta(n^11.394)
case 1: Theta(n^3)
case 1: Theta(n^6)
case 2: Theta(n^2 log n)
case 1: Theta(n^10.062)
case 1: Theta(n^5.881)
case 2: Theta(n^3 log n)
case 3: Theta(n^4)
case 1: Theta(n^7.315)
case 1: Theta(n^8.504)
case 2: Theta(log n)
case 3: Theta(n^6)
case 1: Theta(n^18.225)
case 1: Theta(n^6)
case 3: Theta(n^6)
case 1: Theta(n^19.766)
case 1: Theta(n^12.463)
case 1: Theta(n^6.770)
case 2: Theta(n^2 log n)
case 3: Theta(n^6)
case 1: Theta(n^7.698)
case 3: Theta(n^4)
case 2: Theta(n^3 log n)
case 1: Theta(n^7.271)
case 1: Theta(n^9.205)
case 2: Theta(n^6 log n)
case 1: Theta(n^5.374)
case 1: Theta(n^6.143)
case 1: Theta(n^4)
case 2: Theta(n^3 log n)
=== hidden
30
59049 9 5
27389 10 1
920702 3 3
263544 8 2
527216 8 6
16 2 4
32 2 5
986458 4 3
6561 9 6
768464 3 0
273916 3 4
766112 6 3
243 3 5
4 4 6
81 3 4
976499 9 1
216 6 3
824372 5 0
604941 5 0
6561 9 4
64 4 3
194563 8 6
9 9 1
180146 2 3
471315 10 5
791403 8 4
64 8 2
288698 10 2
579207 2 4
3125 5 4
---
case 2: Theta(n^5 log n)
case 1: Theta(n^4.438)
case 1: Theta(n^12.500)
case 1: Theta(n^6.003)
case 1: Theta(n^6.336)
case 2: Theta(n^4 log n)
case 2: Theta(n^5 log n)
case 1: Theta(n^9.956)
case 3: Theta(n^6)
case 1: Theta(n^12.336)
case 1: Theta(n^11.397)
case 1: Theta(n^7.562)
case 2: Theta(n^5 log n)
case 3: Theta(n^6)
case 2: Theta(n^4 log n)
case 1: Theta(n^6.277)
case 2: Theta(n^3 log n)
case 1: Theta(n^8.464)
case 1: Theta(n^8.272)
case 2: Theta(n^4 log n)
case 2: Theta(n^3 log n)
case 3: Theta(n^6)
case 2: Theta(n log n)
case 1: Theta(n^17.459)
case 1: Theta(n^5.673)
case 1: Theta(n^6.531)
case 2: Theta(n^2 log n)
case 1: Theta(n^5.460)
case 1: Theta(n^19.144)
case 1: Theta(n^5)

## Hints
- Comparing `d` with `log_b a` is the same as comparing `b^d` with `a`. Do that with integers.
- Case 2 has two special spellings: `d = 0` gives `log n`, and `d = 1` gives `n log n`. Write `n^1` as `n` everywhere.
- For case 1, check whether `a` is an exact power of `b` by multiplying `1, b, b², …` until you reach or pass `a`.

## Solution
Compute `b^d` with integers and compare it with `a`. That is the same as comparing `d` with `log_b a`, but it has no rounding error. (`b^d` stays at most 10⁹ here.)

- **Equal (case 2):** every level of the recursion tree does the same work, `n^d`, and there are `log n` levels.
- **`b^d > a` (case 3):** the work shrinks geometrically down the tree, so the top level dominates.
- **`b^d < a` (case 1):** the number of subproblems grows faster than the work shrinks, so the leaves dominate. There are `n^(log_b a)` of them.

For case 1, multiply up powers of `b` to see whether `a` is an exact power (then `K` is an integer). Otherwise print `ln a / ln b` with 3 decimals.

Complexity: O(d + log_b a) per query.

```cpp
#include <bits/stdc++.h>
using namespace std;

static string npow(const string& k) { return k == "1" ? "n" : "n^" + k; }

string master(long long a, long long b, int d) {
    long long bd = 1;                       // b^d <= 10^9, fits easily
    for (int i = 0; i < d; ++i) bd *= b;
    if (bd == a) {                          // d == log_b a
        if (d == 0) return "case 2: Theta(log n)";
        return "case 2: Theta(" + npow(to_string(d)) + " log n)";
    }
    if (bd > a)                             // d > log_b a: the root's work dominates
        return "case 3: Theta(" + npow(to_string(d)) + ")";
    // d < log_b a: is log_b a an integer k with b^k == a?
    long long p = 1; int k = 0;
    while (p < a) { p *= b; ++k; }
    string K;
    if (p == a) K = to_string(k);
    else {
        char buf[32];
        snprintf(buf, sizeof buf, "%.3f", log((double)a) / log((double)b));
        K = buf;
    }
    return "case 1: Theta(" + npow(K) + ")";
}
```
