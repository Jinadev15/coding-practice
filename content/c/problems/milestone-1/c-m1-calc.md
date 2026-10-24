---
id: c-m1-calc
title: Recursive-Descent Calculator
difficulty: Hard
order: 3
tags: recursion, parsing, pointers, error handling
---
## Statement
Evaluate integer arithmetic expressions, one per line, using **recursive descent**. The grammar, from lowest to highest precedence:

```
expr   := term   { ('+' | '-') term }
term   := unary  { ('*' | '/' | '%') unary }
unary  := '-' unary | power
power  := atom [ '^' unary ]          (right-associative: 2^3^2 = 2^9)
atom   := NUMBER | '(' expr ')' | 'abs' '(' expr ')' | 'max' '(' expr ',' expr ')'
```

Spaces may appear anywhere between tokens. Values are 64-bit signed integers (`long long`). `/` and `%` follow C semantics (truncation toward zero). `^` needs a non-negative exponent. Note that `-2^2` is `-(2^2) = -4`, because unary minus is above power in the grammar.

Print the value for each line, or one of these errors:
- `error: division by zero` (for `/` or `%` by 0)
- `error: negative exponent`
- `error: syntax at N`, where N is the 1-based column of the first character where parsing failed (the column one past the end of the line if the input ended too early).

There's no overflow in the tests.

## Starter
```c
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main(void) {
    char line[1024];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        /* TODO */
    }
    return 0;
}
```

## Tests
=== sample
1 + 2 * 3
(1 + 2) * 3
-2^2
2^3^2
7 / -2
7 % -2
max(3, abs(-10)) - 1
1 / (2 - 2)
2 ^ -1
3 + * 4
(1 + 2
---
7
9
-4
512
-3
1
9
error: division by zero
error: negative exponent
error: syntax at 5
error: syntax at 7
=== hidden
42
   -  - 5
10 - 4 - 3
100 / 10 / 5
2 * (3 + 4) * 5 % 7
abs(3 - 10) ^ 2
max(max(1, 2), max(-5, 0))
0 ^ 0
-(-(-(1)))
1 2
abs 3
max(1 2)
)
9223372036854775807
-9223372036854775807 - 1
5 % 0
((((((((((1))))))))))
2^62 + (2^62 - 1)
12 x
---
42
5
3
2
0
49
2
1
-1
error: syntax at 3
error: syntax at 5
error: syntax at 7
error: syntax at 1
9223372036854775807
-9223372036854775808
error: division by zero
1
9223372036854775807
error: syntax at 4

## Hints
- Keep a global (or passed-around) cursor `const char *p` plus the line start, so errors can report `p - start + 1`. Skip spaces at the start of every token-reading function.
- Each grammar rule becomes one function returning `long long`. Signal errors through a global error code, and once it's set, unwind by returning 0 everywhere.
- After `expr()` returns at the top level, check that the whole line was consumed. Otherwise it's a syntax error at the leftover character (`1 2` → column 3).
- Parse numbers digit by digit into an `unsigned long long`, so `9223372036854775807` doesn't overflow, and negate in `unary`. For `-9223372036854775807 - 1` the subtraction happens in `expr`.
- For power, square-and-multiply or a simple loop both work. Exponents are small, except that `0^huge` or `1^huge` could appear, so the square-and-multiply loop is safest.

## Solution
```c
#include <stdio.h>
#include <string.h>
#include <ctype.h>

enum { OK, ESYNTAX, EDIV, EEXP };
static const char *p, *start;
static int err;
static long errcol;

static void fail(int code) {
    if (!err) { err = code; errcol = (long)(p - start) + 1; }
}
static void skip(void) { while (*p == ' ' || *p == '\t') p++; }
static int accept(char c) {
    skip();
    if (*p == c) { p++; return 1; }
    return 0;
}
static int accept_word(const char *w) {
    skip();
    size_t n = strlen(w);
    if (strncmp(p, w, n) == 0) { p += n; return 1; }
    return 0;
}
static void expect(char c) { if (!accept(c)) fail(ESYNTAX); }

static long long expr(void);
static long long unary(void);

static long long ipow(long long b, long long e) {
    long long r = 1;
    while (e > 0) {
        if (e & 1) r *= b;
        e >>= 1;
        if (e) b *= b;
    }
    return r;
}

static long long atom(void) {
    if (err) return 0;
    skip();
    if (isdigit((unsigned char)*p)) {
        unsigned long long v = 0;
        while (isdigit((unsigned char)*p)) v = v * 10 + (unsigned long long)(*p++ - '0');
        return (long long)v;
    }
    if (accept('(')) {
        long long v = expr();
        expect(')');
        return v;
    }
    if (accept_word("abs")) {
        expect('(');
        long long v = expr();
        expect(')');
        return v < 0 ? -v : v;
    }
    if (accept_word("max")) {
        expect('(');
        long long a = expr();
        expect(',');
        long long b = expr();
        expect(')');
        return a > b ? a : b;
    }
    fail(ESYNTAX);
    return 0;
}

static long long power(void) {
    long long b = atom();
    if (err) return 0;
    if (accept('^')) {
        long long e = unary();                 /* right-associative */
        if (err) return 0;
        if (e < 0) { fail(EEXP); return 0; }
        return ipow(b, e);
    }
    return b;
}

static long long unary(void) {
    if (accept('-')) return -unary();
    return power();
}

static long long term(void) {
    long long v = unary();
    for (;;) {
        if (err) return 0;
        skip();
        char op = *p;
        if (op != '*' && op != '/' && op != '%') return v;
        const char *at = p++;
        long long r = unary();
        if (err) return 0;
        if (op == '*') v *= r;
        else if (r == 0) { p = at; fail(EDIV); return 0; }
        else v = op == '/' ? v / r : v % r;
    }
}

static long long expr(void) {
    long long v = term();
    for (;;) {
        if (err) return 0;
        if (accept('+')) v += term();
        else if (accept('-')) v -= term();
        else return v;
    }
}

int main(void) {
    char line[1024];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        start = p = line;
        err = OK;
        long long v = expr();
        skip();
        if (!err && *p) fail(ESYNTAX);         /* leftover input */
        if (err == ESYNTAX) printf("error: syntax at %ld\n", errcol);
        else if (err == EDIV) printf("error: division by zero\n");
        else if (err == EEXP) printf("error: negative exponent\n");
        else printf("%lld\n", v);
    }
    return 0;
}
```

**The pattern:** each grammar rule is a function, and precedence comes from the call structure. `expr` calls `term`, which calls `unary`, and so on, so tighter-binding operators are evaluated deeper in the recursion. Loops implement left-associative `{ op x }` repetitions, while `power` recursing into `unary` for its exponent makes `^` right-associative. Error handling uses a sticky global error code: the first failure records the column, and every function returns early once it's set. That's the C equivalent of an exception unwinding the parse. This is how real compilers' hand-written parsers (gcc and clang both use recursive descent) and robot command interpreters are structured.
