---
id: cpp-fs-rho-brent
title: Tail and Cycle of x² + c (Brent)
difficulty: Hard
order: 7
tags: functional graph, Brent, Floyd, cycle length, number theory, implicit graph
time_limit: 2
---
## Statement
Iterate the map `f(x) = (x² + c) mod m` from a start value `x₀`:

```text
x₀, x₁ = f(x₀), x₂ = f(x₁), …
```

There are only `m` possible values, so the sequence eventually repeats and then cycles forever: its shape is the letter ρ. Find

- `μ` (mu): the index of the first value that lies on the cycle (the tail length), and
- `λ` (lambda): the cycle length, the smallest `λ ≥ 1` with `x_{μ+λ} = x_μ`.

```cpp
std::pair<long long, long long> rho(unsigned long long m, unsigned long long c, unsigned long long x0);   // {mu, lambda}
```

Example: `m = 10, c = 1, x₀ = 3` gives `3, 0, 1, 2, 5, 6, 7, 0, …`. The value `0` (index 1) recurs at index 7, so `μ = 1` and `λ = 6`.

This is the **graph is implicit** case of cycle finding: the "nodes" are numbers and `f` is the `next` pointer. Here `m` goes up to 10¹², so the graph can't be stored, and `μ + λ` is typically around a million. Use **Brent's algorithm** (or Floyd) with O(1) memory. Compute `x²` with `unsigned __int128` to avoid overflow.

**Input:** queries until the end of input, one per line: `m c x0` (1 ≤ m ≤ 10¹², 0 ≤ c, x0 < m). At most 4 queries have m > 10⁶.

