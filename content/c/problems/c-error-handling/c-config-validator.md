---
id: c-config-validator
title: Robust Config Loader with Error Codes
difficulty: Medium
order: 1
tags: error handling, errno, strtol, status codes, goto cleanup
---
## Statement
Write a config loader in the C error-handling style: every failure is a **status code**, never a crash. Implement:

```c
typedef enum { CFG_OK, CFG_SYNTAX, CFG_UNKNOWN_KEY, CFG_BAD_INT, CFG_RANGE, CFG_DUPLICATE, CFG_MISSING } CfgStatus;
const char *cfg_strerror(CfgStatus s);   /* "ok", "syntax error", "unknown key", "not an integer",
                                            "out of range", "duplicate key", "missing required key" */
typedef struct { int port; int rate_hz; int retries; char name[32]; } Config;
CfgStatus parse_int_range(const char *text, long lo, long hi, int *out);   /* *out set only on success */
CfgStatus cfg_load(FILE *in, Config *cfg, int *err_line);                   /* stops at the FIRST error */
```

Config format: lines `key = value` (spaces around `=` optional). Blank lines and lines starting with `#` are skipped. Keys:

| Key | Rule | Default |
|---|---|---|
| `port` | integer 1..65535, **required** | (none) |
| `rate_hz` | integer 1..1000 | 50 |
| `retries` | integer 0..10 | 3 |
| `name` | 1..31 characters (longer is `CFG_RANGE`) | `"robot"` |

A line without `=`, or with an empty key or value, is a `CFG_SYNTAX` error. Integers must be **fully** numeric (`"12abc"`, `""` and `"1.5"` are `CFG_BAD_INT`; out-of-range or overflowing values are `CFG_RANGE`). A repeated key is `CFG_DUPLICATE`. After the whole file is read, a missing `port` is `CFG_MISSING` with `err_line = 0`. On error, `*cfg` must be left **unchanged** (load into a temporary, then copy on success).

The input contains several config files separated by lines containing only `%%`. The driver writes each one to a temporary file, loads it through a `FILE *`, and prints the result.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <ctype.h>

typedef enum { CFG_OK, CFG_SYNTAX, CFG_UNKNOWN_KEY, CFG_BAD_INT, CFG_RANGE, CFG_DUPLICATE, CFG_MISSING } CfgStatus;
typedef struct { int port; int rate_hz; int retries; char name[32]; } Config;

const char *cfg_strerror(CfgStatus s) { return "ok"; }
CfgStatus parse_int_range(const char *text, long lo, long hi, int *out) { *out = atoi(text); return CFG_OK; }
CfgStatus cfg_load(FILE *in, Config *cfg, int *err_line) { return CFG_OK; }
```

## Driver
```c
static void run_one(const char *text, int idx) {
    FILE *tmp = tmpfile();
    if (!tmp) { perror("tmpfile"); exit(1); }
    fputs(text, tmp);
    rewind(tmp);
    Config cfg = {-1, -1, -1, "untouched"};
    int line = -1;
    CfgStatus s = cfg_load(tmp, &cfg, &line);
    fclose(tmp);
    if (s == CFG_OK)
        printf("#%d ok: port=%d rate_hz=%d retries=%d name=%s\n", idx, cfg.port, cfg.rate_hz, cfg.retries, cfg.name);
    else
        printf("#%d error at line %d: %s (cfg %s)\n", idx, line, cfg_strerror(s),
               strcmp(cfg.name, "untouched") == 0 && cfg.port == -1 ? "unchanged" : "MODIFIED");
}

