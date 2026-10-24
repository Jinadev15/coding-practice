---
id: c-bit-flags
title: Robot Status Register
difficulty: Medium
order: 1
tags: bitwise operators, masks, unsigned
---
## Statement
A motor controller exposes an 8-bit status register:

| Bit | Meaning |
|---|---|
| 0 | POWER |
| 1 | ENABLED |
| 2 | FAULT |
| 3 | OVERHEAT |
| 4–7 | a 4-bit speed level (0–15) |

Start with `reg = 0` (`uint8_t`). Process commands until the end of input:

- `set NAME` / `clear NAME` / `toggle NAME` for the flag names above
- `speed K` sets bits 4–7 to K (0 ≤ K ≤ 15) without touching bits 0–3
- `show` prints `reg=0xHH [flags] speed=K`, where flags lists the set flag names in bit order separated by `,` (or `-` if none)

## Starter
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    uint8_t reg = 0;
    char cmd[16], arg[16];
    while (scanf("%15s", cmd) == 1) {

    }
    return 0;
}
```

## Tests
=== sample
set POWER
set ENABLED
speed 9
show
toggle POWER
set OVERHEAT
show
---
reg=0x93 [POWER,ENABLED] speed=9
reg=0x9A [ENABLED,OVERHEAT] speed=9
=== hidden
show
speed 15
set FAULT
speed 0
show
clear FAULT
toggle ENABLED
toggle ENABLED
show
---
reg=0x00 [-] speed=0
reg=0x04 [FAULT] speed=0
reg=0x00 [-] speed=0

## Hints
- Map names to bit numbers with an array `const char *names[] = {"POWER", "ENABLED", "FAULT", "OVERHEAT"};` and `strcmp`.
- Set the speed: `reg = (reg & 0x0F) | (k << 4);`. Read it: `reg >> 4`.
- Parenthesise every mask test: `if ((reg >> i) & 1)`.

## Solution
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

static const char *NAMES[] = {"POWER", "ENABLED", "FAULT", "OVERHEAT"};

static int bit_of(const char *name) {
    for (int i = 0; i < 4; i++)
        if (strcmp(name, NAMES[i]) == 0) return i;
    return -1;
}

int main(void) {
    uint8_t reg = 0;
    char cmd[16], arg[16];
    while (scanf("%15s", cmd) == 1) {
        if (strcmp(cmd, "show") == 0) {
            printf("reg=0x%02X [", reg);
            int any = 0;
            for (int i = 0; i < 4; i++) {
                if ((reg >> i) & 1u) {
                    printf("%s%s", any ? "," : "", NAMES[i]);
                    any = 1;
                }
            }
            printf("%s] speed=%d\n", any ? "" : "-", reg >> 4);
            continue;
        }
        scanf("%15s", arg);
        if (strcmp(cmd, "speed") == 0) {
            int k;
            sscanf(arg, "%d", &k);
            reg = (uint8_t)((reg & 0x0Fu) | ((unsigned)k << 4));
        } else {
            uint8_t mask = (uint8_t)(1u << bit_of(arg));
            if (strcmp(cmd, "set") == 0) reg |= mask;
            else if (strcmp(cmd, "clear") == 0) reg &= (uint8_t)~mask;
            else if (strcmp(cmd, "toggle") == 0) reg ^= mask;
        }
    }
    return 0;
}
```

`reg & 0x0F` keeps the low nibble (the flags) while the new speed is shifted into the high nibble, which is the standard read-modify-write of a hardware register field. The `(uint8_t)` casts silence `-Wconversion`: `~mask` is computed as an `int`, because of integer promotion.
