---
id: c-defensive-imu-parser
title: A Defensive IMU Frame Parser
difficulty: Hard
order: 1
tags: defensive programming, MISRA, CRC-16, bounds checking, validation, fuzzing
time_limit: 4
---
## Statement
A flight controller receives IMU frames over a noisy UART. Write the parser in safety-critical style: validate **everything**, never read outside the buffer, and report a precise status. The judge **fuzzes** your parser with millions of corrupted frames. Each buffer ends exactly at an unmapped guard page, so reading even one byte past `len` crashes.

**Frame (18 bytes):**

| Bytes | Content |
|---|---|
| 0–1 | sync `0x55 0xAA` |
| 2 | type, must be `0x01` |
| 3 | sequence number `seq` (u8) |
| 4–9 | accel x, y, z: `int16` little-endian, raw counts |
| 10–15 | gyro x, y, z: `int16` little-endian |
| 16–17 | CRC-16/CCITT-FALSE of bytes 0–15, **big-endian** |

CRC-16/CCITT-FALSE: polynomial `0x1021`, initial value `0xFFFF`, no reflection, no final XOR. `crc16_ccitt("123456789")` is `0x29B1`.

```c
typedef enum { IMU_OK, IMU_ERR_NULL, IMU_ERR_LEN, IMU_ERR_SYNC, IMU_ERR_TYPE,
               IMU_ERR_CRC, IMU_ERR_RANGE, IMU_ERR_SEQ } ImuStatus;
typedef struct { uint8_t seq; int32_t accel_mg[3]; int32_t gyro_mdps[3]; } ImuSample;
typedef struct { bool has_seq; uint8_t last_seq; uint32_t errors[8]; } ImuParser;
```

`ImuStatus imu_parse(ImuParser *p, const uint8_t *buf, size_t len, ImuSample *out)` checks in this order and returns the **first** failure:
1. `IMU_ERR_NULL`: `p`, `buf` or `out` is NULL. Return immediately and touch nothing, not even the counters.
2. `IMU_ERR_LEN`: `len != 18`.
3. `IMU_ERR_SYNC`: wrong sync bytes.
4. `IMU_ERR_TYPE`: type isn't `0x01`.
5. `IMU_ERR_CRC`: CRC mismatch.
6. `IMU_ERR_RANGE`: any accel raw value outside `[-16384, 16384]`, or any gyro raw value outside `[-30000, 30000]`.
7. `IMU_ERR_SEQ`: a sequence number was seen before (`has_seq`) and `seq != (last_seq + 1) mod 256`. The data is still valid: fill `out` and update `last_seq`, but return `IMU_ERR_SEQ` so packet loss is reported.

Rules:
- On `IMU_OK` or `IMU_ERR_SEQ`, fill `out`:
  - `accel_mg = raw * 1000 / 8192`
  - `gyro_mdps = raw * 1000 / 131`

  Both use C's truncating `int32_t` division. Then set `has_seq = true` and `last_seq = seq`.
- On every other error, `out` and the sequence state are **unchanged**.
- For every status except `IMU_ERR_NULL`, increment `p->errors[status]`. `errors[IMU_OK]` counts good frames.
- `void imu_parser_init(ImuParser *p)` zeroes the parser. `uint16_t crc16_ccitt(const uint8_t *d, size_t n)` is tested directly.

## Starter
```c
#define _DEFAULT_SOURCE
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef enum { IMU_OK, IMU_ERR_NULL, IMU_ERR_LEN, IMU_ERR_SYNC, IMU_ERR_TYPE,
               IMU_ERR_CRC, IMU_ERR_RANGE, IMU_ERR_SEQ } ImuStatus;
typedef struct { uint8_t seq; int32_t accel_mg[3]; int32_t gyro_mdps[3]; } ImuSample;
typedef struct { bool has_seq; uint8_t last_seq; uint32_t errors[8]; } ImuParser;

void imu_parser_init(ImuParser *p) { memset(p, 0, sizeof *p); }

uint16_t crc16_ccitt(const uint8_t *d, size_t n) {
    uint16_t c = 0;
    for (size_t i = 0; i < n; i++) c += d[i];
    return c;
}

ImuStatus imu_parse(ImuParser *p, const uint8_t *buf, size_t len, ImuSample *out) {
    if (buf[0] != 0x55 || buf[1] != 0xAA) return IMU_ERR_SYNC;
    out->seq = buf[3];
    for (int i = 0; i < 3; i++) {
        out->accel_mg[i] = *(const int16_t *)(buf + 4 + 2 * i) * 1000 / 8192;
        out->gyro_mdps[i] = *(const int16_t *)(buf + 10 + 2 * i) * 1000 / 131;
    }
    (void)p; (void)len;
    return IMU_OK;
}
```

