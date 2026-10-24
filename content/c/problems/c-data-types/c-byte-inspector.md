---
id: c-byte-inspector
title: Same Bits, Different Types
difficulty: Medium
order: 2
tags: signed, unsigned, two's complement, uint8_t
---
## Statement
Read integers `v` (−128 ≤ v ≤ 255), one per line, until the end of input. For each, store it in a `uint8_t` (if it's negative, the conversion reduces modulo 256) and print:

`u=U s=S hex=HH bits=BBBBBBBB`

where `U` is the value as `uint8_t` (0–255), `S` is the **same 8 bits** interpreted as `int8_t` (−128–127), `HH` is two uppercase hex digits, and `BBBBBBBB` is the 8-bit binary pattern (most significant bit first).

## Starter
```c
#include <stdio.h>
#include <stdint.h>

int main(void) {
    int v;
    while (scanf("%d", &v) == 1) {

    }
    return 0;
}
```

## Tests
=== sample
200
-1
5
---
u=200 s=-56 hex=C8 bits=11001000
u=255 s=-1 hex=FF bits=11111111
u=5 s=5 hex=05 bits=00000101
=== hidden
128
-128
0
127
---
u=128 s=-128 hex=80 bits=10000000
u=128 s=-128 hex=80 bits=10000000
u=0 s=0 hex=00 bits=00000000
u=127 s=127 hex=7F bits=01111111

## Hints
- `uint8_t b = (uint8_t)v;` (well-defined modulo 256).
- Signed view: `int s = b < 128 ? b : b - 256;`. Converting `b` to `int8_t` directly gives the same result on every two's-complement machine (and is guaranteed since C23).
- Bits: loop `i` from 7 down to 0 and print `(b >> i) & 1`.

## Solution
```c
#include <stdio.h>
#include <stdint.h>

int main(void) {
    int v;
    while (scanf("%d", &v) == 1) {
        uint8_t b = (uint8_t)v;
        int s = b < 128 ? b : b - 256;
        printf("u=%d s=%d hex=%02X bits=", b, s, b);
        for (int i = 7; i >= 0; i--)
            putchar(((b >> i) & 1) ? '1' : '0');
        putchar('\n');
    }
    return 0;
}
```

`while (scanf(...) == 1)` is the C idiom for "read until the end of input": `scanf` returns the number of items converted, and `EOF` at the end. The `b - 256` formula is exactly the definition of two's complement: a set top bit is worth −128 instead of +128. Robot sensors often send signed 8- and 16-bit values over serial links, and decoding them is this same operation.
