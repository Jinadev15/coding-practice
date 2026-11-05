---
id: cpp-product-except-self
title: Products and Sums Except Self
difficulty: Medium
order: 7
tags: arrays, prefix products, suffix products, modular arithmetic
time_limit: 2
---
## Statement
For every position `i`, compute the product of **all other** elements, modulo 10⁹+7:

```cpp
std::vector<long long> product_except_self(const std::vector<long long>& a);   // modulo 1e9+7
```

Values range over `[0, 10⁹]`, so **zeros are allowed**, and that is why you can't divide the total product by `a[i]`. (A modular inverse of 0 doesn't exist either.) Use a **prefix pass** (the product of everything to the left) and a **suffix pass** (everything to the right) in O(n) time. Apart from the output vector, use O(1) extra memory.

Also implement the **max** version with the same two-pass shape. It shows that the technique works for any associative operation:

```cpp
std::vector<long long> max_except_self(const std::vector<long long>& a);   // max of all OTHER elements
```

For `n = 1`, the product of no elements is 1, and the max of no elements is defined as −1.

**Input:** cases until the end of input: `n` followed by `n` values (n ≤ 10⁶). The driver prints both results for small n, or checksums for big n.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

const long long MOD = 1000000007;
vector<long long> product_except_self(const vector<long long>& a) {
    vector<long long> out(a.size(), 1);
    for (size_t i = 0; i < a.size(); ++i)
        for (size_t j = 0; j < a.size(); ++j)
            if (i != j) out[i] = out[i] * (a[j] % MOD) % MOD;    // O(n^2)
    return out;
}
vector<long long> max_except_self(const vector<long long>& a) { return vector<long long>(a.size(), -1); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    size_t n;
    while (cin >> n) {
        vector<long long> a(n);
        for (auto& x : a) cin >> x;
        auto p = product_except_self(a), m = max_except_self(a);
        if (n <= 12) {
            for (auto x : p) cout << x << ' ';
            cout << "| ";
            for (auto x : m) cout << x << ' ';
            cout << '\n';
        } else {
            long long hp = 0, hm = 0;
            for (size_t i = 0; i < n; ++i) { hp = (hp * 31 + p[i]) % 1000000007; hm = (hm * 31 + m[i] + 1) % 1000000007; }
            cout << hp << ' ' << hm << '\n';
        }
    }
}
```

## Tests
=== sample
4
1 2 3 4
5
0 4 0 2 9
---
24 12 8 6 | 4 4 4 3 
0 0 0 0 0 | 9 9 9 9 4 
=== hidden
1
7
2
0 5
3
1000000000 1000000000 1000000000
6
3 0 2 0 0 1
---
1 | -1 
5 0 | 5 0 
49 49 49 | 1000000000 1000000000 1000000000 
0 0 0 0 0 0 | 2 3 3 3 3 3 
=== hidden
5
776809885 918047402 816045264 7272835 652951548
2
473841253 711872879
5
352265120 701752505 214899962 320654301 576286349
1
0
3
17055647 29802879 236042238
9
462411920 835600639 116917245 270039045 600028398 439089437 593355139 815884240 681080249
---
851983993 744714551 57549313 498889775 764658727 | 918047402 816045264 918047402 918047402 918047402 
711872879 473841253 | 711872879 473841253 
88783785 553457238 83698454 156447154 936847125 | 701752505 576286349 701752505 701752505 701752505 
1 | -1 
208760036 60237015 380249564 | 236042238 236042238 29802879 
717186123 893639781 543530129 668001922 446844467 818540081 103315413 887156608 972927511 | 835600639 815884240 835600639 835600639 835600639 835600639 835600639 835600639 835600639 
=== hidden
1
229151535
2
747650186 920436635
6
432267052 591339348 131286756 781447270 828286613 600419029
9
0 954067931 216984641 469488461 214693966 105341028 552377834 763285354 967692597
9
0 302599314 424614603 8019934 200195869 489635286 863221408 473891247 492014381
2
479189178 646235390
---
1 | -1 
920436635 747650186 | 920436635 747650186 
667935704 371426515 782407575 757257039 723114629 666161226 | 828286613 828286613 828286613 828286613 781447270 828286613 
646903349 0 0 0 0 0 0 0 0 | 967692597 967692597 967692597 967692597 967692597 967692597 967692597 967692597 954067931 
999781959 0 0 0 0 0 0 0 0 | 863221408 863221408 863221408 863221408 863221408 863221408 492014381 863221408 863221408 
646235390 479189178 | 646235390 479189178 
=== hidden
8
165631805 73323144 99125614 0 576590867 804674647 475528008 639536149
6
89886603 532841732 641531183 344676605 54958778 773715717
5
949365832 362880917 405656115 395348120 537838235
5
554505948 427141703 721881837 978844245 526071376
4
750247923 764006830 21535224 340259274
1
519849589
---
0 0 0 361351450 0 0 0 0 | 804674647 804674647 804674647 804674647 804674647 639536149 804674647 804674647 
69447247 782701031 860147180 356961941 366229617 606613817 | 773715717 773715717 773715717 773715717 773715717 641531183 
321097017 271270978 193897775 651370808 817207902 | 537838235 949365832 949365832 949365832 949365832 
508089843 379712173 638646066 396775780 311234138 | 978844245 978844245 978844245 721881837 978844245 
467613455 102926981 589260182 59187060 | 764006830 750247923 764006830 764006830 
1 | -1 
=== hidden
@gen 717360092 big
=== hidden
@gen 717360093 big
=== hidden
@gen 717360094 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    print(n); print(" ".join(str(r.choice([0, r.randint(0, 10**9)]) if r.random() < 0.15 else r.randint(1, 10**9)) for _ in range(n)))
```

