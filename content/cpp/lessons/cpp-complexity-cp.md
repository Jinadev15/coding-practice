# Competitive Programming Setup

C++ is the language of competitive programming and of performance-critical algorithm work, because it runs 10–100× faster than CPython and the STL provides battle-tested containers and algorithms. Writing correct, fast C++ for algorithmic problems still takes a toolkit:
- fast I/O
- a complexity budget
- overflow discipline with `long long`
- a few templates you trust
- an awareness of the pitfalls that turn an accepted solution into "wrong answer" or "time limit exceeded"

This lesson sets up that toolkit. The rest of the module applies it to each algorithm family (the theory is covered in depth in the Python DSA module, and here we focus on C++ implementation).

## 1. The budget in C++

A modern judge machine does roughly **10⁸–10⁹ simple operations per second** in optimised C++.

| n | Feasible complexity (1 s) |
|---|---|
| ≤ 10–11 | O(n!) |
| ≤ 20–25 | O(2ⁿ · n) |
| ≤ 500 | O(n³) |
| ≤ 5 000 | O(n²) |
| ≤ 10⁶ | O(n log n) |
| ≤ 10⁸ | O(n), with tight loops |
| ≥ 10⁹ | O(log n), O(√n) |

Constant factors matter: cache-friendly `std::vector` loops beat `std::map` or `std::list` traversals by large factors (Memory and Performance lesson).

## 2. Fast I/O

```cpp
#include <bits/stdc++.h>          // GCC-only convenience header: fine for contests, not for production
using namespace std;

int main() {
    ios::sync_with_stdio(false);  // decouple iostreams from C stdio: big speed-up
    cin.tie(nullptr);             // don't flush cout before every cin
    int n;
    cin >> n;
    vector<long long> a(n);
    for (auto& x : a) cin >> x;
    // ...
    cout << answer << '\n';       // '\n', NOT endl: endl flushes every line
}
```

> [!WARNING]
> After `sync_with_stdio(false)`, don't mix `printf`/`scanf` with `cin`/`cout` in the same stream. Their buffers are independent, so the output order can be scrambled. `endl` inside a loop printing 10⁶ lines can cost more time than the algorithm itself.

For extreme input sizes (10⁷ numbers), read the whole input with `fread` into a buffer and parse it manually.

## 3. Overflow discipline

| Type | Range | Use |
|---|---|---|
| `int` | ±2.1·10⁹ | indices, counts < 2·10⁹ |
| `long long` | ±9.2·10¹⁸ | sums, products, anything that might exceed 2·10⁹ |
| `unsigned long long` | 0 … 1.8·10¹⁹ | hashing, bit tricks, modular wrap |
| `__int128` | ±1.7·10³⁸ | the products of two long longs before a mod (GCC/Clang) |

```cpp
int a = 100000, b = 100000;
long long bad = a * b;            // overflow happens in int BEFORE the conversion (UB)
long long good = 1LL * a * b;     // promote first
long long s = accumulate(v.begin(), v.end(), 0LL);   // the initial value decides the type! 0 would be int
```

`std::accumulate(v.begin(), v.end(), 0)` sums in `int`, a classic silent bug. The literal suffix `LL` and `1LL *` are your friends.

## 4. Templates worth memorising

```cpp
const long long INF = 4e18;                // or LLONG_MAX / 4 to allow INF + INF without overflow
const int MOD = 1'000'000'007;

long long power(long long b, long long e, long long m) {
    long long r = 1; b %= m;
    for (; e; e >>= 1, b = b * b % m)
        if (e & 1) r = r * b % m;
    return r;
}

template <class T> bool chmin(T& a, const T& b) { return b < a ? (a = b, true) : false; }
template <class T> bool chmax(T& a, const T& b) { return a < b ? (a = b, true) : false; }

// lambda recursion (C++23: deducing this; before that, pass the lambda to itself)
auto dfs = [&](this auto&& self, int u, int p) -> void {
    for (int v : adj[u]) if (v != p) self(v, u);
};
```