## Driver
```c
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

static uint8_t *page;          /* [page][guard]: buffers end at the guard */
static long psz;
static uint8_t *place(const uint8_t *src, size_t len) {
    uint8_t *p = page + psz - len;
    if (len) memcpy(p, src, len);
    return p;
}
static uint32_t x = 2463534242u;
static uint32_t rnd(void) { x ^= x << 13; x ^= x >> 17; x ^= x << 5; return x; }
static uint16_t ref_crc(const uint8_t *d, size_t n) {
    uint16_t c = 0xFFFF;
    for (size_t i = 0; i < n; i++) { c ^= (uint16_t)(d[i] << 8); for (int b = 0; b < 8; b++) c = (c & 0x8000) ? (uint16_t)((c << 1) ^ 0x1021) : (uint16_t)(c << 1); }
    return c;
}
static void make(uint8_t f[18], uint8_t seq, const int16_t a[3], const int16_t g[3]) {
    f[0] = 0x55; f[1] = 0xAA; f[2] = 1; f[3] = seq;
    for (int i = 0; i < 3; i++) {
        f[4 + 2 * i] = (uint8_t)a[i]; f[5 + 2 * i] = (uint8_t)((uint16_t)a[i] >> 8);
        f[10 + 2 * i] = (uint8_t)g[i]; f[11 + 2 * i] = (uint8_t)((uint16_t)g[i] >> 8);
    }
    uint16_t c = ref_crc(f, 16); f[16] = (uint8_t)(c >> 8); f[17] = (uint8_t)c;
}
static const char *NAMES[] = {"OK", "NULL", "LEN", "SYNC", "TYPE", "CRC", "RANGE", "SEQ"};
static void show(ImuStatus st, const ImuSample *s) {
    printf("%-5s seq=%u a=(%d,%d,%d) g=(%d,%d,%d)\n", (unsigned)st < 8 ? NAMES[st] : "?", s->seq,
           s->accel_mg[0], s->accel_mg[1], s->accel_mg[2], s->gyro_mdps[0], s->gyro_mdps[1], s->gyro_mdps[2]);
}

int main(void) {
    psz = sysconf(_SC_PAGESIZE);
    page = mmap(NULL, (size_t)psz * 2, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (page == MAP_FAILED || mprotect(page + psz, (size_t)psz, PROT_NONE)) return 1;
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        ImuParser P; imu_parser_init(&P);
        ImuSample S; memset(&S, 0, sizeof S);
        if (!strcmp(cmd, "crc")) {
            printf("%04x %04x %04x\n", crc16_ccitt((const uint8_t *)"123456789", 9), crc16_ccitt(place(NULL, 0), 0),
                   crc16_ccitt(place((const uint8_t *)"\x55\xAA", 2), 2));
        } else if (!strcmp(cmd, "good")) {
            uint8_t f[18]; int16_t a[3] = {8192, -4096, 16384}, g[3] = {131, -262, -30000};
            make(f, 7, a, g); show(imu_parse(&P, place(f, 18), 18, &S), &S);
            int16_t a2[3] = {1, -1, -16384}, g2[3] = {130, -130, 29999};
            make(f, 8, a2, g2); show(imu_parse(&P, place(f, 18), 18, &S), &S);
            make(f, 10, a, g2); show(imu_parse(&P, place(f, 18), 18, &S), &S);
            make(f, 11, a, g); show(imu_parse(&P, place(f, 18), 18, &S), &S);
            make(f, 0, a, g); P.last_seq = 255; show(imu_parse(&P, place(f, 18), 18, &S), &S);
        } else if (!strcmp(cmd, "errors")) {
            uint8_t f[18], b[18]; int16_t a[3] = {100, 200, 300}, g[3] = {-1, -2, -3};
            make(f, 1, a, g); show(imu_parse(&P, place(f, 18), 18, &S), &S);
            printf("null: %s %s %s\n", NAMES[imu_parse(NULL, f, 18, &S)], NAMES[imu_parse(&P, NULL, 18, &S)], NAMES[imu_parse(&P, f, 18, NULL)]);
            printf("len0 %s len1 %s len17 %s\n", NAMES[imu_parse(&P, place(f, 0), 0, &S)], NAMES[imu_parse(&P, place(f, 1), 1, &S)],
                   NAMES[imu_parse(&P, place(f, 17), 17, &S)]);
            memcpy(b, f, 18); b[1] = 0xAB; printf("sync %s\n", NAMES[imu_parse(&P, place(b, 18), 18, &S)]);
            memcpy(b, f, 18); b[2] = 2; printf("type %s\n", NAMES[imu_parse(&P, place(b, 18), 18, &S)]);
            memcpy(b, f, 18); b[9] ^= 0x10; printf("crc %s\n", NAMES[imu_parse(&P, place(b, 18), 18, &S)]);
            int16_t ab[3] = {100, 16385, 0}; make(b, 2, ab, g); printf("range %s\n", NAMES[imu_parse(&P, place(b, 18), 18, &S)]);
            int16_t gb[3] = {0, 0, -30001}; make(b, 2, a, gb); printf("range %s\n", NAMES[imu_parse(&P, place(b, 18), 18, &S)]);
            show(IMU_OK, &S);
            printf("counters:"); for (int i = 0; i < 8; i++) printf(" %u", P.errors[i]); printf(" last=%u\n", P.last_seq);
        } else if (!strcmp(cmd, "fuzz")) {
            unsigned long n; if (scanf("%lu", &n) != 1) return 1;
            uint64_t h = 1469598103934665603ull; uint8_t f[40];
            for (unsigned long i = 0; i < n; i++) {
                int16_t a[3], g[3];
                for (int k = 0; k < 3; k++) { a[k] = (int16_t)(rnd() % 34000) - 17000; g[k] = (int16_t)(rnd() % 62000) - 31000; }
                if (rnd() % 3) for (int k = 0; k < 3; k++) { a[k] /= 2; g[k] /= 2; }
                make(f, (uint8_t)(i + (rnd() % 16 == 0)), a, g);
                size_t len = 18; uint32_t m = rnd() % 12;
                if (m == 0) len = rnd() % 18;
                else if (m == 1) len = 19 + rnd() % 20;
                else if (m == 2) f[rnd() % 18] ^= (uint8_t)(1u << (rnd() % 8));
                else if (m == 3) f[rnd() % 3] = (uint8_t)rnd();
                if (len > 18) for (size_t k = 18; k < len; k++) f[k] = (uint8_t)rnd();
                ImuStatus st = imu_parse(&P, place(f, len), len, &S);
                h = (h ^ (uint64_t)st) * 1099511628211ull;
                h = (h ^ (uint32_t)(S.accel_mg[0] + 7 * S.gyro_mdps[2] + 31 * S.seq)) * 1099511628211ull;
            }
            printf("fuzz %016llx\ncounters:", (unsigned long long)h);
            for (int i = 0; i < 8; i++) printf(" %u", P.errors[i]);
            printf("\n");
        }
    }
    return 0;
}
```