## Hints
- out[i] = (product of a[0..i−1]) × (product of a[i+1..n−1]).
- Do one left-to-right pass storing the prefix products in `out`, then one right-to-left pass multiplying in a running suffix product.
- Take `% MOD` after every multiplication, and count down with `for (size_t i = n; i-- > 0;)` to avoid unsigned wrap-around.

## Solution
"Everything except `i`" = (everything left of `i`) combined with (everything right of `i`).

- **First pass**, left to right: store the running product of the prefix *before* including `a[i]`.
- **Second pass**, right to left: multiply in the running product of the suffix after `i`.

The running values are single variables, so apart from the output the extra memory is O(1).

The same shape works for **any associative operation**: sum, max, gcd, xor. Only the identity element changes (1 for product, −1 here for max over non-negative values). Division-based shortcuts break on zeros, and they don't exist at all for max or gcd.

`for (size_t i = n; i-- > 0; )` is the safe way to count down with an unsigned index. It runs `i = n−1 … 0` without wrapping around.

Complexity: O(n) time, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

const long long MOD = 1000000007;

vector<long long> product_except_self(const vector<long long>& a) {
    size_t n = a.size();
    vector<long long> out(n, 1);
    long long left = 1;                                   // product of a[0..i-1]
    for (size_t i = 0; i < n; ++i) { out[i] = left; left = left * (a[i] % MOD) % MOD; }
    long long right = 1;                                  // product of a[i+1..n-1]
    for (size_t i = n; i-- > 0; ) { out[i] = out[i] * right % MOD; right = right * (a[i] % MOD) % MOD; }
    return out;
}

vector<long long> max_except_self(const vector<long long>& a) {
    size_t n = a.size();
    vector<long long> out(n, -1);
    long long left = -1;
    for (size_t i = 0; i < n; ++i) { out[i] = left; left = max(left, a[i]); }
    long long right = -1;
    for (size_t i = n; i-- > 0; ) { out[i] = max(out[i], right); right = max(right, a[i]); }
    return out;
}
```