**Output:** `mu lambda` per query.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<long long, long long> rho(unsigned long long m, unsigned long long c, unsigned long long x0) {
    return {0, 0};   // TODO
}
```

## Driver
```cpp
int main() {
    unsigned long long m, c, x0;
    while (cin >> m >> c >> x0) {
        auto [mu, lam] = rho(m, c, x0);
        cout << mu << ' ' << lam << '\n';
    }
}
```

## Tests
=== sample
10 1 3
1 0 0
7 0 2
1000000007 1 2
---
1 6
0 1
0 2
4871 27573
=== hidden
2 1 0
2 0 1
13 5 12
100 99 50
999983 3 7
65536 1 1
---
0 2
0 1
4 2
1 2
435 1534
10 2
=== hidden
37 2 25
2931 2301 832
2531 1058 317
1091 922 1011
1143 1046 645
450 290 5
---
1 6
0 7
24 13
41 39
2 6
2 2
=== hidden
2583 1414 1576
210 158 92
1080 737 966
270 85 52
1284 109 981
1389 412 753
---
1 3
0 2
3 2
2 18
2 6
22 8
=== hidden
2740 2241 438
2669 1973 491
1129 656 1105
2790 2453 2422
1557 985 1051
2305 1648 1594
---
13 66
1 48
24 21
6 6
38 3
38 1
=== hidden
529251065619 249958487744 383357772145
785552514701 131054430265 11464697462
560451961971 523651528322 130899283304
714003667478 668821728286 37891432679
662204 281142 599871
124087 45941 38039
762109 559116 195069
781736 14104 108738
306252 6614 61735
541002 247705 379665
451658 199900 278823
530044 198295 178338
899911 538984 770841
744874 640935 146906
952398 932050 522737
991237 99491 249362
198449 10500 15228
898895 528762 685715
130324 20773 63205
805981 696775 283914
308780 259742 107589
477913 219472 2380
956254 138426 124637
746849 410490 675862
---
158691 308654
371 46968
38 108
915 37554
74 280
113 449
28 200
7 10
5 42
33 30
614 229
177 10
52 520
43 302
89 33
50 564
50 15
87 550
20 52
70 180
9 254
275 536
212 16
4 65
=== hidden
582282683960 433700841042 411972610775
937720301836 360653292784 390528700588
717528880788 629730041619 984933750
841132701644 542520709105 241172507298
690483 674511 267195
811977 650869 668972
703045 126820 135797
315993 254967 195875
184707 130976 184398
466511 275201 238612
559742 120193 919
269102 98528 26880
967877 118026 879279
339172 264534 339102
149042 124531 113382
767724 637903 215861
665167 50429 101462
346284 184316 278796
789981 270419 623020
138067 121834 76517
265202 231952 161526
778340 744647 152412
612008 13016 454067
884401 60222 248888
---
11184 122430
21750 455544
7760 269458
493 38970
198 55
606 12
16 5
196 315
30 10
46 60
18 60
7 44
133 481
57 12
120 178
30 74
3 60
78 34
3 4240
13 32
7 2
229 66
4 70
14 62
=== hidden
993952730838 169346970570 735270668593
581668850339 260659800789 37235552208
725862176480 29960112839 504388565645
620346484559 474981030327 583209496491
172249 39017 37437
917952 561385 826000
571013 477517 192246
104620 60654 74856
851165 22098 295861
32009 9265 30058
749841 381974 623761
38918 977 863
555083 423371 485438
612351 497860 61522
357070 257823 118498
492345 36127 389509
550363 543613 132450
167599 78957 17768
326369 135619 233422
547659 242615 517287
814800 212853 162276
851093 797496 368361
850157 65731 227674
387396 2137 286444
---
1178 46230
9110 8688
161 8094
1538 223533
7 108
27 12
131 430
69 16
9 4
6 36
65 620
3 30
204 1
5 60
88 12
3 66
184 118
49 278
35 520
70 222
3 12
729 662
7 440
5 18

## Hints
- The sequence x₀, f(x₀), … is a linked list whose `next` pointer is f. All the cycle-finding tools apply, but the "list" is never stored.
- Brent: keep the tortoise fixed while the hare takes up to `power` steps; if they never meet, move the tortoise to the hare and double `power`. The step count when they meet is λ.
- Once λ is known, put one pointer λ steps ahead of the start and walk both together: they meet after μ steps. Use `unsigned __int128` for `x * x`.

## Solution
**Brent's algorithm** keeps the tortoise still and lets the hare run in rounds of length 1, 2, 4, 8, … At the start of each round the tortoise teleports to the hare's position. Once the round length is at least `λ` and the tortoise is already on the cycle (both happen within O(μ + λ) steps), the hare returns to the tortoise within that round, and the number of steps it took in the round **is** `λ`.

**Then μ:** start two pointers at `x₀`, advance one of them `λ` steps, then step both together. They are always `λ` apart, so they first coincide when the trailing one enters the cycle: after `μ` steps.

**Why not store everything?** A hash map from value to index is the obvious solution and works for small `m`, but needs memory proportional to `μ + λ` (millions of entries here, and unbounded in general, e.g. in Pollard's rho factorisation with huge `m`). Floyd also uses O(1) memory but evaluates `f` about three times per step; Brent evaluates it once per hare step and is typically 25–35% faster, which matters when `f` is expensive (128-bit multiplication and a modulo here).

Complexity: O(μ + λ) evaluations of `f`, O(1) memory. For a random-looking map, μ + λ ≈ √(πm/2), about 1.25·10⁶ for m = 10¹².

```cpp
#include <bits/stdc++.h>
using namespace std;
using u64 = unsigned long long;

static inline u64 f(u64 x, u64 c, u64 m) { return (u64)(((unsigned __int128)x * x + c) % m); }

pair<long long, long long> rho(u64 m, u64 c, u64 x0) {
    // Brent, part 1: lambda. The tortoise waits at x_{2^i - 1}; the hare runs up to 2^i steps past it.
    u64 power = 1, lam = 1, tortoise = x0, hare = f(x0, c, m);
    while (tortoise != hare) {
        if (power == lam) { tortoise = hare; power <<= 1; lam = 0; }   // teleport the tortoise
        hare = f(hare, c, m);
        ++lam;
    }
    // Part 2: mu. Put the hare lambda steps ahead of the start, then walk both until they meet.
    u64 t = x0, h = x0;
    for (u64 i = 0; i < lam; ++i) h = f(h, c, m);
    long long mu = 0;
    while (t != h) { t = f(t, c, m); h = f(h, c, m); ++mu; }
    return {mu, (long long)lam};
}
```