## Tests
=== sample
crc
good
---
29b1 ffff f8e5
OK    seq=7 a=(1000,-500,2000) g=(1000,-2000,-229007)
OK    seq=8 a=(0,0,-2000) g=(992,-992,229000)
SEQ   seq=10 a=(1000,-500,2000) g=(992,-992,229000)
OK    seq=11 a=(1000,-500,2000) g=(1000,-2000,-229007)
OK    seq=0 a=(1000,-500,2000) g=(1000,-2000,-229007)
=== hidden
errors
---
OK    seq=1 a=(12,24,36) g=(-7,-15,-22)
null: NULL NULL NULL
len0 LEN len1 LEN len17 LEN
sync SYNC
type TYPE
crc CRC
range RANGE
range RANGE
OK    seq=1 a=(12,24,36) g=(-7,-15,-22)
counters: 1 0 3 1 1 1 2 0 last=1
=== hidden
fuzz 1500000
---
fuzz a57b4aa38244112f
counters: 529251 0 250096 96967 48653 104591 62843 407599

## Hints
- Bitwise CRC-16: `crc ^= (uint16_t)(byte << 8)`, then 8 times: if the top bit is set, `crc = (crc << 1) ^ 0x1021`, else `crc <<= 1`. Keep it `uint16_t`.
- Check `len` **before** reading any byte. A 0-byte buffer sits right at the guard page.
- Assemble little-endian values with shifts: `(int16_t)(uint16_t)(b[i] | (b[i+1] << 8))`. Don't cast `buf + 4` to `int16_t *`: that's a misaligned access and a strict-aliasing violation.
- Compute the whole sample into a local `ImuSample`, and copy it to `*out` only once every check has passed.
- Count with a helper `static ImuStatus done(ImuParser *p, ImuStatus s) { p->errors[s]++; return s; }`.

