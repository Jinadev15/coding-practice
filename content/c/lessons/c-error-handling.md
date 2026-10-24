# Error Handling in C

C has no exceptions. Every failure must be **reported through return values** and **checked by the caller**: `malloc` returns NULL, `fopen` returns NULL and sets `errno`, `read` returns -1. That makes error handling explicit, but verbose and easy to forget, and an ignored error usually becomes a crash or corruption far from its cause. This lesson covers the conventions (return codes, `errno`, out-parameters), the **`goto cleanup`** pattern that keeps multi-resource functions correct, assertions, and how to design error-reporting APIs.

## 1. Conventions for reporting errors

| Convention | Example | Notes |
|---|---|---|
| return a status code (0 = success) | `int parse(const char *s, int *out)` | the result goes through an out-parameter |
| return a sentinel | `malloc` → `NULL`, `getchar` → `EOF`, `strchr` → `NULL` | the sentinel must be impossible as a valid result |
| return -1 and set `errno` | POSIX `open`, `read`, `write` | the caller reads `errno` for the reason |
| return a negative error code | Linux kernel: `return -ENOMEM;` | combines status and reason in one int |
| an error enum | `typedef enum { OK, ERR_IO, ERR_PARSE } Status;` | self-documenting, switchable |

```c
typedef enum { PARSE_OK, PARSE_EMPTY, PARSE_INVALID, PARSE_RANGE } ParseStatus;

ParseStatus parse_int(const char *s, int *out) {     // the result goes in *out only on success
    if (!s || !*s) return PARSE_EMPTY;
    char *end;
    errno = 0;
    long v = strtol(s, &end, 10);
    if (*end != '\0') return PARSE_INVALID;          // trailing garbage like "12abc"
    if (errno == ERANGE || v < INT_MIN || v > INT_MAX) return PARSE_RANGE;
    *out = (int)v;
    return PARSE_OK;
}
```

> [!KEY]
> Mark functions whose result must not be ignored: `__attribute__((warn_unused_result))` (gcc/clang) or C23's `[[nodiscard]]`. glibc already does this for `fread`, `write` and `realloc`.

## 2. `errno`, `perror` and `strerror`

```c
#include <errno.h>
#include <string.h>

FILE *f = fopen(path, "r");
if (!f) {
    fprintf(stderr, "cannot open %s: %s\n", path, strerror(errno));   // a message for the error code
    perror(path);                                                     // shorthand: "path: No such file or directory"
    if (errno == ENOENT) { /* create a default config */ }
}
```

Rules for `errno`:
- It's only meaningful **immediately after** a function **reports** failure. Successful calls may change it arbitrarily.
- To detect errors from functions without a distinct error return (`strtol`), set `errno = 0` before the call and check it afterwards.
- It's thread-local (each thread has its own).
- Common values: `ENOENT` (no such file), `EACCES` (permission denied), `ENOMEM`, `EINVAL` (invalid argument), `ERANGE` (out of range), `EINTR` (interrupted by a signal: retry), `EAGAIN` (try again: non-blocking I/O).

## 3. The `goto cleanup` pattern

Functions that acquire several resources must release **exactly** those acquired, on every path. Nested `if`s get unreadable, and repeating the cleanup at each `return` invites leaks. The idiomatic solution, used throughout the Linux kernel, is one exit point with a cleanup block:

```c
int copy_file(const char *src, const char *dst) {
    int status = -1;               // assume failure
    FILE *in = NULL, *out = NULL;
    char *buf = NULL;

    in = fopen(src, "rb");
    if (!in) goto cleanup;
    out = fopen(dst, "wb");
    if (!out) goto cleanup;
    buf = malloc(1 << 16);
    if (!buf) goto cleanup;

    size_t n;
    while ((n = fread(buf, 1, 1 << 16, in)) > 0)
        if (fwrite(buf, 1, n, out) != n) goto cleanup;
    if (ferror(in)) goto cleanup;
    status = 0;                    // success only if we got here

cleanup:                           // every path: release in reverse order of acquisition
    free(buf);                     // free(NULL) is fine
    if (out && fclose(out) != 0) status = -1;   // fclose can fail (deferred write errors)!
    if (in) fclose(in);
    return status;
}
```

> [!TIP]
> Initialise every resource to NULL or -1 at the top, so the cleanup block can test what was actually acquired. Check `fclose` on files you **wrote**: buffered data is flushed at close, and a full disk is reported there. Ignoring that error silently loses data.

## 4. Assertions: bugs vs. errors

```c
#include <assert.h>
void set_motor(int id, double rpm) {
    assert(id >= 0 && id < MOTOR_COUNT);   // a programming error if false: crash loudly in debug builds
    ...
}
_Static_assert(sizeof(Header) == 16, "wire format changed");   // checked at compile time
```

| Situation | Handle with |
|---|---|
| expected run-time failures (missing file, bad input, network down) | **error returns**, checked and handled |
| impossible states that indicate a **bug** (broken invariants, invalid internal arguments) | `assert`: fail fast in testing |
| facts known at compile time | `_Static_assert` |

`assert` vanishes with `-DNDEBUG`, so never use it to validate external input, and never put side effects in it.

## 5. Designing error APIs

- Be consistent within a module: if one function returns `0`/`-1`, they all should.
- Leave out-parameters untouched on failure, and document it.
- Provide an error-message function (`const char *lib_strerror(int code)`), like `sqlite3_errmsg` or `strerror`.
- Libraries should **never call `exit()`** on errors. Report them, and let the application decide.
- Robot and embedded code: on unrecoverable errors, enter a **safe state** (stop the actuators) rather than continuing with corrupted data.

## 6. Exam-ready answers

> [!EXAM]
> **Error handling in C.** C reports errors through return values rather than exceptions: functions return status codes, sentinel values such as NULL or EOF, or -1 with the global (thread-local) variable `errno` set to an error code described by `perror` or `strerror`. `errno` is meaningful only immediately after a failed call, and must be cleared before calling functions like `strtol` whose failure is signalled only through it. Every return value that can indicate failure must be checked. Functions acquiring multiple resources commonly use a single exit point with a `goto cleanup` label that releases the acquired resources in reverse order on every path. Assertions (`assert`, disabled by `NDEBUG`) check internal invariants that indicate programming errors, and `_Static_assert` checks compile-time conditions; neither replaces handling expected run-time errors.

## 7. Cheat sheet

| Need | Code |
|---|---|
| report with a reason | `perror("open")`, `strerror(errno)` |
| detect strtol errors | `errno = 0; v = strtol(s, &end, 10); if (errno \|\| *end) ...` |
| status + result | `int f(args, T *out)` returning 0 or an error code |
| multi-resource cleanup | `goto cleanup;` with NULL-initialised resources |
| check a written file | `if (fclose(f) != 0) ...` |
| internal invariant | `assert(cond)` |
| compile-time check | `_Static_assert(cond, "msg")` |
| must-use result | `__attribute__((warn_unused_result))` / `[[nodiscard]]` |

> [!INTERVIEW]
> **"Why is `goto` acceptable, even recommended, for cleanup in C?"** Without exceptions or destructors, a function holding several resources needs every early return to release exactly what's been acquired so far. Duplicating cleanup at each return is error-prone, and deep `if` nesting hurts readability. A forward `goto` to a single cleanup block at the end gives one exit path, with releases in reverse order. It's structured (only forward jumps to cleanup labels), and it's the documented style in the Linux kernel, the C equivalent of RAII and `finally`. The goto Dijkstra criticised was unstructured jumping backwards and into blocks.
