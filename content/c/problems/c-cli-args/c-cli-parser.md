---
id: c-cli-parser
title: A Real Command-Line Option Parser
difficulty: Medium
order: 1
tags: argc, argv, option parsing, strtol, exit codes
---
## Statement
Implement the argument handling of a command-line tool `scan`:

```
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
```

```c
int run(int argc, char **argv);   /* returns the exit status */
```

Rules:
- `-v` / `--verbose` and `-q` / `--quiet` are flags. Short flags may be **grouped** (`-vq`). If both are given, quiet wins.
- `-n COUNT`: COUNT is a separate argument or attached (`-n5`), and must be an integer 1..1000. `--count=N` is the long form.
- `-o FILE` / `-oFILE` / `--output=FILE`.
- `--mode=fast` or `--mode=safe` (default `safe`).
- `--` ends option parsing: everything after it is an input, even if it starts with `-`. A lone `-` is an input (stdin, by convention).
- At least one INPUT is required.
- Defaults: count = 10, output = `-` (stdout).

On success, print `verbose=V quiet=Q count=C output=O mode=M inputs=[a,b,...]` and return 0. On any usage error, print **one** message from the list below **to stdout** (so the tests can see it), then the usage line, and return 2:
`error: unknown option 'X'`, `error: option '-n' needs a value`, `error: invalid count 'X'`, `error: invalid mode 'X'`, `error: no inputs`. (For `-o` without a value, use `error: option '-o' needs a value`.)

The driver splits each input line on spaces into an `argv` array (with `argv[0] = "scan"`), calls `run`, and prints the exit status.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

