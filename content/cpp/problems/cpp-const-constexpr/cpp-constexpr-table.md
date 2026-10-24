---
id: cpp-constexpr-table
title: Compile-Time Lookup Tables
difficulty: Medium
order: 1
tags: constexpr, static_assert, std::array
---
## Statement
Build two tables **at compile time**:

- `constexpr std::array<int, 256> POP`: the popcount (number of 1 bits) of every byte value
- `constexpr std::array<long long, 64> FIB`: the Fibonacci numbers F(0)…F(63)

Write `constexpr` functions `make_pop()` and `make_fib()` that return them, and add `static_assert` checks (`POP[255] == 8`, `FIB[10] == 55`). Then answer queries **at run time** using only the tables:

- `pop X` (0 ≤ X < 2^64): the popcount of X, computed byte by byte using `POP`
- `fib N` (0 ≤ N < 64): F(N)

## Starter
```cpp
#include <array>

constexpr std::array<int, 256> make_pop() {
    std::array<int, 256> t{};
    return t;
}

constexpr std::array<long long, 64> make_fib() {
    std::array<long long, 64> f{};
    return f;
}
```

## Driver
```cpp
#include <iostream>
#include <string>
constexpr auto POP = make_pop();
constexpr auto FIB = make_fib();
static_assert(POP[255] == 8 && POP[0] == 0, "popcount table wrong");
static_assert(FIB[10] == 55, "fib table wrong");
int main() {
    std::string q;
    while (std::cin >> q) {
        unsigned long long x; std::cin >> x;
        if (q == "pop") {
            int c = 0;
            for (int i = 0; i < 8; ++i) c += POP[(x >> (8 * i)) & 0xFF];
            std::cout << c << '\n';
        } else {
            std::cout << FIB[x] << '\n';
        }
    }
}
```

## Tests
=== sample
pop 255
fib 10
pop 18446744073709551615
---
8
55
64
=== hidden
pop 0
fib 0
fib 1
fib 63
pop 1099511627776
---
0
0
1
6557470319842
1

## Hints
- `t[i] = (i & 1) + t[i / 2];` fills the popcount table in one pass (the value for i reuses the smaller i/2).
- Loops and assignment to `std::array` elements are allowed in `constexpr` functions (C++14 and later).

## Solution
```cpp
#include <array>

constexpr std::array<int, 256> make_pop() {
    std::array<int, 256> t{};
    for (int i = 1; i < 256; ++i)
        t[i] = (i & 1) + t[i / 2];
    return t;
}

constexpr std::array<long long, 64> make_fib() {
    std::array<long long, 64> f{};
    f[1] = 1;
    for (int i = 2; i < 64; ++i)
        f[i] = f[i - 1] + f[i - 2];
    return f;
}
```

Because the driver declares `constexpr auto POP = make_pop();`, the compiler **must** evaluate the functions during compilation. If they contained something not allowed in constant evaluation (say, undefined behaviour or a call to a non-constexpr function), the build would fail. The `static_assert`s are unit tests that run inside the compiler. The tables end up in read-only data with zero run-time setup cost.