## 5. STL complexity cheat sheet

| Container / algorithm | Operation | Cost |
|---|---|---|
| `vector` | push_back / index | amortised O(1) / O(1) |
| `deque` | push/pop at both ends | O(1) |
| `set`/`map` (red–black) | insert/find/erase, lower_bound | O(log n) |
| `unordered_map` | average find/insert | O(1), worst O(n), large constant |
| `priority_queue` | push/pop/top | O(log n)/O(log n)/O(1) |
| `sort`, `stable_sort` | | O(n log n) |
| `nth_element` | | O(n) average |
| `lower_bound` on a vector | | O(log n) |
| `lower_bound(set.begin(), set.end(), x)` | | **O(n)!** Use `set.lower_bound(x)` |

> [!DANGER]
> `std::lower_bound` on `set`/`map` iterators is linear, because they aren't random access. Always use the **member** `s.lower_bound(x)`. Similarly, `std::count` and `std::find` on a set are O(n), while `s.count(x)` and `s.find(x)` are O(log n).

## 6. Hacking-resistant hashing

`unordered_map<long long, int>` can be forced into O(n) per operation by crafted inputs (the default hash of integers is the identity). For untrusted input, use a randomised hash:

```cpp
struct SplitMix {
    static uint64_t mix(uint64_t x) {
        x += 0x9e3779b97f4a7c15; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
        x = (x ^ (x >> 27)) * 0x94d049bb133111eb; return x ^ (x >> 31);
    }
    size_t operator()(uint64_t x) const {
        static const uint64_t seed = chrono::steady_clock::now().time_since_epoch().count();
        return mix(x + seed);
    }
};
unordered_map<long long, int, SplitMix> freq;
freq.reserve(1 << 20);                    // avoid rehashing
```

## 7. Debugging workflow

- Compile with `-O2 -Wall -Wextra -Wshadow -fsanitize=address,undefined -D_GLIBCXX_DEBUG` locally. `_GLIBCXX_DEBUG` adds bounds and iterator checks to the STL.
- Write a brute-force solution and a random test generator, then **stress test** both until they disagree.
- Assert invariants with `assert(...)` during development.

## 8. Exam-ready answers

> [!EXAM]
> **Choosing an algorithm from constraints.** Before implementing, estimate the number of elementary operations the intended algorithm performs for the maximum input and compare it with the time limit, assuming roughly 10⁸ simple operations per second for optimised C++: n ≤ 10⁵–10⁶ requires O(n log n) or better, n ≤ 5000 allows O(n²), and n ≤ 20 permits exponential algorithms such as bitmask DP. Memory limits and data types must be considered too: values exceeding about 2·10⁹ require 64-bit integers, and intermediate products must be computed in a wide enough type before reduction.

## 9. Cheat sheet

| Need | Code |
|---|---|
| fast I/O | `ios::sync_with_stdio(false); cin.tie(nullptr);` |
| newline | `'\n'` |
| 64-bit product | `1LL * a * b` |
| sum of a vector | `accumulate(begin, end, 0LL)` |
| INF without overflow | `LLONG_MAX / 4` |
| set lower bound | `s.lower_bound(x)` (member!) |
| safe hash map | custom splitmix hasher + `reserve` |
| debug build | `-fsanitize=address,undefined -D_GLIBCXX_DEBUG` |

> [!INTERVIEW]
> **"Your O(n log n) solution gets TLE with n = 10⁶. What do you check?"** Check I/O first (sync off, `'\n'` not `endl`). Then look for hidden linear work (`std::lower_bound` on a set, `list::size` in old libraries, copying vectors by value into functions), `map` where a sorted vector or array suffices, `unordered_map` without `reserve` or with an adversarial hash, and recursion overhead. Profile with `perf` if available.
