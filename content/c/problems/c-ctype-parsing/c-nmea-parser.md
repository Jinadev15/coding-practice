---
id: c-nmea-parser
title: GPS Sentence Parser
difficulty: Hard
order: 1
tags: parsing, checksums, strtod, robotics
---
## Statement
GPS receivers on robots stream **NMEA** sentences like:

```text
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
```

Parse simplified `GPGGA` sentences, one per line:

1. The line starts with `$` and contains `*` followed by **two hex digits**: the checksum.
2. The checksum is the XOR of every character strictly between `$` and `*`. If it doesn't match, print `bad checksum`.
3. Fields are comma-separated. **Empty fields are allowed**, so don't use `strtok`. Field 0 must be `GPGGA`, otherwise print `unsupported`.
4. Field 2 is latitude `ddmm.mmmm` with field 3 `N`/`S`; field 4 is longitude `dddmm.mmmm` with field 5 `E`/`W`. Convert to decimal degrees: `deg + minutes/60`, negative for S/W.
5. Field 6 is the fix quality (int); field 7 is the satellite count; field 9 is the altitude in metres.

Output `lat=%.6f lon=%.6f fix=%d sats=%d alt=%.1f`. If the fix quality is 0 or the latitude field is empty, print `no fix`. Anything else malformed prints `malformed`.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main(void) {
    char line[256];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = '\0';

    }
    return 0;
}
```

## Tests
=== sample
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*48
$GPRMC,1,2*48
---
lat=48.117300 lon=11.516667 fix=1 sats=8 alt=545.4
bad checksum
unsupported
=== hidden
$GPGGA,000000,,,,,0,00,,,M,,M,,*66
$GPGGA,120000,3345.500,S,07040.250,W,2,12,1.1,10.0,M,0,M,,*51
GPGGA,1*00
---
no fix
lat=-33.758333 lon=-70.670833 fix=2 sats=12 alt=10.0
malformed

## Hints
- Find `*` with `strrchr`. Compute the XOR over `line+1 .. star-1` and parse the two hex digits with `strtol(star+1, &end, 16)`.
- Split manually: walk the string, recording the start of each field and replacing `,` with `'\0'` (or store start/length pairs). Keep empty fields.
- Latitude: `v = strtod(field, NULL); deg = (int)(v / 100); min = v - deg*100;`.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

static double to_degrees(const char *f, const char *hemi) {
    double v = strtod(f, NULL);
    int deg = (int)(v / 100);
    double d = deg + (v - deg * 100) / 60.0;
    return (hemi[0] == 'S' || hemi[0] == 'W') ? -d : d;
}

int main(void) {
    char line[256];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = '\0';
        char *star = strrchr(line, '*');
        if (line[0] != '$' || !star || !isxdigit((unsigned char)star[1])
            || !isxdigit((unsigned char)star[2]) || star[3] != '\0') {
            puts("malformed");
            continue;
        }
        unsigned sum = 0;
        for (char *p = line + 1; p < star; p++) sum ^= (unsigned char)*p;
        unsigned given = (unsigned)strtol(star + 1, NULL, 16);
        if (sum != given) { puts("bad checksum"); continue; }
        *star = '\0';
        char *fields[32];
        int nf = 0;
        char *p = line + 1;
        fields[nf++] = p;
        for (; *p && nf < 32; p++) {
            if (*p == ',') { *p = '\0'; fields[nf++] = p + 1; }
        }
        if (strcmp(fields[0], "GPGGA") != 0) { puts("unsupported"); continue; }
        if (nf < 10) { puts("malformed"); continue; }
        int fix = atoi(fields[6]);
        if (fix == 0 || fields[2][0] == '\0') { puts("no fix"); continue; }
        printf("lat=%.6f lon=%.6f fix=%d sats=%d alt=%.1f\n",
               to_degrees(fields[2], fields[3]), to_degrees(fields[4], fields[5]),
               fix, atoi(fields[7]), strtod(fields[9], NULL));
    }
    return 0;
}
```

Splitting in place, by recording field starts and overwriting commas with `'\0'`, keeps empty fields and needs no extra memory. That's exactly what `strtok` gets wrong. The checksum detects corruption on noisy serial links. `atoi` is acceptable for the fix and satellite fields here only because the checksum already guarantees the sentence is intact. In general, prefer `strtol`.