## Solution
```c
#define _DEFAULT_SOURCE
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef enum { IMU_OK, IMU_ERR_NULL, IMU_ERR_LEN, IMU_ERR_SYNC, IMU_ERR_TYPE,
               IMU_ERR_CRC, IMU_ERR_RANGE, IMU_ERR_SEQ } ImuStatus;
typedef struct { uint8_t seq; int32_t accel_mg[3]; int32_t gyro_mdps[3]; } ImuSample;
typedef struct { bool has_seq; uint8_t last_seq; uint32_t errors[8]; } ImuParser;

#define IMU_FRAME_LEN   ((size_t)18u)
#define IMU_ACCEL_MAX   ((int32_t)16384)
#define IMU_GYRO_MAX    ((int32_t)30000)

void imu_parser_init(ImuParser *p) { (void)memset(p, 0, sizeof *p); }

uint16_t crc16_ccitt(const uint8_t *d, size_t n) {
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0u; i < n; i++) {
        crc ^= (uint16_t)((uint16_t)d[i] << 8);
        for (uint32_t b = 0u; b < 8u; b++) {
            crc = ((crc & 0x8000u) != 0u) ? (uint16_t)((uint16_t)(crc << 1) ^ 0x1021u) : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

static int32_t le16(const uint8_t *b) {
    return (int32_t)(int16_t)(uint16_t)((uint16_t)b[0] | (uint16_t)((uint16_t)b[1] << 8));
}

static ImuStatus done(ImuParser *p, ImuStatus s) {
    p->errors[s]++;
    return s;
}

ImuStatus imu_parse(ImuParser *p, const uint8_t *buf, size_t len, ImuSample *out) {
    if ((p == NULL) || (buf == NULL) || (out == NULL)) { return IMU_ERR_NULL; }
    if (len != IMU_FRAME_LEN) { return done(p, IMU_ERR_LEN); }          /* before touching any byte */
    if ((buf[0] != 0x55u) || (buf[1] != 0xAAu)) { return done(p, IMU_ERR_SYNC); }
    if (buf[2] != 0x01u) { return done(p, IMU_ERR_TYPE); }
    const uint16_t want = (uint16_t)(((uint16_t)buf[16] << 8) | (uint16_t)buf[17]);
    if (crc16_ccitt(buf, 16u) != want) { return done(p, IMU_ERR_CRC); }

    ImuSample s;
    s.seq = buf[3];
    for (size_t i = 0u; i < 3u; i++) {
        const int32_t a = le16(&buf[4u + (2u * i)]);
        const int32_t g = le16(&buf[10u + (2u * i)]);
        if ((a < -IMU_ACCEL_MAX) || (a > IMU_ACCEL_MAX) || (g < -IMU_GYRO_MAX) || (g > IMU_GYRO_MAX)) {
            return done(p, IMU_ERR_RANGE);                               /* out untouched */
        }
        s.accel_mg[i] = (a * 1000) / 8192;
        s.gyro_mdps[i] = (g * 1000) / 131;
    }

    const bool gap = p->has_seq && (s.seq != (uint8_t)(p->last_seq + 1u));
    *out = s;                                                            /* commit only valid data */
    p->has_seq = true;
    p->last_seq = s.seq;
    return done(p, gap ? IMU_ERR_SEQ : IMU_OK);
}
```

- **Check the length before reading.** The starter reads `buf[0]` on a 0-byte buffer and crashes on the guard page. Real UART drivers hand over short frames all the time.
- **Validate in layers**: framing (length, sync, type), then integrity (CRC), then plausibility (physical range), then continuity (sequence). Each layer only runs on data the previous one accepted, and each failure has its own counter for telemetry.
- **Shift-assembled integers** are endian-independent and alignment-safe. The starter's `*(const int16_t *)(buf + 4)` is misaligned (it can fault on Cortex-M0) and violates strict aliasing.
- **Commit-at-end**: everything is decoded into a local first, so a frame rejected for range never half-overwrites the last good sample that the control loop is using.
- **No overflow by construction**: raw values are within ±30000 after the range check, so `raw * 1000` fits easily in `int32_t`.
- **MISRA style**: explicit comparisons, unsigned constants, an enum status, no dynamic memory, and bounded loops.