int main(void) {
    static char buf[1 << 16];
    size_t len = 0;
    char line[512];
    int idx = 0;
    int v;
    printf("parse '42'=%d ", parse_int_range("42", 0, 100, &v)); printf("v=%d\n", v);
    v = 7;
    printf("parse '12abc'=%d '-5'(0..9)=%d '99999999999999999999'=%d '' =%d v still %d\n",
           parse_int_range("12abc", 0, 100, &v), parse_int_range("-5", 0, 9, &v),
           parse_int_range("99999999999999999999", 0, 100, &v), parse_int_range("", 0, 1, &v), v);
    while (fgets(line, sizeof line, stdin)) {
        if (strcmp(line, "%%\n") == 0 || strcmp(line, "%%") == 0) {
            buf[len] = '\0';
            run_one(buf, ++idx);
            len = 0;
            continue;
        }
        size_t n = strlen(line);
        memcpy(buf + len, line, n);
        len += n;
    }
    buf[len] = '\0';
    run_one(buf, ++idx);
    return 0;
}
```

## Tests
=== sample
# robot config
port = 8080
rate_hz=200
name = rover-7
%%
port = 80
retries = 11
%%
rate_hz = 10
%%
port = 1
port = 2
%%
port = 70000
%%
port 8080
%%
port = 9000
speed = 3
---
parse '42'=0 v=42
parse '12abc'=3 '-5'(0..9)=4 '99999999999999999999'=4 '' =3 v still 7
#1 ok: port=8080 rate_hz=200 retries=3 name=rover-7
#2 error at line 2: out of range (cfg unchanged)
#3 error at line 0: missing required key (cfg unchanged)
#4 error at line 2: duplicate key (cfg unchanged)
#5 error at line 1: out of range (cfg unchanged)
#6 error at line 1: syntax error (cfg unchanged)
#7 error at line 2: unknown key (cfg unchanged)
=== hidden
port=65535
retries=0
rate_hz=1000
name=a_name_that_is_exactly_31_chars
%%
port = 1
name = a_name_that_is_definitely_32_chr
%%
port = 1.5
%%
port =
%%
 = 5
%%

   
# only comments
%%
port = 22
rate_hz = 0
%%
port = -1
%%
port = 443
name = x
retries = 2
---
parse '42'=0 v=42
parse '12abc'=3 '-5'(0..9)=4 '99999999999999999999'=4 '' =3 v still 7
#1 ok: port=65535 rate_hz=1000 retries=0 name=a_name_that_is_exactly_31_chars
#2 error at line 2: out of range (cfg unchanged)
#3 error at line 1: not an integer (cfg unchanged)
#4 error at line 1: syntax error (cfg unchanged)
#5 error at line 1: syntax error (cfg unchanged)
#6 error at line 0: missing required key (cfg unchanged)
#7 error at line 2: out of range (cfg unchanged)
#8 error at line 1: out of range (cfg unchanged)
#9 ok: port=443 rate_hz=50 retries=2 name=x

## Hints
- `parse_int_range`: `errno = 0; char *end; long v = strtol(text, &end, 10);`, then: no digits (`end == text`) or trailing junk (`*end != '\0'`) means `CFG_BAD_INT`, and `errno == ERANGE`, `v < lo` or `v > hi` means `CFG_RANGE`. Only then write `*out`.
- Trim whitespace from the key and value (and strip the trailing `'\n'`) before checking them.
- Use a local `Config tmp = {0, 50, 3, "robot"}` plus "seen" flags. Copy `*cfg = tmp` only when everything succeeded.
- Count lines from 1 for `err_line`.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <ctype.h>

typedef enum { CFG_OK, CFG_SYNTAX, CFG_UNKNOWN_KEY, CFG_BAD_INT, CFG_RANGE, CFG_DUPLICATE, CFG_MISSING } CfgStatus;
typedef struct { int port; int rate_hz; int retries; char name[32]; } Config;

const char *cfg_strerror(CfgStatus s) {
    static const char *msgs[] = {"ok", "syntax error", "unknown key", "not an integer",
                                 "out of range", "duplicate key", "missing required key"};
    return (s >= CFG_OK && s <= CFG_MISSING) ? msgs[s] : "unknown error";
}

CfgStatus parse_int_range(const char *text, long lo, long hi, int *out) {
    char *end;
    errno = 0;
    long v = strtol(text, &end, 10);
    if (end == text || *end != '\0') return CFG_BAD_INT;
    if (errno == ERANGE || v < lo || v > hi) return CFG_RANGE;
    *out = (int)v;                                   /* only on success */
    return CFG_OK;
}

static char *trim(char *s) {
    while (isspace((unsigned char)*s)) s++;
    char *e = s + strlen(s);
    while (e > s && isspace((unsigned char)e[-1])) *--e = '\0';
    return s;
}

CfgStatus cfg_load(FILE *in, Config *cfg, int *err_line) {
    Config tmp = {0, 50, 3, "robot"};
    int seen_port = 0, seen_rate = 0, seen_retries = 0, seen_name = 0;
    char line[512];
    int lineno = 0;
    CfgStatus st = CFG_OK;

    while (fgets(line, sizeof line, in)) {
        lineno++;
        char *t = trim(line);
        if (*t == '\0' || *t == '#') continue;
        char *eq = strchr(t, '=');
        if (!eq) { st = CFG_SYNTAX; goto fail; }
        *eq = '\0';
        char *key = trim(t), *val = trim(eq + 1);
        if (*key == '\0' || *val == '\0') { st = CFG_SYNTAX; goto fail; }

        if (strcmp(key, "port") == 0) {
            if (seen_port++) { st = CFG_DUPLICATE; goto fail; }
            if ((st = parse_int_range(val, 1, 65535, &tmp.port)) != CFG_OK) goto fail;
        } else if (strcmp(key, "rate_hz") == 0) {
            if (seen_rate++) { st = CFG_DUPLICATE; goto fail; }
            if ((st = parse_int_range(val, 1, 1000, &tmp.rate_hz)) != CFG_OK) goto fail;
        } else if (strcmp(key, "retries") == 0) {
            if (seen_retries++) { st = CFG_DUPLICATE; goto fail; }
            if ((st = parse_int_range(val, 0, 10, &tmp.retries)) != CFG_OK) goto fail;
        } else if (strcmp(key, "name") == 0) {
            if (seen_name++) { st = CFG_DUPLICATE; goto fail; }
            if (strlen(val) > 31) { st = CFG_RANGE; goto fail; }
            strcpy(tmp.name, val);
        } else {
            st = CFG_UNKNOWN_KEY;
            goto fail;
        }
    }
    if (!seen_port) { lineno = 0; st = CFG_MISSING; goto fail; }
    *cfg = tmp;                                      /* commit only on full success */
    return CFG_OK;

fail:
    *err_line = lineno;
    return st;
}
```

- **Status codes plus a message table** (`cfg_strerror`) are the C error-reporting idiom (compare `errno`/`strerror` and `sqlite3_errstr`).
- **`strtol` done right:** clearing `errno` first, checking the end pointer for "no digits" and trailing junk, and checking `ERANGE` for overflow. That rejects exactly what `atoi` would silently accept.
- **Transactional updates:** the configuration is built in `tmp` and committed in one assignment, so a failure leaves the caller's `Config` untouched (the driver verifies "unchanged"). That's the strong exception guarantee, done by hand.
- **A single error exit** (`goto fail`) records the line and returns the status from one place.