int run(int argc, char **argv) {
    return 0;
}
```

## Driver
```c
int main(void) {
    char line[1024];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        char *argv[64];
        int argc = 0;
        argv[argc++] = "scan";
        for (char *tok = strtok(line, " "); tok && argc < 63; tok = strtok(NULL, " ")) argv[argc++] = tok;
        argv[argc] = NULL;
        int status = run(argc, argv);
        printf("-> exit %d\n", status);
    }
    return 0;
}
```

## Tests
=== sample
a.txt
-v -n 5 -o out.csv a.txt b.txt
-vq -n7 --mode=fast x
--count=3 --output=res.txt -- -weird.txt -
-n
-n 0 a
-n 12x a
--mode=turbo a
-z a
-v
---
verbose=0 quiet=0 count=10 output=- mode=safe inputs=[a.txt]
-> exit 0
verbose=1 quiet=0 count=5 output=out.csv mode=safe inputs=[a.txt,b.txt]
-> exit 0
verbose=0 quiet=1 count=7 output=- mode=fast inputs=[x]
-> exit 0
verbose=0 quiet=0 count=3 output=res.txt mode=safe inputs=[-weird.txt,-]
-> exit 0
error: option '-n' needs a value
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: invalid count '0'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: invalid count '12x'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: invalid mode 'turbo'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: unknown option '-z'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: no inputs
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
=== hidden
-q -v a
-oFILE --verbose --quiet one two three
-n 1000 a
-n 1001 a
-n -5 a
-n99999999999999999999 a
--count= a
--mode=safe -- --mode=fast
-o
-vx a
--frobnicate a
-
--
---
verbose=0 quiet=1 count=10 output=- mode=safe inputs=[a]
-> exit 0
verbose=0 quiet=1 count=10 output=FILE mode=safe inputs=[one,two,three]
-> exit 0
verbose=0 quiet=0 count=1000 output=- mode=safe inputs=[a]
-> exit 0
error: invalid count '1001'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: invalid count '-5'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: invalid count '99999999999999999999'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: invalid count ''
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
verbose=0 quiet=0 count=10 output=- mode=safe inputs=[--mode=fast]
-> exit 0
error: option '-o' needs a value
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: unknown option '-x'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
error: unknown option '--frobnicate'
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2
verbose=0 quiet=0 count=10 output=- mode=safe inputs=[-]
-> exit 0
error: no inputs
usage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...
-> exit 2

## Hints
- Loop `for (int i = 1; i < argc; i++)`. Once you've seen `--`, everything goes into the inputs.
- For short options, walk the characters of the cluster: `for (char *p = arg + 1; *p; p++)`. For `n` and `o`, the rest of the cluster (`p + 1`) is the value if it's non-empty, otherwise the next argument.
- Validate the count with `strtol`: `errno = 0`, an end pointer at the string's end, at least one digit, and the range 1..1000.
- Collect inputs into an array of `char *`. They can simply point at the existing `argv` strings, with no copying needed.
- Write a small `usage_error(const char *fmt, const char *arg)` helper that prints and returns 2, so each error is a one-line `return`.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

static int usage_error(const char *msg, const char *arg) {
    printf(msg, arg);
    printf("\nusage: scan [-v] [-q] [-n COUNT] [-o FILE] [--mode=fast|safe] [--] INPUT...\n");
    return 2;
}

static int parse_count(const char *s, int *out) {
    char *end;
    errno = 0;
    long v = strtol(s, &end, 10);
    if (end == s || *end != '\0' || errno == ERANGE || v < 1 || v > 1000) return 0;
    *out = (int)v;
    return 1;
}

int run(int argc, char **argv) {
    int verbose = 0, quiet = 0, count = 10;
    const char *output = "-", *mode = "safe";
    const char *inputs[64];
    int ninputs = 0, options_done = 0;

    for (int i = 1; i < argc; i++) {
        const char *arg = argv[i];
        if (options_done || strcmp(arg, "-") == 0 || arg[0] != '-') {
            inputs[ninputs++] = arg;
        } else if (strcmp(arg, "--") == 0) {
            options_done = 1;
        } else if (strncmp(arg, "--", 2) == 0) {                     /* long options */
            if (strcmp(arg, "--verbose") == 0) verbose = 1;
            else if (strcmp(arg, "--quiet") == 0) quiet = 1;
            else if (strncmp(arg, "--count=", 8) == 0) {
                if (!parse_count(arg + 8, &count)) return usage_error("error: invalid count '%s'", arg + 8);
            } else if (strncmp(arg, "--output=", 9) == 0) output = arg + 9;
            else if (strncmp(arg, "--mode=", 7) == 0) {
                mode = arg + 7;
                if (strcmp(mode, "fast") != 0 && strcmp(mode, "safe") != 0)
                    return usage_error("error: invalid mode '%s'", mode);
            } else return usage_error("error: unknown option '%s'", arg);
        } else {                                                     /* short option cluster */
            for (const char *p = arg + 1; *p; p++) {
                if (*p == 'v') verbose = 1;
                else if (*p == 'q') quiet = 1;
                else if (*p == 'n' || *p == 'o') {
                    const char *val = p[1] ? p + 1 : (i + 1 < argc ? argv[++i] : NULL);
                    if (!val) return usage_error(*p == 'n' ? "error: option '-n' needs a value%s"
                                                           : "error: option '-o' needs a value%s", "");
                    if (*p == 'n') {
                        if (!parse_count(val, &count)) return usage_error("error: invalid count '%s'", val);
                    } else {
                        output = val;
                    }
                    break;                                           /* the value consumed the rest */
                } else {
                    char bad[3] = {'-', *p, '\0'};
                    return usage_error("error: unknown option '%s'", bad);
                }
            }
        }
    }
    if (ninputs == 0) return usage_error("error: no inputs%s", "");
    if (quiet) verbose = 0;
    printf("verbose=%d quiet=%d count=%d output=%s mode=%s inputs=[", verbose, quiet, count, output, mode);
    for (int k = 0; k < ninputs; k++) printf("%s%s", k ? "," : "", inputs[k]);
    printf("]\n");
    return 0;
}
```

This mirrors POSIX `getopt` conventions by hand: grouped short flags (`-vq`), attached or separate values (`-n7` and `-n 7`), `--` as the end of options, and a lone `-` as a positional argument. Robust tools validate every value (`strtol` with full checks, not `atoi`), report precisely what went wrong, and exit with status **2** for usage errors so shell scripts can tell "bad invocation" apart from "the work failed" (1). The inputs point straight into `argv`, whose strings live for the whole program, so no copying is needed.
