---
id: c-calc-switch
title: Command Calculator with switch
difficulty: Easy
order: 1
tags: switch, char, integer arithmetic
---
## Statement
Each input line is `a op b` with integers `a`, `b` and a single-character operator. Use a `switch` on `op`:

| op | result |
|---|---|
| `+` `-` `*` | as usual (use `long long`) |
| `/` | C integer division; print `error: div by zero` if b is 0 |
| `%` | C remainder; same zero check |
| `^` | `a` to the power `b` for `0 ≤ b ≤ 62` (repeated multiplication); `error: bad exponent` otherwise |
| `<` / `>` | the smaller / larger of the two (stacked cases sharing code is fine) |
| anything else | `error: unknown op X` |

## Starter
```c
#include <stdio.h>

int main(void) {
    long long a, b;
    char op;
    while (scanf("%lld %c %lld", &a, &op, &b) == 3) {

    }
    return 0;
}
```

## Tests
=== sample
7 / 2
-7 % 2
2 ^ 10
5 & 3
---
3
-1
1024
error: unknown op &
=== hidden
9 / 0
4 % 0
3 ^ -1
2 ^ 62
-5 < 3
-5 > 3
100000 * 100000
---
error: div by zero
error: div by zero
error: bad exponent
4611686018427387904
-5
3
10000000000

## Hints
- Read each line with `scanf("%lld %c %lld", &a, &op, &b)`; the space before `%c` skips whitespace.
- Each `case` needs a `break`, otherwise execution falls through to the next case. Stacking `case '/': case '%':` on purpose shares code.
- For `^`, multiply in a loop `b` times starting from 1, after checking `0 <= b <= 62`; the `default:` label catches unknown operators.

## Solution
```c
#include <stdio.h>

int main(void) {
    long long a, b;
    char op;
    while (scanf("%lld %c %lld", &a, &op, &b) == 3) {
        switch (op) {
        case '+': printf("%lld\n", a + b); break;
        case '-': printf("%lld\n", a - b); break;
        case '*': printf("%lld\n", a * b); break;
        case '/':
        case '%':
            if (b == 0) {
                printf("error: div by zero\n");
            } else {
                printf("%lld\n", op == '/' ? a / b : a % b);
            }
            break;
        case '^':
            if (b < 0 || b > 62) {
                printf("error: bad exponent\n");
            } else {
                long long r = 1;
                for (long long i = 0; i < b; i++) r *= a;
                printf("%lld\n", r);
            }
            break;
        case '<':
        case '>':
            printf("%lld\n", (op == '<') == (a < b) ? a : b);
            break;
        default:
            printf("error: unknown op %c\n", op);
        }
    }
    return 0;
}
```

`%c` in `"%lld %c %lld"` comes after a space in the format, so it skips whitespace and reads the operator. Stacked labels (`case '/': case '%':`) share code, which is intentional fall-through. The `<`/`>` line uses a small trick: when the operator matches the comparison result, choose `a`, otherwise `b`.
