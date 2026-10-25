# Greedy, Math and Bits

The final DSA lesson collects the C++ forms of greedy algorithms, number theory and bit manipulation: custom comparators for sorting-based greedies (and the strict-weak-ordering rule they must obey), `std::gcd`/`std::lcm`, modular arithmetic with overflow-safe multiplication, sieves, `<bit>` utilities, and `std::bitset`. The proofs and theory are in the Python Greedy, Bit Manipulation and Number Theory lessons.

## 1. Greedy with sorting and comparators

```cpp
// interval scheduling: maximum non-overlapping, sort by end
sort(iv.begin(), iv.end(), [](const auto& a, const auto& b) { return a.second < b.second; });
int count = 0; long long end = LLONG_MIN;
for (auto [s, e] : iv) if (s >= end) { ++count; end = e; }
```

> [!DANGER]
> A comparator must be a **strict weak ordering**: irreflexive (`comp(a, a)` is false), transitive, and with transitive incomparability. Writing `<=` instead of `<` violates irreflexivity, and `std::sort` may then read out of bounds and crash. That's real undefined behaviour, not just a wrong order.

### The classic exchange-argument sort: "largest number"

Arrange numbers to form the largest concatenation: sort by `a + b > b + a` on strings. This comparator is a valid strict weak ordering (provably transitive), so `std::sort` is safe:

```cpp
sort(s.begin(), s.end(), [](const string& a, const string& b) { return a + b > b + a; });
```

### Scheduling with deadlines

Earliest-deadline-first (sort by deadline), or "maximise profit with deadlines" (sort by profit and fill the latest free slot using a DSU over time slots). The DSU trick finds the latest free slot ≤ d in near-O(1).

## 2. Number theory in C++

```cpp
#include <numeric>
long long g = std::gcd(48LL, 18LL);         // 6
long long l = std::lcm(4LL, 6LL);           // 12 (careful: can overflow)

using u64 = unsigned long long;
u64 mulmod(u64 a, u64 b, u64 m) { return (unsigned __int128)a * b % m; }   // safe for m up to 2^63
u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1 % m; a %= m;
    for (; e; e >>= 1, a = mulmod(a, a, m)) if (e & 1) r = mulmod(r, a, m);
    return r;
}

// deterministic Miller–Rabin for 64-bit n
bool is_prime(u64 n) {
    if (n < 2) return false;
    for (u64 p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
        if (n % p == 0) return n == p;
    u64 d = n - 1; int s = 0;
    while (!(d & 1)) { d >>= 1; ++s; }
    for (u64 a : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) {
        u64 x = powmod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        bool composite = true;
        for (int r = 1; r < s && composite; ++r) {
            x = mulmod(x, x, n);
            if (x == n - 1) composite = false;
        }
        if (composite) return false;
    }
    return true;
}
```

The first 12 primes as witnesses make Miller–Rabin deterministic for all n < 3.3·10²⁴, which covers every 64-bit value.

### Linear sieve (smallest prime factor)

```cpp
vector<int> spf(N + 1, 0), primes;
for (int i = 2; i <= N; ++i) {
    if (!spf[i]) { spf[i] = i; primes.push_back(i); }
    for (int p : primes) {
        if (p > spf[i] || 1LL * i * p > N) break;
        spf[i * p] = p;                      // each composite is marked exactly once
    }
}
// factorise x in O(log x): while (x > 1) { int p = spf[x]; x /= p; ... }
```

## 3. Bits: `<bit>` and builtins

| Need | C++20 `<bit>` | GCC builtin |
|---|---|---|
| popcount | `std::popcount(x)` | `__builtin_popcountll(x)` |
| trailing zeros | `std::countr_zero(x)` | `__builtin_ctzll(x)` (UB for 0) |
| leading zeros | `std::countl_zero(x)` | `__builtin_clzll(x)` (UB for 0) |
| ⌊log₂ x⌋ | `std::bit_width(x) - 1` | `63 - __builtin_clzll(x)` |
| power of two? | `std::has_single_bit(x)` | `x && !(x & (x - 1))` |
| next power of two | `std::bit_ceil(x)` | |
| rotate | `std::rotl(x, k)` | |

The `<bit>` functions require **unsigned** types and are defined for 0 (`countr_zero(0u) == 32`).

```cpp
// iterate over the set bits
for (unsigned m = mask; m; m &= m - 1) {
    int i = std::countr_zero(m);
    // ... element i
}

std::bitset<64> b(0b1011);
b.count(); b.test(1); b.set(5); b.flip(); b.to_ullong();
```

## 4. Combinatorics mod p

```cpp
const int MOD = 1'000'000'007, MX = 1'000'000;
vector<long long> fact(MX + 1), inv(MX + 1);
fact[0] = 1;
for (int i = 1; i <= MX; ++i) fact[i] = fact[i - 1] * i % MOD;
inv[MX] = powmod(fact[MX], MOD - 2, MOD);
for (int i = MX; i > 0; --i) inv[i - 1] = inv[i] * i % MOD;
auto C = [&](int n, int k) -> long long {
    return (k < 0 || k > n) ? 0 : fact[n] * inv[k] % MOD * inv[n - k] % MOD;
};
```

## 5. Exam-ready answers

> [!EXAM]
> **Strict weak ordering.** Standard sorting algorithms and ordered containers require their comparator to induce a strict weak ordering: it must be irreflexive (`comp(a, a)` is false), asymmetric, and transitive, and incomparability (neither `comp(a, b)` nor `comp(b, a)`) must also be transitive, so that equivalent elements form consistent classes. Comparators that violate these properties, for example using `<=`, or comparing floating-point values that include NaN, cause undefined behaviour: `std::sort` may produce unsorted output or access memory out of bounds, and `std::set` may lose or duplicate elements.

## 6. Cheat sheet

| Need | C++ |
|---|---|
| sort by a key | `sort(..., [](auto& a, auto& b){ return a.k < b.k; })` |
| comparator rule | strict `<`, never `<=` |
| gcd/lcm | `std::gcd`, `std::lcm` |
| 64-bit mulmod | `(unsigned __int128)a * b % m` |
| primality (64-bit) | deterministic Miller–Rabin |
| SPF sieve | linear sieve |
| bit ops | `<bit>`: `popcount`, `countr_zero`, `bit_width` |
| fixed bitset | `std::bitset<N>` |

> [!INTERVIEW]
> **"`sort` with a comparator crashed with a segfault. How?"** The comparator wasn't a strict weak ordering, typically `return a <= b;`, or a comparator inconsistent across calls (random, or depending on mutable state). Introsort's unguarded inner loops rely on `comp(x, x) == false` to stop at sentinels, so with `<=` they can run past the end of the array. Fix it by using `<` and making sure the ordering is transitive.
