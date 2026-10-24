---
id: c-can-signals
title: CAN Bus Signal Codec (Intel and Motorola Byte Order)
difficulty: Hard
order: 2
tags: bit manipulation, CAN, DBC, endianness, two's complement, fixed-point scaling, robotics
---
## Statement
Robots and vehicles carry sensor and actuator data over a **CAN bus** in 8-byte frames. A database file (a DBC) describes where each **signal** lives inside the frame. Write the codec a robot controller uses to pack and unpack those signals.

A signal is defined by `signal NAME START LEN ORDER SIGN FACTOR OFFSET`:
- **Bits** are numbered `byte * 8 + bit`, where bit 0 is the least significant bit of each byte. The frame bytes are B0 … B7.
- **`le`** (Intel, little-endian): `START` is the signal's **least significant** bit. Raw bit i lives at frame bit `START + i`.
- **`be`** (Motorola, big-endian): `START` is the signal's **most significant** bit. The following (less significant) bits go *down* within the byte, from bit 7 towards bit 0. After bit 0 of byte k, they continue at bit 7 of byte k + 1. So from position p, the next position is `p - 1`, or `p + 15` if `p % 8 == 0`.
- `LEN` is from 1 to 32. `SIGN` is `u` (unsigned) or `s` (two's complement over LEN bits).
- Physical value = `raw * FACTOR + OFFSET`, where FACTOR and OFFSET are doubles.

Commands (all definitions in the tests are valid and fit inside 64 bits):

| Command | Action and output |
|---|---|
| `signal …` | defines a signal (prints nothing) |
| `frame B0 … B7` | sets the frame from 8 hex bytes (prints nothing) |
| `show` | prints `frame: B0 B1 … B7` as two-digit uppercase hex |
| `decode NAME` | prints `NAME = V (raw R)`, with V formatted as `%.3f` and R as a signed or unsigned decimal |
| `encode NAME VALUE` | raw = round((VALUE − OFFSET) / FACTOR), using `llround`; if it falls outside the raw range, it's clamped to the nearest limit. Writes the raw value into the frame without disturbing other bits, then prints `encode NAME -> raw R` with ` (clamped)` appended if clamping happened |

An unknown signal name prints `error: unknown signal NAME`. The frame starts at all zeros.

## Starter
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        /* TODO */
    }
    return 0;
}
```

## Tests
=== sample
signal speed 0 16 le u 0.01 0
signal temp 16 8 le s 1 -40
signal rpm 31 16 be u 1 0
encode speed 12.34
encode temp 25
encode rpm 4660
show
decode speed
decode temp
decode rpm
frame FF FF FF FF FF FF FF FF
decode temp
decode rpm
decode nope
---
encode speed -> raw 1234
encode temp -> raw 65
encode rpm -> raw 4660
frame: D2 04 41 12 34 00 00 00
speed = 12.340 (raw 1234)
temp = 25.000 (raw 65)
rpm = 4660.000 (raw 4660)
temp = -41.000 (raw -1)
rpm = 65535.000 (raw 65535)
error: unknown signal nope
=== hidden
signal a 0 1 le u 1 0
signal b 1 3 le s 1 0
signal c 4 4 le u 0.5 -2
signal d 63 1 be u 1 0
encode a 1
encode b -4
encode c 5.5
encode d 1
show
decode b
decode c
encode b 3
encode b -5
encode b 100
encode c 1000
encode c -1000
show
decode a
decode b
decode c
decode d
---
encode a -> raw 1
encode b -> raw -4
encode c -> raw 15
encode d -> raw 1
frame: F9 00 00 00 00 00 00 80
b = -4.000 (raw -4)
c = 5.500 (raw 15)
encode b -> raw 3
encode b -> raw -4 (clamped)
encode b -> raw 3 (clamped)
encode c -> raw 15 (clamped)
encode c -> raw 0 (clamped)
frame: 07 00 00 00 00 00 00 80
a = 1.000 (raw 1)
b = 3.000 (raw 3)
c = -2.000 (raw 0)
d = 1.000 (raw 1)
=== hidden
signal steer 12 12 le s 0.1 0
signal yaw 39 16 be s 0.01 0
signal flags 24 8 le u 1 0
signal mid 51 10 be u 1 0
frame 00 00 00 00 00 00 00 00
encode steer -123.4
encode yaw -3.14
encode flags 165
encode mid 1000
show
decode steer
decode yaw
decode flags
decode mid
encode mid 1024
encode yaw 400
show
decode yaw
decode steer
---
encode steer -> raw -1234
encode yaw -> raw -314
encode flags -> raw 165
encode mid -> raw 1000
frame: 00 E0 B2 A5 FE C6 0F A0
steer = -123.400 (raw -1234)
yaw = -3.140 (raw -314)
flags = 165.000 (raw 165)
mid = 1000.000 (raw 1000)
encode mid -> raw 1023 (clamped)
encode yaw -> raw 32767 (clamped)
frame: 00 E0 B2 A5 7F FF 0F FC
yaw = 327.670 (raw 32767)
steer = -123.400 (raw -1234)
=== hidden
signal wide 0 32 le u 1 0
signal wides 32 32 le s 1 0
signal mwide 7 32 be u 1 0
encode wide 4294967295
encode wides -2147483648
show
decode wide
decode wides
decode mwide
encode mwide 305419896
show
decode wide
encode wides 1e12
decode wides
frame 12 34 56 78 9A BC DE F0
decode mwide
decode wide
decode wides
signal odd 13 9 be s 0.25 10
decode odd
encode odd 0
show
decode odd
---
encode wide -> raw 4294967295
encode wides -> raw -2147483648
frame: FF FF FF FF 00 00 00 80
wide = 4294967295.000 (raw 4294967295)
wides = -2147483648.000 (raw -2147483648)
mwide = 4294967295.000 (raw 4294967295)
encode mwide -> raw 305419896
frame: 12 34 56 78 00 00 00 80
wide = 2018915346.000 (raw 2018915346)
encode wides -> raw 2147483647 (clamped)
wides = 2147483647.000 (raw 2147483647)
mwide = 305419896.000 (raw 305419896)
wide = 2018915346.000 (raw 2018915346)
wides = -253838182.000 (raw -253838182)
odd = -13.500 (raw -94)
encode odd -> raw -40
frame: 12 3B 16 78 9A BC DE F0
odd = 0.000 (raw -40)
## Hints
- Build a list of frame bit positions for the signal, from the raw value's **least significant** bit to its most significant. For `le`, that's `START + i`. For `be`, walk from `START` (the MSB) with `p = (p % 8 == 0) ? p + 15 : p - 1`, collecting LEN positions, then reverse the list.
- Frame bit p is `(frame[p / 8] >> (p % 8)) & 1`. Assemble the raw value in a `uint64_t`.
- Signed: if bit LEN−1 is set, subtract `1ULL << LEN` (as `long long`).
- The raw range is `[0, 2^LEN − 1]` for unsigned and `[−2^(LEN−1), 2^(LEN−1) − 1]` for signed. Compare as doubles *before* calling `llround`, so huge values like 1e12 clamp instead of overflowing.
- Encoding writes the low LEN bits of the two's-complement raw value: clear each target bit, then set it.

## Solution
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

typedef struct {
    char name[32];
    int start, len, be, is_signed;
    double factor, offset;
} Signal;

static Signal sigs[64];
static int nsigs;
static uint8_t frame[8];

static Signal *find(const char *name) {
    for (int i = 0; i < nsigs; i++) if (!strcmp(sigs[i].name, name)) return &sigs[i];
    return NULL;
}

/* pos[i] = frame bit holding raw bit i (i = 0 is the LSB) */
static void positions(const Signal *s, int *pos) {
    if (!s->be) {
        for (int i = 0; i < s->len; i++) pos[i] = s->start + i;
        return;
    }
    int p = s->start;
    for (int i = s->len - 1; i >= 0; i--) {            /* MSB first */
        pos[i] = p;
        p = (p % 8 == 0) ? p + 15 : p - 1;
    }
}

static long long decode_raw(const Signal *s) {
    int pos[32];
    positions(s, pos);
    uint64_t raw = 0;
    for (int i = 0; i < s->len; i++)
        raw |= (uint64_t)((frame[pos[i] / 8] >> (pos[i] % 8)) & 1u) << i;
    if (s->is_signed && (raw >> (s->len - 1)) & 1u) return (long long)raw - (long long)(1ULL << s->len);
    return (long long)raw;
}

static void encode_raw(const Signal *s, long long raw) {
    int pos[32];
    positions(s, pos);
    uint64_t bits = (uint64_t)raw;                     /* two's complement; low len bits are used */
    for (int i = 0; i < s->len; i++) {
        uint8_t m = (uint8_t)(1u << (pos[i] % 8));
        if ((bits >> i) & 1u) frame[pos[i] / 8] |= m;
        else frame[pos[i] / 8] &= (uint8_t)~m;
    }
}

int main(void) {
    char cmd[32], name[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "signal")) {
            Signal *s = &sigs[nsigs];
            char order[4], sign[4];
            if (scanf("%31s %d %d %3s %3s %lf %lf", s->name, &s->start, &s->len, order, sign,
                      &s->factor, &s->offset) != 7) return 1;
            s->be = !strcmp(order, "be");
            s->is_signed = !strcmp(sign, "s");
            Signal *old = find(s->name);
            if (old && old != s) *old = *s; else nsigs++;
        } else if (!strcmp(cmd, "frame")) {
            for (int i = 0; i < 8; i++) {
                unsigned b;
                if (scanf("%x", &b) != 1) return 1;
                frame[i] = (uint8_t)b;
            }
        } else if (!strcmp(cmd, "show")) {
            printf("frame:");
            for (int i = 0; i < 8; i++) printf(" %02X", frame[i]);
            printf("\n");
        } else if (!strcmp(cmd, "decode")) {
            if (scanf("%31s", name) != 1) return 1;
            Signal *s = find(name);
            if (!s) { printf("error: unknown signal %s\n", name); continue; }
            long long raw = decode_raw(s);
            printf("%s = %.3f (raw %lld)\n", s->name, (double)raw * s->factor + s->offset, raw);
        } else if (!strcmp(cmd, "encode")) {
            double value;
            if (scanf("%31s %lf", name, &value) != 2) return 1;
            Signal *s = find(name);
            if (!s) { printf("error: unknown signal %s\n", name); continue; }
            double lo = s->is_signed ? -ldexp(1.0, s->len - 1) : 0.0;
            double hi = s->is_signed ? ldexp(1.0, s->len - 1) - 1 : ldexp(1.0, s->len) - 1;
            double r = (value - s->offset) / s->factor;
            int clamped = 0;
            long long raw;
            if (r < lo - 0.5) { raw = (long long)lo; clamped = 1; }
            else if (r >= hi + 0.5) { raw = (long long)hi; clamped = 1; }
            else {
                raw = llround(r);
                if (raw < (long long)lo) { raw = (long long)lo; clamped = 1; }
                if (raw > (long long)hi) { raw = (long long)hi; clamped = 1; }
            }
            encode_raw(s, raw);
            printf("encode %s -> raw %lld%s\n", s->name, raw, clamped ? " (clamped)" : "");
        }
    }
    return 0;
}
```

The whole codec rests on one idea: map every **raw bit index to a frame bit position**, and both directions become simple loops.
- **Intel** signals occupy consecutive positions, counting upward.
- **Motorola** signals use DBC's "sawtooth" numbering: start at the MSB, walk down to bit 0 of the byte, then jump to bit 7 of the next byte (`p + 15`). Collecting positions from the MSB and filling the array backwards gives the same LSB-first list.

Sign handling is two's complement over LEN bits: decode subtracts 2^LEN when the top bit is set, and encode keeps the low LEN bits of the 64-bit two's-complement value.

The clamp check is done on doubles *before* converting with `llround`. Converting an out-of-range double to an integer is undefined behaviour, and a corrupted setpoint on a real bus could command an actuator to full scale.
