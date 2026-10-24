---
id: c-telemetry-codec
title: Binary Telemetry Packet Codec
difficulty: Hard
order: 1
tags: endianness, bit masks, serialisation, checksums
---
## Statement
A robot sends telemetry as binary packets, transmitted here as hex strings. Write a portable **decoder and encoder** using shifts and masks: **no struct casting and no bit fields**.

Packet layout (16 bytes, multi-byte fields **big-endian**):

| Offset | Size | Field |
|---|---|---|
| 0 | 1 | magic, must be `0xA5` |
| 1 | 1 | flags: bit 7 = `armed`, bit 6 = `fault`, bits 5–3 = `mode` (0–7), bits 2–0 = `battery_level` (0–7) |
| 2 | 2 | sequence number (uint16) |
| 4 | 4 | timestamp in ms (uint32) |
| 8 | 2 | x position in cm (**int16**, two's complement) |
| 10 | 2 | y position in cm (int16) |
| 12 | 2 | heading in centidegrees (uint16, 0–35999) |
| 14 | 1 | reserved, must be 0 |
| 15 | 1 | checksum: XOR of bytes 0–14 |

Commands, one per line:
- `decode HEX32` prints `seq=S t=T armed=A fault=F mode=M batt=B x=X y=Y heading=H.HH`, or `invalid: REASON`, where REASON is the first failing check in this order: `length` (not exactly 32 hex digits), `hex` (a non-hex character), `magic`, `reserved`, `checksum`, `heading`.
- `encode SEQ T ARMED FAULT MODE BATT X Y HEADING_CENTIDEG` prints the 32-digit uppercase hex packet (with the correct checksum).

## Starter
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        /* TODO */
    }
    return 0;
}
```

## Tests
=== sample
encode 1 1000 1 0 3 5 -150 220 9000
decode A59D0001000003E8FF6A00DC23280090
decode A59D0001000003E8FF6A00DC23280091
decode A5
decode B59D0001000003E8FF6A00DC23280090
decode A59D0001000003E8FF6AXXDC23280090
decode A59D0001000003E8FF6A00DC8CA000B7
---
A59D0001000003E8FF6A00DC23280090
seq=1 t=1000 armed=1 fault=0 mode=3 batt=5 x=-150 y=220 heading=90.00
invalid: checksum
invalid: length
invalid: magic
invalid: hex
invalid: heading
=== hidden
encode 65535 4294967295 0 1 7 7 -32768 32767 35999
encode 0 0 0 0 0 0 0 0 0
decode A5000000000000000000000000000000
decode a50000000000000000000000000000a5
decode A59D0001000003E8FF6A00DC23280191
decode A5FF00070000000980007FFF8C9F0047
decode A5401234DEADBEEFFFFF0001000000E0
decode A59D0001000003E8FF6A00DC232800900
decode A59D0001000003E8FF6A00DC8CA00000
---
A57FFFFFFFFFFFFF80007FFF8C9F00C9
A50000000000000000000000000000A5
invalid: checksum
seq=0 t=0 armed=0 fault=0 mode=0 batt=0 x=0 y=0 heading=0.00
invalid: reserved
seq=7 t=9 armed=1 fault=1 mode=7 batt=7 x=-32768 y=32767 heading=359.99
seq=4660 t=3735928559 armed=0 fault=1 mode=0 batt=0 x=-1 y=1 heading=0.00
invalid: length
invalid: checksum

## Hints
- Hex to bytes: two characters per byte. A tiny helper `hexval(c)` returns 0–15 or -1.
- Big-endian reads: `(uint16_t)(b[i] << 8 | b[i+1])` and the four-byte version. For a signed int16, read it as `uint16_t` then convert: `(int16_t)u` is implementation-defined before C23, so compute `u >= 0x8000 ? (int)u - 0x10000 : (int)u` to be fully portable.
- Flags: `armed = b >> 7 & 1`, `fault = b >> 6 & 1`, `mode = b >> 3 & 7`, `batt = b & 7`. Encoding is the reverse: `armed << 7 | fault << 6 | mode << 3 | batt`.
- Print the heading as `h / 100` and `h % 100` with `%u.%02u` to avoid floating-point formatting issues.

## Solution
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>

static int hexval(int c) {
    if (c >= '0' && c <= '9') return c - '0';
    c = toupper(c);
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static uint16_t be16(const uint8_t *p) { return (uint16_t)(p[0] << 8 | p[1]); }
static uint32_t be32(const uint8_t *p) {
    return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3];
}
static void put16(uint8_t *p, uint16_t v) { p[0] = (uint8_t)(v >> 8); p[1] = (uint8_t)v; }
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v >> 24); p[1] = (uint8_t)(v >> 16); p[2] = (uint8_t)(v >> 8); p[3] = (uint8_t)v;
}
static int as_int16(uint16_t u) { return u >= 0x8000 ? (int)u - 0x10000 : (int)u; }
static uint8_t xor_sum(const uint8_t *b, int n) {
    uint8_t c = 0;
    for (int i = 0; i < n; i++) c ^= b[i];
    return c;
}

static void decode(const char *hex) {
    uint8_t b[16];
    if (strlen(hex) != 32) { puts("invalid: length"); return; }
    for (int i = 0; i < 16; i++) {
        int hi = hexval((unsigned char)hex[2 * i]), lo = hexval((unsigned char)hex[2 * i + 1]);
        if (hi < 0 || lo < 0) { puts("invalid: hex"); return; }
        b[i] = (uint8_t)(hi << 4 | lo);
    }
    if (b[0] != 0xA5) { puts("invalid: magic"); return; }
    if (b[14] != 0) { puts("invalid: reserved"); return; }
    if (xor_sum(b, 15) != b[15]) { puts("invalid: checksum"); return; }
    unsigned heading = be16(b + 12);
    if (heading > 35999) { puts("invalid: heading"); return; }
    uint8_t f = b[1];
    printf("seq=%u t=%lu armed=%u fault=%u mode=%u batt=%u x=%d y=%d heading=%u.%02u\n",
           be16(b + 2), (unsigned long)be32(b + 4), f >> 7 & 1u, f >> 6 & 1u, f >> 3 & 7u, f & 7u,
           as_int16(be16(b + 8)), as_int16(be16(b + 10)), heading / 100, heading % 100);
}

static void encode(void) {
    unsigned seq, armed, fault, mode, batt, heading;
    unsigned long t;
    int x, y;
    if (scanf("%u %lu %u %u %u %u %d %d %u", &seq, &t, &armed, &fault, &mode, &batt, &x, &y, &heading) != 9) return;
    uint8_t b[16] = {0};
    b[0] = 0xA5;
    b[1] = (uint8_t)((armed & 1) << 7 | (fault & 1) << 6 | (mode & 7) << 3 | (batt & 7));
    put16(b + 2, (uint16_t)seq);
    put32(b + 4, (uint32_t)t);
    put16(b + 8, (uint16_t)(x & 0xFFFF));          /* two's complement bit pattern */
    put16(b + 10, (uint16_t)(y & 0xFFFF));
    put16(b + 12, (uint16_t)heading);
    b[15] = xor_sum(b, 15);
    for (int i = 0; i < 16; i++) printf("%02X", b[i]);
    putchar('\n');
}

int main(void) {
    char cmd[16], hex[128];
    while (scanf("%15s", cmd) == 1) {
        if (strcmp(cmd, "encode") == 0) encode();
        else if (strcmp(cmd, "decode") == 0 && scanf("%127s", hex) == 1) decode(hex);
    }
    return 0;
}
```

**Why shifts instead of casting a struct onto the buffer:**
- **Endianness:** `be16` and `be32` assemble values from bytes explicitly, so the code gives the same result on little-endian x86, big-endian PowerPC and any ARM.
- **Alignment and padding:** a `struct` overlay would have padding (`uint32_t` at offset 4 is fine, but compilers may pad elsewhere) and misaligned accesses, and the layout of bit fields for `flags` is implementation-defined.
- **Signedness:** `as_int16` converts the 16-bit two's-complement pattern without relying on implementation-defined narrowing conversions.
- **Validation order** matters in real protocol stacks: cheap structural checks first, then integrity (the checksum), then semantic checks (the heading range).

The same techniques decode CAN frames, MAVLink drone packets, and sensor registers read over I²C/SPI.
