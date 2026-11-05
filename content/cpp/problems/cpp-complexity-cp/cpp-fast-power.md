---
id: cpp-fast-power
title: Fast Modular Exponentiation
difficulty: Easy
order: 3
tags: complexity, logarithmic, binary exponentiation, overflow, __int128
time_limit: 1
---
## Statement
Compute `a^e mod m` for very large numbers:

```cpp
unsigned long long power_mod(unsigned long long a, unsigned long long e, unsigned long long m);
```

with 0 ≤ a, e ≤ 10¹⁸ and 1 ≤ m ≤ 10¹⁸.

Multiplying `a` by itself `e` times is O(e), which is 10¹⁸ steps. **Binary exponentiation** is O(log e), about 60 steps. Products of two numbers below 10¹⁸ overflow 64 bits, so multiply in `unsigned __int128` before taking the remainder.

By convention `0^0 = 1`, and every result is reduced mod `m`, so anything mod 1 is 0.

**Input:** `q`, then `q` lines `a e m`. Print each result on its own line. q ≤ 2·10⁵.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

unsigned long long power_mod(unsigned long long a, unsigned long long e, unsigned long long m) {
    unsigned long long r = 1 % m;
    for (unsigned long long i = 0; i < e; ++i) r = r * a % m;   // O(e) and overflows
    return r;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    while (q--) {
        unsigned long long a, e, m;
        cin >> a >> e >> m;
        cout << power_mod(a, e, m) << '\n';
    }
}
```

## Tests
=== sample
4
2 10 1000
3 0 7
5 3 1
0 0 13
---
24
1
0
1
=== hidden
3
1000000000000000000 1000000000000000000 999999999999999989
123456789123456789 987654321987654321 1000000000000000000
2 999999999999999999 1000000007
---
3138428376721
372351741974933589
359738130
=== hidden
40
0 9 2
0 222 1
1 129 919460959080304594
85991860533753693 46 1
465600313464144439 256 2322093088268891
0 260 2
0 221 2
245166028961239346 299 889591797722615244
0 189 1
0 44 2
1 32 1
1 226 2
291589746927126752 202 1
0 167 469704146616303549
769881959784977524 210 2
1 99 365428722628026965
0 252 2
1 280 2
91176199858496055 71 2
0 88 989111317225046979
1 64 1
843793367533027445 17 1
578630723718925792 48 1
234375469703845661 233 2
488948081381408887 244 2
820550519779675253 150 1
0 293 962650813276512379
1 144 2
0 200 727153970534152353
373586719581373200 251 2
0 115 26594629717225606
573773245835045242 20 2
0 248 583748323192130458
0 129 295898852358293482
0 256 626469946314359363
1 272 1
1 103 2
240363777768024473 3 1
1 58 404485628662170988
0 223 2
---
0
0
1
0
139814417943473
0
0
102987381093506408
0
0
0
1
0
0
0
1
0
1
1
0
0
0
0
1
1
0
0
1
0
0
0
0
0
0
0
0
1
0
1
0
=== hidden
40
0 17 819430324980719119
124081250888493000 247 420146598961195266
0 162 1
867292617346972187 45 1
0 184 1
1 97 1
0 123 658763340406633318
1 12 266212074016645873
0 54 812286618225753412
481120337097448738 265 213466899803265655
503883038333793053 268 1
0 120 2
840001109103149597 236 1
0 173 570748016048087280
712238659467546472 162 2
465832831048098413 211 2
1 196 2
0 298 1
0 11 182463610356173152
96027694090011290 23 2
0 86 2
1 244 1
0 262 1
0 153 1
1 139 1
1 294 1
505296090705730996 31 445903866832842846
1 131 1
1 113 625001148553613695
375823420808799015 192 96734437048233398
273766795306625674 280 593663466304598376
270674881385802920 13 2
1 114 1
1 122 103642176400839486
0 62 2
0 170 758016602541637356
419237650107591760 143 756509479028901954
1 65 1
1 241 637438203346124380
403609850860486517 270 88600193611878638
---
0
167699717795496978
0
0
0
0
0
1
0
118520309679185203
0
0
0
0
0
1
1
0
0
0
0
0
0
0
0
0
42921227244388726
0
1
16495793859639121
326390354748594232
0
0
1
0
0
323869204796669344
0
1
31908444273822389
=== hidden
40
0 25 378560847236312841
0 271 2
204941351188437793 126 820221157822777658
296236821117979184 45 1
59501277995579793 175 1
1 208 792410524249898197
1 194 1
145353959251614677 170 2
255468855459472579 300 2
170791693136724238 101 2
0 31 1
1 246 2
0 146 2
1 42 1
0 254 2
1 186 475687016903458908
0 278 1
689978042451029349 129 1
525524482677192601 182 1
320883842336569404 155 2
1 57 697793070219083214
232230490868993415 242 888799061922714580
1 71 2
0 49 1
332196997237442538 199 1
0 253 2
0 218 1
0 216 2
1 27 1
648156954105563337 9 731971603300124396
0 203 780289307370422571
1 221 708336234146723303
0 63 2
1 247 1
1 69 1
1 116 2
0 165 2
1 50 1
0 242 666205003784387223
0 293 812269720184847800
---
0
0
591134552323149507
0
0
1
0
1
1
0
0
1
0
0
0
1
0
0
0
0
1
634438701129894545
1
0
0
0
0
0
0
545279938204539661
0
1
0
0
0
1
0
0
0
0
=== hidden
@gen 3337224636 big
=== hidden
@gen 3337224637 big
=== hidden
@gen 3337224638 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    q = 40; print(q)
    for _ in range(q):
        print(r.choice([0, 1, r.randint(0, 10**18)]), r.randint(0, 300), r.choice([1, 2, r.randint(1, 10**18)]))
else:
    q = 200000; print(q)
    print("\n".join(f"{r.randint(0,10**18)} {r.randint(0,10**18)} {r.randint(1,10**18)}" for _ in range(q)))
```

## Hints
- `a^13 = a^8 · a^4 · a^1`, because 13 is `1101` in binary.
- Keep `b = a^(2^k)` by squaring at every step, and multiply it into the answer when the lowest bit of `e` is 1. Then shift `e` right.
- `(unsigned __int128)x * y % m` avoids overflow. Remember that `1 % m` is 0 when `m = 1`.

## Solution
Write the exponent in binary. For example, `e = 13 = 1101₂`, so `a^13 = a^8 · a^4 · a^1`.

Square `b` repeatedly to get `a, a², a⁴, a⁸, …` (one squaring per bit). Multiply the result by the powers whose bit is set in `e`. That's at most 2·⌈log₂ e⌉ multiplications.

Every product of two values below `m ≤ 10¹⁸` fits in 128 bits, so cast to `unsigned __int128` before multiplying, then take `% m`.

Start with `r = 1 % m`, so that `m = 1` gives 0.

Complexity: O(log e) per query.

```cpp
#include <bits/stdc++.h>
using namespace std;

unsigned long long power_mod(unsigned long long a, unsigned long long e, unsigned long long m) {
    using u128 = unsigned __int128;
    unsigned long long r = 1 % m, b = a % m;
    while (e > 0) {
        if (e & 1) r = (u128)r * b % m;     // this bit of e is set: multiply it in
        b = (u128)b * b % m;                // b becomes a^(2^k)
        e >>= 1;
    }
    return r;
}
```
