---
id: c-dynamic-rpn
title: Dynamically Typed RPN Calculator
difficulty: Hard
order: 1
tags: tagged unions, enums, switch, dynamic memory
---
## Statement
Build a stack calculator whose values carry **runtime types**, the way scripting-language interpreters do. Represent a value as a **tagged union**:

```c
typedef enum { T_INT, T_FLOAT, T_STR } Type;
typedef struct {
    Type type;
    union { long long i; double f; char *s; } as;
} Value;
```

Each input line is one program in Reverse Polish Notation. Tokens:
- an integer literal (`42`, `-7`) pushes an INT; a literal containing `.` (`2.5`, `-0.5`) pushes a FLOAT; `"text"` (no spaces inside) pushes a STR.
- `+ - * /` pop `b` then `a` and push `a op b`. Typing rules:
  - INT op INT → INT (`/` truncates toward zero; dividing by 0 is an error);
  - any FLOAT with INT/FLOAT → FLOAT (`/` by 0.0 is an error);
  - STR `+` STR → the concatenation; STR `*` INT → the string repeated (a count < 0 is an error); every other combination involving a STR is a **type error**.
- `dup`, `swap`, `drop`: the usual stack operations (`dup` of a STR must deep-copy it).
- `type`: replace the top with a STR naming its type (`"int"`, `"float"`, `"str"`).

After each line, print the stack bottom to top, separated by spaces: INTs plainly, FLOATs with `%g`, STRs in double quotes. Print `(empty)` for an empty stack. On any error (stack underflow, type error, division by zero, bad token), print `error: underflow`, `error: type`, `error: div0` or `error: token` instead, and discard that line's stack. **Free every string**: the tests run thousands of lines, and leaks are a bug.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum { T_INT, T_FLOAT, T_STR } Type;
typedef struct {
    Type type;
    union { long long i; double f; char *s; } as;
} Value;

int main(void) {
    char line[4096];
    while (fgets(line, sizeof line, stdin)) {
        /* TODO */
    }
    return 0;
}
```

## Tests
=== sample
1 2 +
7 2 /
7 2.0 /
"ab" "cd" +
"ha" 3 *
1 "x" +
5 dup *
1 2 swap -
3.5 type
+
1 0 /
"a" -1 *
1 2 3 drop
42 foo
---
3
3
3.5
"abcd"
"hahaha"
error: type
25
1
"float"
error: underflow
error: div0
error: type
1 2
error: token
=== hidden

-7 2 /
0.1 0.2 +
"x" 0 *
"one" dup "two" swap
1 2.5 * type swap drop
"s" 2 * 2 * dup +
2 "s" *
1.0 0.0 /
---
(empty)
-3
0.3
""
"one" "two" "one"
error: underflow
"ssssssss"
error: type
error: div0
=== hidden
3.21 -1.08
-3 "ab" dup 8.28
33 3.07 + drop -7.74 dup swap type swap / type +
45 -6.34 -9 drop 0.07 2 drop / 5.37 *
29
6.64 "x"
"ab" 0 swap type -
-40 -23 "ab" -6.90 -0.60
"ab" 23 6.77 / - swap
37 8.21 dup / dup *
3.99 12
"x" -23 - type drop "q" -46 type "robot" /
-3.34 43 / dup - type dup "x" type
"ab" -17 / drop 1.17 swap dup -1.23 drop "x" -0.90 drop
"q" "x" -45 type + - swap + 43 type
"x" "q" -7.86 - -43 35 -
"robot" 22 -1.90 "q" -30 -8.76 3.98 * /
-3.82 -46 + -1.84 drop swap "robot" 38 type dup "x" swap
"robot" -25 swap / / dup drop drop "x" drop swap
15 -4.24 29 / dup * "q" / *
-5.65 "q" dup - + -3 * 31 6.00 31 -
"robot" -4.76 drop "x" dup + / dup 2 swap "x" /
-7.36 13 swap * + 0.33 swap - *
-8 9 -7.85 -2.39 /
1.95 "x" drop * + 8.32 "x" dup +
-40 "robot" 34 - -1.01 drop -25 +
11 -5.45 - + dup "x" "ab" "x" 13
-4.24 1.60 drop + type + / type /
2.17 20 dup -33 drop /
-37 "q" - "robot" "q" *
"x" 1.04 -1.39 swap 2 4.10
-7.51 -6.92 + "q"
"q" "x" drop
"q" "q" 47 swap type 2.89 type 8.14 + 14 -
1.02 -23 + / -12 - swap -8.19 "x" dup *
"x" 42 3.41 -2.34 -41 -3.04 drop 0.77 + 37
"robot" 8.58 "q" "robot" 1.02 "ab" -8.06 "q" / + swap
-6.33 "robot" * -8.93
-19 -0.18 / 6.78 -8.15 43 10 + dup dup 4.05
-5.65 -7.63
4
9 24 dup dup * - "q" dup
"robot" 1.95 / swap drop 24 "x"
"x" "ab" + drop + swap
-44 5.17 type -8.42 - 8.02 + dup dup -8.69 42
5.44 -40 13 -0.59 50 30 + "x" -2.75 -8.44 +
-38 -6.17 dup swap * * * -
-6 -5.06 / 28
"q" "robot" type swap 49 - + drop -
4.40 "x" dup - dup "q" 2.13 drop dup
18 "x" -7 swap dup "ab"
"ab" 8.36 + / 0.94 -18 -6.49 5.54 * - dup
"ab" -3 -2.10 swap "q" dup
-21 -3.37 / / + + 3.53 -4.42 "q" * type
"ab" "x" type -2.07 swap "robot" -1 + -
"ab" "robot" 42
"robot" 4.35 type / type 49 -5 2.28 / / - 0.33
"q" "x"
"ab" "robot" 1.74 -25 -47 -48 19 drop 24
"q" "robot" + - type - / "ab" drop dup * type
-20 -17 -46 -2.69 8.09 dup * "robot" 6 /
-6.19 -37 48 dup "x" "ab" swap "x" dup dup
25 "ab" + 22 "x"
1 "robot" -20 17 dup 1.71 dup swap swap type -0.26
-26 -3.77 - * 49 / "x" -19 +
-8 -49
"x" "ab" swap "robot" + "q" + type + "ab" +
-26 "ab" type -8.79 * drop - +
-6.08 32 dup / -
"q" -27 dup dup swap - - 39
-8.84 "x" 14
"x" "robot" "ab" *
"robot" 24 "robot" -30 + - swap drop "q" -47 "q"
-2 "ab" type * dup type / dup
"q"
-6 3.13
24 23 "ab" -14 "robot" - -1.59 -5 5.22 drop * dup
"q" "x" 0.15 + "robot" "x" * +
-8 -41 type * 6 - 23 swap -21 18 -7.14
"q" -1.59
-8.17 7.06 dup + drop * + "robot" / "ab" +
37 "q" -10 * swap drop -13
21 "q" dup "q" + + - * 5 drop drop
49 12 0
-0.49 34 swap -5.54 "q" -5.20 swap dup -0.94 -2.01
8.98 -8.41
"robot" -45 swap swap "q" -6.09 36 type 42
-40 -6 type - * - "robot"
"ab" "q" 8 -12 4.01 drop / - / dup
"robot" 44
38 25 -0.41 *
"robot" -2.08 swap -8.29 / 8.74 dup 1.97 - swap drop dup
"robot" -6.43 15 "ab" 18 drop + type "q" dup +
"robot" "robot" "x" - + -9 + + drop
"q" -1 -12 6.68 6.70 "q" drop + drop -
6.17 "x" 2.87 "ab" 5.13 / -39 "robot"
5.57 4.03 swap type
"ab" -41
"x" "q" "robot" "ab" / swap swap dup +
"ab" -8.91 -19 type "ab" dup 45 drop drop -13 7 +
-26 "robot" / swap -6.97 type dup - / type drop drop
"ab" "x" dup -6 swap - * swap
-31 "x" "x"
"x" 32 - "q" + "ab" swap
-4.80 5.75 swap
-6.93 2.38 + / * 0 + - type "x" + /
"x" 0.51 "ab" swap
-8.68 "x" -2.04 "q" * "ab" 19 type * drop + /
38 -21 dup
"x" -31 1.43 26 / -4 / "ab" -26 -8.74
-0.69 -36 3.63 8 "ab" type /
"robot" "x" + swap - "ab" dup type
-13 "robot" drop + / -22 type
-28
"robot" -9
"ab" "q" / swap -8.38 + swap dup
3.18 6.50 drop "ab" swap
"robot" 13 "x" "x" + -7 dup / 31 "robot"
-7.47 3.31 "ab" * type / "q" + + + + 48
"q" "x"
29 "q" -30 / - + -24 -0.35 dup "ab" *
-31 -20 type -26 -14 + -
-1.76 2 drop / "q" "q" type drop 38
1.34 "x" * type "ab"
"ab" -5.54 -
"robot" 29 swap / dup
-4 "x" -3.56 "x" "robot" dup + 7 "ab"
-4.49 -39
"robot"
"ab" 7.48 dup "x" drop -2.51
"q" -0.66 "q" swap * swap type "ab" swap -8.49 -7.89 *
4.18
-48 "x" "x"
-33 "robot" + drop - type +
"ab" -0.96 "robot" swap dup / /
30 "q" "x" -4.89 dup + "robot" - type
"ab" -3.35 dup -36
-32 -37 - 4.04 -4.98
46 "q" -0.88 -5.76 "x" "robot" - "robot" drop 2.54
-36 -29 swap * 7.58 +
"robot"
1.20 -5.52 -42 -5.09 "robot" type dup
-3.94 -3.54
"ab" 28 "robot" -5
16 4.60
"q" -6.69 "ab" drop dup - * 16 drop dup
"x"
"robot" -7.96 -3 / 21 + dup * -3.91 31
3.08 -42 * -37 *
-23 7 "robot" / -5.45 drop drop swap "q" /
44 -6.69 + "x" - -
6.70 -4.42 / type -15
-34 -32
-6.83
"robot" "ab"
22 5.32 5 -4.17 -26 -2.83 dup drop /
"robot" 3.88 swap
3.16 -3.88 "robot" -48
"robot" "q" drop 33 type
25 -8.73 - dup dup / 42 swap
"ab" "ab" dup 8.82 "ab" / + -8.54
"q" 3.61 type -4.05 -
"q" 6.52 drop dup
3.54 -3.98 10 type /
-30 "q" + "robot"
1.95 -6.91 "robot" -18 type - swap
44 16 -1.06 - swap
-49 "ab" - 3.83 type -38 dup
"ab" "x" dup "x"
"q" 1.56 "q" "robot" "x" "robot" + +
-27 -5.78 swap -2 29 + -27 * - -
36 1.12 * / "q" / 31 *
-0.42 "x" -41 drop "x" / type 40
-1.02 -46 / 35 -4.57 -4.60 + 22 swap
"ab"
"q" 48 drop swap type -44 swap
"robot" "robot" + type "x" * 0.35
"ab"
"ab" 1.32 -50 -1.36 / swap
"robot" 9 drop drop 7.92 44 swap swap "ab" 6.34 +
"x" 8.20 -46 dup dup swap "x" 2 - / - drop
-31 5.49
6.55 "ab" type + -14 drop type +
-30 -15 "robot" "robot" 41 "x" *
"x" "x" type "robot" type -
-4 -7.81 dup 22 * drop / - dup "robot" dup
-5.20 -8.91 - / 4.88
6 "q" - 29 type / dup "x"
"robot" "q" * 50 8 *
"q" 40 * -11 4 drop +
0.67 6 swap type swap + type
-19 "robot" type - + - type drop drop drop type +
"robot" -31 dup "robot" + drop "q" -7 - -11 "q" "robot"
0.65 20 type -2.80 type -6 -2.45
-34 -44 -46 - -4.16
2.88 "ab" drop dup -29 41 type
"x" "ab" "x" type * swap drop
"ab" 21 "x" "x" / 4.40 type +
"robot" 7 "q" "robot" 1.87 "x" / -
5.45 39 swap "robot" 15 -6.33 "ab" + /
-5.58 45 / swap
-6.67 6.29 -24 swap swap type * * 25 7.03 -6.45
22 7 drop dup -7 swap + 3.11 drop 3.90 -7.70 -3.56
-25 0.54 "x" -3 "ab" -6.65 1.44 /
4 -50 8.05 "robot" swap / / -0.50
"q" -0.12 type swap + - -5.12 "x" -1.56 dup
14
3.27 "q" / swap dup "q" - * / - "ab"
-11 "robot" + 6.68 + -3.86 11
-1.34 "x" drop * / -10 * 2.34 drop
0.20 -37
"ab" "ab" + dup swap -1.93 dup / dup *
44 50 "ab" - - * -23 / - / 0.42 "robot"
"ab" -8.47 -5.07 swap - + 3.33 / drop "x" "robot"
-15 -23 dup 1.10 * + type 40 "x" - "ab"
33 "ab" type swap -0.10 drop drop
23 -8.26 + type * "robot" 42 swap
-43
-44 -8.41 + "robot" -3.46
3 "q" 12 5.11 swap - 50 swap drop +
"robot" "robot" 4.19 "q" drop
10 4.33 dup / type "x" 8.53 -
5.85 1.70
8.19 41 / type / - + 2
"q" -4.43 swap drop "ab" 1 type "x" drop + +
-33 41 "robot"
-8.39 33 24 "robot"
"x" -4.86 * 27 "q" "q" / * "q" drop
"x" "x" dup + / -34 dup 2.69 2.68 dup "robot" -3.53
"q"
-11 11 drop
-3.59 -6 6 -43 + / "q" type
35 8.08 dup 9 / dup
1.06 "q" +
15 "x" drop drop / dup - drop drop -28
"x" "x"
"ab" "q" drop / 8.67 -4.03 -39
8 -3.96 -26 + swap -6.53 / type * - 44 29
2.57 "ab" -6.53 swap swap "robot" * -39 swap
-5.29 "robot" "x" -36 * drop dup type
34 -22 "q" "ab"
"q" 4 1.74 drop "x"
-7.55 5.93 6.58 -6.74 -36 dup -34 / + swap
"x" -4 type
"q" "ab" 1.57
-4.67 "q" / type -13 drop swap -1.78 type -6.43 5.39
5.25 -49
-7.58 -0.51 swap
-31 7.80 "robot" / - type / type 6.67 - swap -18
"robot" 0.78 drop * swap -21 7.44 + "q" dup 48
-8.01 -0.01 * type "x" type +
-19 "q" / + type "ab" + -25
"ab" "q" -31 - "robot" type + * swap drop
"ab" 2 - 7.24 swap dup drop
"robot" -47 swap 2 + -44
-48 "x" -29 type 40 drop + "robot" * *
-3.76
0.32 -7 "x" + * -31 "robot"
"x" 1.17 swap -11
"x" -46 -33 * / + -5.80 / - drop 22
-48 "robot" "ab" * + + type
7.33 "robot" - * "x" 10 swap -1.52 type -3.33 +
2.15 2.32 type 4.08 type -
-5.43 "robot" swap -6.60 "ab" * type 3.81
36 3 -3.71
-7.31 "q" - "q" -4.52 4.13
"ab" "q" 14 * / 1.77 31 "robot"
-6.17 "x" * 31 / * + + swap -
"ab" "ab" swap -0.29 12 /
7.77 47 + - - 29 "robot" - + dup
24 -3.98 type drop + swap - *
-6.01 5.47 -11 "robot" 14
"q" 44 + "robot" dup - "q"
13 "robot" "q" -24 -43 + "x" dup
3 -25 drop * 50 dup -
"x" "x" - swap / + 33 drop type type +
14 8.14 * * dup type + "ab" dup drop 1.87
-7.07 "q" type + dup 0.60 40 * * + drop
-17 "q" +
-6.91 -2
7.20 "ab" -7.59 drop 3.74 drop "ab" * -4.22 - drop
19 3.86 -14 * -0.26 -13 4.96 / * swap drop -
5.53 1 + dup
"x" "x" * - swap 36 - -2.05
3 "ab" * 14 dup * dup - 49 *
"robot" "robot" - 8.87 dup 8.38 drop
-0.94 30 drop / -50 / "ab" - swap
2.28 -3.09
0.10 "q" drop swap / + / -50 drop swap -
"q" 3 -36
-11 -1.17 "q"
-1.21 "robot" - type -26 8.33 *
-4.03 -3.58 swap 6.73 drop / "robot" -2 18
23 8.12 / *
0.84 -4.24 + -8.90
"q" -5.27 + drop -8.47 * - type
-0.36 -37
-4 "ab" * "ab" / 7.95 -3 -7
"robot" "robot" swap "q" + drop * type * -0.79 type swap
-3.52 "robot" + dup "robot" -6.42 * 3.25 / / "q" *
-0.80 1.42 drop swap -4.14 + "q" + dup -
7 -1.59 type + "x" drop * -2.18 swap type "q" "x"
8.68 -6 -30 "x" 5 48 /
-1.50 7.55 * dup 44 -2.59 type "ab" /
-2.89 "q" dup type swap + -
25 6.87
"q" -3.98 type "q" -8.92 / -11 "ab"
-35 9 + * 33 - drop
"ab" -37 25 * type dup
31 0.39 swap 1.51 +
"ab" 3.51 type drop swap 22 / 8.12 44 15 "q" 8.78
2.34 -14 dup swap
-4.08 "q" 19 "q" "q" type
44
-2.94 19
"q"
-0.68 "robot" + dup -4 drop dup "robot" type type dup
48 "robot" "ab" 13 * dup -0.33 type 7.01 drop 48
"ab"
"robot" -2.79 swap -29 / drop 4 - "x" 40
49 -6.09 + 6 23 drop "q" -6.64 dup
"x"
"x"
-8.05 "robot" "x" 4.30
0.80 4.65 swap -43
"x" 0.93 swap swap drop * -6.20 + swap drop +
44 -12 drop - - 36 dup type type 7.39 + -44
"x" 0.09 - /
-8.52 22 8.63 drop dup "q" -2.68 -37 - swap 8.53 8.14
-3.31 "x" * + drop type 25 type
3.63
"robot" "ab" type -46 dup -6.21 * 35 swap 7
-2 -6.32
-1.62 50 -18 * 47 -8.24
"ab" -8.98 -17 -17 3.73 swap -8.05 -5.80 / type
"robot" 0.86 1.38 -8.87 dup
17 2.86 2.77 swap - / - -0.94
46 -0.85
-44 1.13 - + dup "q" + drop swap + type
0.39 2 26 /
-13 "robot" -5.73 swap drop + - -8.24 swap /
-5.55 "x" swap drop * +
32 -4.86
-2.56 "ab"
7.38 "q" + 7.73
15 -22
"robot" 8.67 30
2.00 -19 -0.37
-2.92
"ab" -8 -5.84 39 dup / "x" 4 *
1.26 "x" -
-3.93 0.52 "robot" 2.99 -9 -7.51 swap
-29 "robot" / * swap -8
"x" 1.22 / type /
-3.89 31 + swap / drop * "robot" / dup * 17
"ab"
"robot" 4.49 7.77 -47 type + * + "ab" dup dup *
"ab" "q" / 7.14
-38 25 - -8.82 -5.16 * "x" * / swap 3.94
"x" "robot" "x" -11 swap swap swap
3.37 3.25 type + -5.61 swap + /
-4.21 -36 drop type
28 "ab" dup -2.14 "robot"
3.80 "q"
"q" "robot" -1.50 -0.61 type / "ab" / -
-6.29 8.34 "ab"
"robot" "robot" 2.75 dup type type "robot" - type
-11 "q" drop 41
1.89 5.87 "ab" -13 + "q" + -44 / "x"
"ab" -6.62 dup type -22 "robot"
"q" "q" -0.99 30
3 "robot"
-36 "x" / drop
8 "robot"
3.19 "ab" 5.00 "q" swap type "robot" 45 type
8 0.50 swap - 21 7.54
5.41 "robot" * type 0.85
6.74 0.51 type / dup "q" +
0.44 "q" / drop
-0.46 27 +
-38 "ab" swap
"ab" 8.08
-1.61 -6.76
2.40 "q" 11 -4.12 * * -6.18 -3.03
"robot" "x" * dup "x" - "robot" swap drop * -
4.04 -4.70 + + "x" "x" "ab" /
14 -1.43 3.61 drop 5 type "robot" "q" 4 -4.01 drop
"q" "q" drop 34
49 "q" type / 17
-4.31 "ab" * 4.56 type 3.72
2.10 -7.16 dup - swap -4.93 dup dup
-4.97 8.10 * 48 8.47 4.89 dup
7.23 "ab" + dup "ab" -13 -0.72 -5.63 dup swap -
-36 -5.79 / + "q" 0.23 drop "q" 18 * / 1.80
"ab" "q" "x" type "q" - - -3.40 / + dup
-5.96 8.41 "x" swap "q" -14 swap dup -2.20 -21 +
-46 -43 / drop dup
21 39 -5.10 - -18 - "x" dup type + 11 +
3.77
"x" -17
7.89 -21 dup swap drop + -7.40 type "x" * type 19
-31 36 swap "robot" dup -5.26 -5.80 - type
"ab" "robot" type * drop drop - -4.55 drop "q"
22 "x" + -19 * - drop
-34 -35 dup dup -6.98 38 - "x" "ab" -1.03
10 "robot"
"x" "q" type "ab"
10 "ab" swap 8.20
"q" 1.33 dup dup type 30 -4.91 "q" 6.44 dup +
"q" 7.28 swap / 37 swap drop -13 dup / -4.20
"q" "robot" dup -6.90
0.43 5.54 "ab" * "robot" "x" 12 - + 8.67 "robot"
-9 9.00
"robot" "robot" swap +
"ab" "ab" 21 + type /
-12 7.32 swap type type 42 "q"
"q" -28 dup
-47 -2.61 swap 6.76 drop type - -22 type "robot" swap drop
-18 4.05 * /
-43 13 0.48 swap "q" drop - 4.08 drop 2.28 7.41 dup
"x" 43 "robot" 17 - "q" drop "ab" 2.10
"robot" "q" * swap swap
"ab" "ab" +
8.87 2 -2.33 + type * -8.13 / drop "q" dup
-2.33 "robot" 29 "x" "ab" type / 3.02 - drop swap
4 "robot" 6.16 "q" swap + -25 10 drop
2.48 -15 swap 24 "q" -3 3.23 21
5.01 "q" type swap "ab" * * type -
-28 "robot" type "ab" "ab" 31 -6.86 * "x" - / dup
-41 "robot" drop + swap 7.47 -11 drop drop "robot" -45 "robot"
-35 "robot" * / -22
"x" "x" dup drop * / "x"
-37 -1.25 33 "x" +
"robot" 8.67 8.07 "robot" swap drop
7.93 "robot" type *
8.71 -0.93 dup swap * swap / drop +
-8.90 "q"
-8.64 27 + -4.47 -1.85 +
-3.24 35 0
"robot" 4.35 drop swap 27 -4 + -5.02 "robot"
21 "q" "x" -5.58 / + drop +
"ab" 0.55 8.50 type / - drop "ab"
-5.94 7.35 drop -5.49 "q" swap -
"x" "q" swap 11 + / - drop / type -8.96 "ab"
"ab" 1.75
-0.90 "x" + - 44 drop 46 -6.10 / 6.20 -2.95
-50 4.04 / - / 6.94 type
24
4.03 1.33
8.87 -30 -6.77 drop dup 2 drop 3.64 type 8.50
-8.61 -5.18 "x" -37
"x" 50 * "ab" dup
"q" -3.48 type / dup
-22 "ab" swap +
-17 25 dup 7.32 type * / / / dup swap
"robot" 4 drop "ab" "ab" - "q" *
"q" "ab" swap + "ab" + dup "x" / 3.46 drop dup
"robot"
"robot" 20 * + - dup swap * drop + type *
"robot" -28 -5.38 - 2.70 * - *
1.64 "robot" type "x" / -6.36 + swap drop - *
-4.28 -1.55 * 33
-6.94 -7.61
2.57 "robot" "q" -2.38 * + "x" * +
-1.32 "ab" * "robot" -0.30 -6.57 "ab" drop *
"x" 4.38 24
0.13 5.16 type "robot" drop "robot" -2.13
4.41 43
-47 "ab" * drop * type type -4.93 type
2.61 "x" - swap drop
45 -0.86 "ab" * drop
13 -36 "robot" dup / / -29 -30 / - + /
-5.73 -10 type - / "q" type / 5.51 type -44
14
3.53 "x" 42 +
23 0 drop type -37 type dup 46 "ab" swap "robot"
"robot" 8 swap
"ab" "x" / 4.95 type 33 swap -18 - drop
"ab" "x" -19 27 swap drop swap
"q" 8.20 1.39 4.57 - - - -23
-49 21 * "ab" 8.47 3.06 * - * - dup 0.56
-2.04 -8.62 swap "q" 8.05
1.71 -8.57
8.01 -2.74 + - -42 + * type 1.42 -49
"q" 23
-23 -12
-6 -6.37 50 + - * -1.27 swap /
"robot" "q" swap 48 "robot"
10 6.68 "robot" dup drop /
"x" 6.91 swap "q" swap
"robot" "x" 23 / "x" + 30 "ab" / 6.67 31 -
"x" -3.14 "ab" 8.63 dup drop
-5.28 -2.94 -20
-2.15 -8.26 35 type type
-49 "q" "q" - -34 / + swap dup -
6 41 +
-46 3 -3 - "ab" -5 - swap 2.36 "ab" drop "q"
-18 0.60 drop dup
-7.40 5.57 31 + / "robot" "robot" -2.73
4.71 -1.05 dup * swap 4.03 / -34 -0.99 * + -0.65
-4 37
"q" 5.50 1 3.95 -1.80 swap drop swap "x" dup / drop
12 -7.18 - swap 4.09 - -49 swap "robot"
"x" "robot" 46 3.24 "ab"
"x" -7.85
"x" 5.31 dup -9
-2.90 -1.59 "q" * dup "x" 2.36
"q" 0.49 -5 /
7.55 "robot" drop +
-25 "ab" "x" 4.95 45 * dup swap -35 * type
"q" -28 "robot" * dup + -10
-1.74 -3 drop / 8.30
4.47 38 * +
11 -3.27 - -1.77 - -26 / swap
"q" "ab" - + - "robot" / "q" 33 41 dup
-3.16 "q" 8.33 "ab" "x" "x"
"robot" "x" / * 46 swap +
-18 "q" "x" + "robot"
"x" "ab" -
"q" "x"
23 "robot"
5.73 2.78 27
-1.31 "ab" drop "robot" "q"
38 "robot" -2.35 swap drop - + drop "ab" / type
6.05 "robot" 13 swap type + * swap
-8.72 6.11 "q" dup * drop type 5.40 drop
-28 -0.90 * swap -5.21
-48 -17 *
"ab" 2.17 -38 4.59 - / drop / swap drop drop /
"ab" "q" drop drop
"q" -28 type -3.17 "ab" / "q" - dup
-2.68 "robot" 5.75 dup drop type + "robot" swap
"ab" -0.66 / - -2.54 swap dup + 22 * drop swap
7.56 -2.00 swap
-10 -0.54 -0.06 -3.56 -5.15 + -
46 "x" dup "q" - + drop / "robot" - -0.02
-5.68 43 -
-28 "ab" - "ab" drop
-6.96 41 * "robot" "x" - type -6 *
4.10 49 *
"q" -5.68 * 1.78 * "ab" drop "ab" dup swap - 12
"q" -4 swap drop "robot"
"robot" -4.63
3.83 -8.51 4.32 - -
"robot" "robot" "ab" 27 47 swap 1.14 "robot" type 3
0.47 -0.65 drop dup 49 33 dup - type
1.27 -1.62
1.26
"q" "q"
15 -1
-29 36 * drop type 5.84 +
"q" -15 "robot" 36 / -25 -28 type - swap * /
0.62 "ab" 7.53 dup type -49 -6.43 25 type "ab" - drop
-15 -20 27 0.27 "robot" swap 5.51 "ab" *
31 -28 swap 0.43
-49 "ab" 37 swap swap 1.15 dup / -0.96 + -6
"x" -8
-14
-7.34 "q" -50 dup dup
"q" "x" - /
1.35 "x" type * 12 type type type + + drop -6.16
"ab" "q" + drop drop swap
-4.20 4.45
"x" -4.38 dup -0.06 swap -1.05 + type drop + type
-38 -18 0.36 - /
"robot" 2.50 * "ab" drop type
-6 -8.82 / + - -14 - dup 6.90 / -
5
-5.92 4.90 -6.74 swap / 4.22 0.19 -2.34
"q" -3.53 29
1.71 -4.24 + -37 - dup / "robot"
"x" 27 dup drop - -32 drop 3.54 type swap dup *
1
6.54 1.61 -5.19
-47 3.57 drop -45 type - 33 -21 dup drop * 7.63
-7.49 -45 -2.86 - -6.67 -38 * * / + +
"x" "x" type "robot" 29
"x" "ab" 7.78 type
"robot" -5.57 4.66 * -
"q" "robot" swap
"x" "x" dup + swap 3.63 dup
-3 "x" "ab" type drop drop type "ab" +
-33 "ab"
4.18 0.23 drop + 3.58 * * -23 49 / 2.45
50 -6.91 / -
-7.13
-1.22 "ab" type - "robot" 29 * -3.45
-2.25 5 -22 drop + + + -25 "q" -28 0.73
12 -31 -4.45 1.88
"robot" "robot" / / - * "robot" dup drop
21 "robot" "ab" - "q" "ab"
"x"
"ab" 32 / drop * drop + *
-43 -27 49 "x"
8 "ab" drop 49 / + -3.89 + 6.62 drop 8.67
"q" 4.77 swap swap
"ab" 12 drop -6.16 type
23 -2.21 swap 2.71 -
3.43 24 type 5.40 drop dup
-12 "x" dup -19 "x" "x" swap
"robot" 5
-16 28 drop 7.41 dup 5.56 "q"
-1.57 -40 41 type 3.51 8.99 dup - -
3.00 -10 4.47 drop + dup - "robot" / + type /
48 "ab" * type 1.98 swap * * -6.91 +
14 "robot" dup -19 dup swap
"q"
21 40 type dup 8.73
19
"q" 21 * "robot" + -4.03 / 4.20 -33
31 -4.98 drop drop -7.25 49 dup
"ab" 2.23 4 -9 -2.80 - / dup -46
1.31 -8.04 * * +
-2.25
33 5.73
"q" -43 "robot" - drop + -1.16 / -7.47 swap
2.57 47 - "ab" -2.91 - dup swap -2.63 -48
15 2.48 * swap
50 -4.74 - type dup dup swap
33 -3.56
6.97
-42 -6.64 -1 / "x" type "x" "ab" * drop
-1.84 -5.86 47 -35 * swap "x" type
"robot" "ab" - 4.61 drop - swap swap
"q" "ab" dup -18 / type - "x"
"robot" 3.52 dup "x" -5.54 -43 dup dup type dup type
-50 3.28 -5.26 27 dup + dup drop * drop
-22
-38 "x" 7 * -8.30 12 swap
"q" -6
-2.32 -38 swap drop
6.09 29 swap - drop -8.35 -25 - 8.63 type -
-25 -0.27 - - swap drop -8.98 type "q" "x" drop
"q" -21 / -4.87 drop
40 "ab" -3 / 7.78 type dup * / swap dup
"q" -7.48 drop - -25 * / - swap dup 4.11
-7.30 6.19 / / type swap "x" type swap
"ab" "ab" + drop 2.37 type 0.50 type drop -37
-7.20 24 dup dup 20 -7.88
-5.99 8.79 drop -19 + -6.19 "robot" + *
"q" -8.18 "robot" -48 type 8.43 -6.95 dup type swap
"robot"
-0.69 8.21 - +
"q" -4.84
"x" 11 -2.52 - "x" "q" 2.23 swap drop
"q" -6.36 17 -2.16
-3.66 "x" * swap -15 type dup 42 drop -
32 -0.17 drop -
6.07 "robot" -1 -33 7.52 -1 - -1.59 4.90 +
"robot" "ab" - "x"
24 "x" "ab" / drop * /
26 9 + "q" / * type + -
"robot" "robot" type swap drop / swap dup dup / dup
-38 -4.54 swap + "x" *
"robot" "x" * + dup -
40 29 "ab" 14 *
"x" 26 + 1.81 * 24 "robot" dup + swap -2
"x" "q" * - -1.84 4.41 + /
-14 -6.18
"x" "q" - drop * -21 dup drop drop 0.98 *
-46 "ab" "robot" -1.97 dup
"robot" "q"
15 7.33
4.45 0.02 dup -
-4.32 1.75 "q" drop -39 dup swap
35 "robot" 24 type
-19 44 type 1.01 "x" * "robot" / / 36 drop
"x" "ab" - drop 8.00 dup / * - /
"q" -3.44
-19 "ab"
9 "robot" type "ab" "robot" / * type "x"
"q" 2.37 - "ab"
"robot" 4
43 -2.64 + "robot" -24 dup "x" + +
-45 -35 23 drop
44 "robot" type + 4.07
"q" "robot"
-20 "ab" "q" 33 drop "robot" / swap 8.91
-50 -1.42 type 6.03 swap 6.53
-21 16
-8.93 -8.77 swap swap 44 -47 -0.87 drop
5 "ab" + 0.70 35 * swap dup - type 0.47
-27 "q" - -2.48 + - swap 10 1.81 * 8.40
-34 "x" 43
-0.36 -12 12 type - - -1.98 + +
-3.87 4.31 "robot" type +
-28 -8.57 - /
-27 -21 +
"robot" "x" -38
-2.19
-1.84 -35 drop "x"
"q" 5.14 -22 6.71
-8.32 -1.41 drop / + -19 + drop swap
8.67 -5.77 47 * / "ab"
-2.02 "q" / 48 4.62 -8 swap 3.46 / swap 2.23
8 "robot" swap drop 1.10 type dup -1.05 "q" -33 swap /
"q" 35 -18
5 21 swap 32 dup swap drop "robot" "robot" / 6.80 -
"x" -48 -
"ab" 11 "q"
"robot" "ab" 6.91 type drop -3.21
-38 -37 + * / "robot" / -46 - "x" type
"q" 46 -33
-1.39 32 "ab" - type 1.08 type "q" drop + swap "ab"
1.28 7.45 drop -2.79 "robot"
36 "robot" "robot" -8.80 / swap
9 -32 * dup -29 47 6.34 * - type
-7 "ab" 23 + type +
"ab" "robot"
24 "x" 44 swap
-8.30 "ab" "x" drop
5 -11
1.29 "x" swap *
-4.51 -3.91
"q" 2.06 43 * 2.07 -3 7.30 * -4 / * *
8 "robot" -35 / -10
"robot" "x" "q" swap / dup * * dup * + +
"robot" "ab" "robot" * dup drop * * 3.21 * "robot" /
"x" 26 type type -29 -11 -2.77 - 2.81 dup 4.14 -
-8.69 "q" swap "ab" "ab" drop type "q"
"x" -8 45 drop -42 swap swap "ab" dup swap *
40 "x"
"ab" "robot" dup 4.81
2 -5 type -0.65 * - -3.71 "x" drop
"q" -8.19 "robot" / + -8.20 type + -6 "ab"
8.01 "ab"
5.83 -8.29 drop dup 4.11 8.84 -8.03
2 20 swap
-34 8 type dup + - + +
7.00 "robot" "q" + dup
"ab" 3 -44 type dup -7.75 drop
-37 "q" 5.65
7 -13 +
-30 "x" dup - swap -14 24
-33 "q"
-6.68 "robot" -4 / -4.96 dup drop / /
3.69 -2.74 + "robot" - -11 * 7.88 "x" -
-50 "x"
-22 "robot" - 1.25 / "ab" 38 / type + * -8.44
"robot" 0.71 -6.96 dup
50 "x" - -3.73
"x" "x" "robot"
"robot" -10 + "q" type
"q" 2.91 type swap "robot" "ab" -6 type type 5.04 drop swap
30 -6.69 -2.87 - * -2 + drop 10 "q" -
"q" 50 * 11 swap dup drop
"x" "robot" + "x"
-33 -22 swap -3.93 "robot" -2.67 33 drop type "robot" dup -8.11
26 -22 -17 "q" dup dup drop "ab"
"x" "x" swap swap -1.61 type - -1.72 / 37 / /
"x" 8.99 "ab" "robot" - "x"
-29 "ab" + drop
"x" 31 + drop / 9 8.82 5.42 "q" swap * +
37 "q" * drop swap / 41 drop *
6 6 "robot" 46 "q" swap + swap "q" / 4
0.17 -4.38 - drop
"x" 5.69 / -13
31 "robot" + 5.81 + "q" "q"
"q" "robot" * / -1.37 + "ab" 0.86
"robot" -1.17 type swap + 6.56 / -8.35 "q"
48 "q" dup 28 "q" + 22 4.26
-1.80 -20
5.47 4.49 + dup 11 "x" 6.85 "robot" 25 -34
3
5.13 "ab" / 0.62 -1.27 swap "x"
"ab" -1.18 -16 drop dup drop type "x" 39
40 23 dup 42 - -6.27 / -9 -8 2 *
-6.54 -6.88 -
7.58 2 dup drop
"robot" "q" / "robot" / + - -29 dup
50 15 / / swap
"q" -9 -10 dup -
-48 "ab" "q" 29 dup swap
2 -48 drop - type +
"q" -11 drop + / type
"ab" -28
-2.79 "q" 8.49 type drop
"ab" 31 - -4.56 6.13 drop swap - + / -49 /
43 8 drop 0.44 -40 "x" type drop 29 -
6.49
5.55 -41 27 drop -4.52 / + dup swap
"robot" "q" -39 swap type drop dup "ab"
6.49 -2.17 + - - 6 swap drop drop
-1.69 0.65 15 /
39 26 type
1.97 3.94 25 - -4.14
-0.77 "q"
"x" "ab"
"q" 1.25 8 -34 drop / - 4.62 "x"
6 -5.30 2.44 - type / dup / + - "x"
-24 "x" * 1
-11 -8.94 + dup / -7.37 drop
"robot" 43 - "q" -25 4.10 - -29 /
1.00 -12 * type dup -6.94 5.27 6.78 "robot" type
25 40
-37 -35 * type "ab" "q" drop + / * -1
-1.40 "robot" 8.74 "q"
"ab" "q"
-19 39 * swap + / -34 +
"robot" -2 / drop * type "robot" 12
-41
"ab" 1.86
"q" 3.46 + -45 * * dup type swap
2.42 -5.82 +
-29 "ab" type - dup + -7.77 "q"
-26 "x" dup swap type -2.87 drop / swap type 4.30 "robot"
"ab" 48 + dup / * swap 2.96 - "x" - 1.45
27 24 type 14 / "robot" 3.82 type + 7.36 4 *
-49 "q" drop swap swap -2.21 type 4.23 * dup 3.26 /
-20 -8 "x" - - -
-8.27 8.02 + swap "robot"
"q" "x" / -5.16
"robot" 0.57 swap swap 14 -23 type * type "q" swap swap
2.13 "robot" swap 5.31 type "robot" -47 type 6.64 2.28 /
"robot" 12 "q" type + - * swap -0.96 type -3.22 swap
2.07 "x" -2.07 "robot" -
"x" 1.53 swap - + / dup type - -5.56 drop
"ab" -4.34 +
"x" 2.16 swap type - "q" / "q" * drop 40 "robot"
"x" "x" 3.97
-34 "x" swap 25 * "q" dup dup drop
-2 1.13 "q"
2 -7 -7 * dup * drop -8.08 type
5.44 18 type
"q" 2.51 - * / dup / -7.05 "x" type
"x" 0.25 * "ab" / -33 swap type - 38 8.43 /
3 23 / "ab" -7.79 -8.11 drop 1.99 type +
1.58 -17 "q" swap drop 4.04 dup +
0.49 -0.38 8.61 drop "q" / swap -1
1.98 "q" dup +
"ab" "ab" type "ab"
-0.83 12
"x" "robot" + type - "robot" -8.26 24
2.16 -32 -3 * 8.66 -
-37 "ab" "ab" "q" 41 * + - drop
-38 26 19 type -35 -6 1.31 + type
"q" 8.68 41 "ab" drop "q" * -1.83 / 10 dup drop
47 7.11 "x" /
"robot" 4.26 16 drop - -44
-6.17 "ab" dup -6.41 swap
"q" -1.22 / 36 /
0
-2.09 -42 / / -7 drop
45 "x" -31 + / 1.23 / /
"x" -31 - / 47 -11 7 swap swap type
-24 -2.69 drop 2.87 + * drop
-26 8.97
"robot" 11 dup -41
1.32 -8.72 "ab" -6.75
-7.62 7.06 drop / + 7
"q"
33 "robot" * drop + 37 /
1.78 -11
7 "x" 23
6 "q" "q"
-5.37 "ab" swap "q" + - + -0.16 / 7.42
-23 "x" - 18 swap 31 -1.76 + type "robot"
-3 -11 drop swap /
42 -4.42
23 7.44 swap -6 "x" drop + +
-0.60 "q" dup * -8.98 drop
-7.41 7.42 * "x" 6.61 * "x" swap "ab" dup
-32 "robot" 4.99 "ab" -7 -8.52 type 2.19
"robot" "x" 6.53 + 5.37 *
49 -4.74 *
8.81 3.43 "q" drop drop "robot" "robot" * dup 0.85 +
46 -5 - - *
"ab" -5 "ab" 8.09 + * swap -3.29 -20 - /
"q"
"robot" 3 swap "q" 0
17 1.85 drop
"robot"
"ab" -37 -24 type type * + / * - drop 1.58
"ab" "x" type + + -24 "robot"
"x" "robot" -6.96 / "q" *
"robot" "robot" 45 drop "ab" dup "robot" drop "q" "robot"
9 30 swap / drop "robot" /
"q" "robot" * type dup 49 type type * drop "x" 28
21 "q" + swap + -6.88 * - -31 -
"ab" "x" swap * 1 "q" -2.95 "x"
9 1.86 swap dup dup * -0.00 * type
39 "q" swap + -3.34 48 drop + -48 -7.58
-8.43 "robot" 24 dup * "ab" dup "robot"
1.79 "x" "q" - "q" dup type + type * 6.42
-39 -4.96 drop swap * drop "ab" - -4.56 drop
"q" -4.21 "ab" drop dup "ab" type "q" -
8.23 "ab"
-0.84 -38 -9 * 31 drop
23 "robot" 50
"q" "robot"
"q" "ab" 3.62 * + - 0.66 7.30 type "ab"
"q" -7.50 dup -50 type swap
"ab" 41
45 21 + type -7.70 type
"x" 13
5.64 "robot" swap drop drop 0.96 type -10 "q" dup
5.96 -5 5.07 drop - 20 * * type 46 *
-31 -2.80 / 1.91 -35 drop -5 * -5.96 8.76
"q" -0.98 "q"
-40 "q" drop "ab" -42 swap -27 dup
-19 "robot" -
-29 13 swap -0.74 / - +
"x" -3.09 "robot" dup 25 swap swap / "ab" drop
-28 "q" drop -
"x" 5.31 type -40 swap "q"
-44 2.85 - 5.23 "robot" * -1 drop * "robot"
21 3.77 24 / 7.87 - 7.93 +
"ab" -34 swap "q" - "ab" 2
-2.72 33 +
-9 45 dup + dup -38 drop drop
"q" 1.75
5.36 -0.88 type dup drop "robot" "q" -
"robot" -9 -2.37 - -6.07 + "ab" 19 38 +
29 "q" * swap * "ab" 35 swap * 29 "ab" -44
"q" "ab" -1 /
3.51 "q" -
-10 "x" drop + + *
-42 -17 type 31 swap + - drop 28 - -8.07 -
0.19 "robot" "robot" - / 4.25 - "x" -8.20 drop
-3.10 -48 / drop drop -8.23 "x" /
-48 -32
-42 22 dup 0.96 5.50
-50
-11 "q" swap swap +
19 1.11 + drop 6 /
"x"
"ab"
1.26 "x"
6.99 0.92
22 -2.56 -18 / 9 / dup
9 -3.59 -0.88 + "q" / drop drop "x" type drop
"x" 22 + / dup -9 - + 7.26 7
-49 "ab" dup swap type swap drop swap type drop -1.01
-7.80 7.26 43 drop / "x" - 7 + - -21
"ab" 4.96
15 11 7 drop -15
-5.46 8.96 6.37 -37 "ab" / "robot" "x"
"x" 46 "robot" "robot" drop - 37 / drop
"robot" "q" / drop / -
"robot" 32 + drop type drop
-0.44 4.61 - dup -2
-13 -8.09
23 33 dup / 46
19 5 drop -1
37 "x" - -39 - drop -11 dup swap
-2 "q" * + "q" - "q" type +
3 "x" 2.47 type + -19 + + *
39 "robot" *
7.26 0.69 + 13 type type type - dup -6
5.09 "robot"
2.29 24
3 -1.80 drop -8.84
23 "robot" *
"q" "ab" 6.15
"q" 1.48 / -7.54 / 7 * 48 drop dup
"x" "robot" 2 drop swap + * dup - dup 2.50 39
"x" -24 * drop 50 - -6 "ab" / 5.63 0.60 7.26
38 -32 drop type drop swap 3.25 -1 5.09 * -47 *
"ab" -3.38 -5.96 drop swap / 4 -6.50
3.79 "ab" 3.89 31 -26 0.84
"x" "q" 8.72
3.01
39 "ab"
"x" "robot" 50 + * type /
7.90 "q" "q" - 1 swap -5.35 - dup 2.93 11
-22 8.99 -0.30 -41 23 swap +
22 -25 drop swap
"q" -25 swap /
"ab" "robot" -4.86 type
7.50 "robot" / + * - dup
-5.30 -1.85 -0.04 * + drop
"ab"
12 7.33 dup - / - "x" + -
-49 8.38
17 -17 *
-0.71
46 -8.45 * swap * drop dup
"x" "q" * "x" -6.64 + 35 /
"x"
-4.11 5 "robot" type drop "ab" / dup -44 -10
50 -0.27 "robot" - -4 - dup + 13 + swap +
"ab" "ab" "q" "robot" + "q" swap / "robot" drop
-48 "ab" 8.20 / / - drop + *
"x" -27 swap swap / * * - - 1.65
2 "robot"
"q" 34 * 3.28 - -5.54 * + dup drop - type
"q" 6.59 -19 "ab" drop * *
33 "ab" + 36 drop /
-10 7.06 / 8.27 6.18 -6.53 2.93 -29 -
-1.80 "ab" / drop 1.72
0.18 "q" / * 40 3.93 "ab" "robot" swap -8.03 dup
25 "x" "x"
-2 6.77 swap
-18 -5.82 "x" -28 33 -16 33 "q" drop
7.93 "ab" / 3.46 - -38 -40 -45 * "ab" - -37
"ab" -34 drop dup dup
-8.07 7.92 47 * 6.88 / "q" "ab"
"ab" "q" + -2.14 type -1 6.68 *
"robot" -18 / - dup
29 "robot" - 5 19 drop "robot" -0.99 "x" dup / 6.88
15 "q" 6.68 25 - "x" -0.28 +
"ab" -1.77 / type -8.07 * * * -1.30 -42
-6.26 8.31 - 1.85 swap drop -0.30 drop type dup -
-7.28 -1.63 type drop dup -35 * swap 5.62 / "robot" 1.23
-9 -5.44 type swap drop -32 "ab"
49 -13 * dup 11 type "x" *
"robot" -4.70 type dup / * -15
-2.05
43 4.79
"robot" "robot" +
-3.14 7.12
8.29 "x"
"robot" 1 type 0.57
-1.51 17 dup -7.67 swap / 7.24 / "x" "x" -
-10 "x" -0.49 * 2 type swap -36 5.38 - type -1.82
-3.14 -8.43 -39
-1.53 0.99 drop 1.89 -7.18 - "x" dup type -
"x" 32 * swap -13 drop type
-19 -0.73 type / "q" /
3.45 "q" 7.19 dup "x"
"x" -2.95 "x" * -8.36 "robot"
-49 3.42 "q" -2.06
5.31 0.74 swap 37 -8.51 34
"robot" -1.90 swap "ab" + "ab" + drop
"robot" 4.17 "ab" swap * / dup
"ab" "robot" swap + * swap
-8.59 -13 18 "robot" -0.93 "x" drop * drop dup +
-2.83 4.67 * 8.91 dup / drop "robot" type *
"ab" 6.61 drop drop 1.33 -
"q" "robot" swap "x" 3.56 -0.29 47
46 -13 5.97 - 45 /
8.46
20 "ab" * "q" -
2.73 1.71 swap -6.83 1.42 * / -3.09 6.39 44 * 2.42
-25 -3.69 -7.07 "robot" type -4.88 0.47 / 29 "robot" "robot" -4.19
"x" -2 1.92 - -2.38 drop "x"
-2.55 20 - + swap 43
"robot" -8.75 drop
10 "x" "q" * "robot" / - type "robot" "q"
6.96 -2 dup "robot" / drop 4.76 -17 -3.18 -
2.40 -36 "robot"
"x" 4.59 + * drop -28 -7
"robot" 15 - *
-3.99 "q" drop drop - / -8.11 "q" dup 8.73
"x" 5 -17 -5.59 "x" dup - swap - 6.15 -6.39 4.68
"q" -47 - 18 swap -5.73 / + -14 "q"
6.58 -45 swap - - 5 "q" -15
4 3 / * type "ab" -15
21 "robot" - -7.10 -7.39
6.08 -1.62 swap "robot" dup "q"
0.57 -4.86 "robot"
"q" "q"
5.51 36 swap dup -
-0.85 34 3.16 "x"
-39 -6.40 +
-45 "q" + - * -19 type
-2.18
-10 -5.67 "x"
-36 5.18 type 5.28 / 32 type
49 -8.04 -49 - - -16 39 -0.10 / 5.15 + swap
-7.82
"robot" "x" 5.29 - 5.73 "robot" * * drop
"ab" 41 - 44 / "x" "q" "x" "q" /
"ab" 7.64
-2.16 "q" 3.08 drop -5.26 -1.72 swap drop /
-5.06
0.90 "q" dup dup swap
"robot" 2.76 drop
-2.17 "ab" - drop 5.91 - type "x" swap 7.53 drop
-48 -0.06 "ab" / -
46 -7.10 dup * -11 - swap dup dup type
"x" "x" "robot"
2.75 15 dup
-7 -6.70 * dup swap "x" type /
"robot" -29 + "x" 2.84 drop "ab" -0.83
4.46 "x" + "q" -20 - + +
32 43 type "x" / - swap 25 -6.82 drop
"q" 17 2.68 swap type type "q" 8.46
-7.95 6 drop swap 50 drop
-4.35 49 "robot" 2.78 type + * swap drop
15 -4.25 "robot" / * drop - "ab" "q" + swap drop
6.58 2.76 drop swap type "q" 44 type /
-6.97
"ab" 8 -42 "x" 42 "x" - dup "ab" swap 18
-50 12 -0.89 * swap -2.60 4.01 - "q"
"robot" "ab" * type / swap * "x"
-12 -4.15 dup *
40 -5
"robot" "q" -21
"q" -29 "q" - - 6.62 swap dup swap
-29 28 type drop -36
"ab" "ab" type swap * 8 - -1.52 / - + 6.72
"x" "x" + / 5.76
"robot" -28 + type - 36 "robot" -7.34 -2.81 +
-2.66 "x" 42 drop /
2.07 -8.72 / * / swap 2 drop +
"q" 50 dup "robot" /
"x"
"q" -3.17 drop "x" -7.84 "q"
3.06 -1.87 * / * * / type "robot" 15
-5.12 -4.88 * -28 4.09 + 47 swap * 21 "ab" 43
8.33 "q" "ab" + + / swap *
-0.03 -3 - dup drop swap 23
-6.94 -1.09 28 * type dup "x" 39 drop type 23 +
"ab" 8.79 swap type
"x" 50 / 0.50
5.31 -2.48 +
7.38 6.20 "q" 21 -46 11 / -36 swap dup
-10 4.13 * - type 1 -4.94
-4.30 "q" type -20 -4.23 / 0.26 0
2.26 -40 3.69 - + dup *
2.00 7.56 *
10 0.32 * /
38
"robot" -2.53 - - dup dup -13 dup
12 -3.78 dup -10 * "ab" 5.80 -31
-48 "q" / "q" - type * "ab"
-7.02 40 * 4.33 +
-33 "x" - 8.88 * 34 "x"
"x" "x" 5.44 "ab" "x" -5.42
0.47 -1 swap - "x" / swap
-26 "x" - -3.47 "robot" -4.02 drop -1.30 -50 type drop +
-2.42 "q" / / *
"q" -7.57 -7.64 dup 1.29 type
"q" 21 - 6 -9 * * -43 * drop
"robot" 1.08 -5.75 + swap type
15 31 drop "ab" *
"x" "q" drop
39 "x" 7.69 drop
47 "x" 0 -5.15
"x" 1.38 22 -3.79 *
-11 "ab" 46 "robot" type + "ab" 12 type 0.05 drop
-0.86 -1.45 - + "q" swap + + "q" "ab" drop
"ab" 8.79 type /
"q" "x" 5.66 -16 "ab"
"ab" 0.14 28 * / drop - +
"q" -1.01 + 14 drop drop -
"robot" -5.48 - "q" / - dup -7
-16 5.83 -20 + * -3.50 "ab" 1.69
"robot" 0.70 -3.10 "ab" swap
-8.07 "x" * swap drop -12 3.65 -7.75 / dup
"q" "q" * "ab" 39 drop
-11
5.33 4 type 25 "ab" / type -3.58 + -9 *
-2 -6
44 3.88 + 7.30 "ab" / 11 - 11 "x" + -6.93
0.15 50 "ab" -2.12
36 2.88 dup 8 dup
-22 5 swap drop "robot" swap
22 "ab" / drop "q" type - *
8.26 -4.13 / "x"
4 "robot"
4.08 "robot" 3.65 drop "ab" 0.19 * drop drop - dup +
1.47 "x" / drop 7
33 6.13 + dup 36 * -6.31 dup type "ab"
-18 "x" 43 "q" drop swap 42 -46 type -
28 "x" - drop * -11 0.51 * type / "x"
-3.52 -5.47 + - dup "q"
"q" "q"
-26 44 -0.70 -25 dup + drop -8.83
"x" -14 * 10 - "x" - - * / 5.12
"ab" "x" drop -3.74 / -5.52 -2.82 swap "ab" -4.02 "robot"
"ab" 1.11 25 7.18 * -2.35 "x" drop * drop 2.66 -11
3 -34 drop "x" "x" / swap 14 8 "ab" +
6.86 "x" -38 23 28 type * 6.58
"q" -15 drop / + *
"robot" "robot" swap 48 dup +
"robot" "robot" drop * 21 -50
"robot" -0.54 "ab" dup -10 13 "x" "robot" *
"ab" -8.44 drop 36 -46 dup dup -0.34 type type
"robot" -6.48 / type type + -4 2 3
-0.08 23 "ab"
-2.24 23 / -13 + "ab" - type swap /
6.98 "q" swap "ab" + drop
3.23 3.28 + * 0.22 - type -
-1.44 44 type type "x" drop -5.54 / + dup "q" *
-7.17 2.45 swap / dup 7.13 + dup "robot"
"q" "x" + +
21 "ab" type / 38 + type / type -8.19
-35 "ab"
"q" "x" swap swap
-17 37 / -5.51 "q" / -8
"robot" "ab" - 9 "ab" -48 + 36 swap - swap
"robot" 13 / -48 / dup + type 2.12 / / -4
-8.39 -7.31 drop
9 "ab" 7.12 swap + dup - swap - / - "ab"
"robot" "x" "q" / -
"robot" "x" - drop + / - 6.35
8 -0.16 2.10
-15 "robot" -48 drop swap
-24 1 26 type 34
"ab" -5.31 "x" / /
22 -6.24 + -13 type "x" type - -3 -2.58 drop
39 -0.02 -4.04 *
-44
1.35 "ab" "x"
-2.06 -8.72 "q" -6.96 * type 8.64 -31 *
-6.03 12 "robot" / -
8.56 "robot" "ab" "robot" "q" "x" "robot" -25
"robot" 46 / / *
-12 25
-5.78 -0.49 -41 /
24 19 - dup / "robot" dup -44 swap
7.46 5.90 swap + 18 dup swap 38 dup + +
-6.88 42 "x" 32 "ab" "q" "robot" "q" * swap type
-0.48 "ab" drop dup dup * drop - drop 5.12
13 -5.56
"robot" -1.77 drop
-43 6.10 - / + "x" type swap / "q"
"x" -38 drop + -7.54 7.91 - type dup -19 * type
47 7.54 3.97 "q" dup * dup swap - drop
"robot" "robot"
5.42 -1.51 -3.69 - -3.64 swap swap dup +
4.74 -4.88 type -22 "x" drop "ab" -2.77
-0.46 4.76 42 "ab"
-6.30 4.61 -35 * swap
-4.88 -7.49 drop "q" drop 6.65 type - type type -5.39
"x" "x" 7 -17 drop -19 type dup + + type 19
4.27 -3.35 type drop
7.69 6.11 -34 * - /
"q" 1.20 - -7.57 + drop 34 dup dup + swap "q"
"x" "ab" dup dup -11 -24 /
-3 "x" * *
"x" "ab"
"robot" 1.45 swap "robot" -27 7.81 - drop type type
6.71 "q" -0.43 -2.67 * *
-13 "ab" type drop type
-8.80 "robot" -47
-6 29 dup drop drop
"ab"
8.84 6.78 -29 swap "x" 40 +
7.72
"x" -20 dup type 8 * "x" "ab" drop 3.32 / 0.31
"robot"
-13 21 5.45 2.14 * swap
"q" -23 -17 -8.05 - dup
2.81 32 - type / 12 dup
"robot" "x" "ab" 20 0.47 4.62 "x" -
"robot" 0.60 * -3.28 - 0.76
"x" -4.93 -7
-8.30 "q" type - - dup swap
1.79 4 -3.28 swap dup -
8.24 -0.16
1 "q"
4.08 -1 "q" - 47 swap type "q" "ab" -50 drop
1.33 "x" "ab"
35 "x" + swap -2.61 type *
-40 -22 -37 1.46 drop + -
"robot" -2.03 + swap swap "ab" drop 1.21 "x" * 8.34
2 -31 4.45 swap
"robot" "ab" 3.08 * / -46 drop type * * + -4.00
"q" -4 "robot" 17 + -7.76 4.33 / dup drop 21 *
-1.64 "ab" -3.60 swap -
7.23 "q"
"q" 20 swap type 2.48 / dup
27 7 swap swap swap
-25 "x" + drop + drop - drop dup type 7.01
49 4.07 * dup /
"ab" 5.19 13 * 4.21 -13 - "ab" -19 swap "robot" -
"robot" -4.80 drop / "q" "robot" -31
-8.71 -2.29 type -5.11 drop / dup drop
-8.21 -0.02 type - type "robot" + -5.79 "q" dup /
44 9 2 * 5.92 -8.66 dup 3 type
5
-6.20 40 "ab" -40 -17 dup drop / - swap type /
7.65 "q" -21 -2.55 -41 dup *
-1.18 -25
-29 7.83 - "ab" swap
"x" 5.75 - *
5.68 16 * swap / "q" 48 swap - swap
-6 -18 / * -6.80 -49 swap type /
"q"
12 50 8.57 "x" swap swap -0.18 42
"ab" "x" * -8.37 - 1.28 swap
-10 "ab" swap drop -
-36 "robot" + 9 "x" * dup "q" type drop type
2.24 "robot" / + 48 dup swap "ab" 1.39 -2.38 - +
-2.95 -4.28 "x" -17 0.97 drop -
0.14 "x" + 4.26 + - "x" -3
"robot"
26 -47 "q" -0.45 type + * + "ab" -44
"robot" 2.03 -26 * 1.36 -6.97 -13 drop swap
"x" "q" 48 drop type -6.23
-7.87 "ab" "x" + swap / -35 *
4
-41 -34 - dup 5.99 dup "x" + + -6.31 type
2.31
"q" 5.92 7.05 - -
30 -6.88
45 7.26 5.18 swap "ab" - -4.42
"x" 26 6.89
"ab" 2.72 / type -24 "q" 12 type drop 7.84 type
"x" "ab" dup "q"
-19 33 *
"x" 3.03 / -7.74 drop + swap + -17 type
2.59 -17 type + -3.05 "robot" /
37 -2.09 dup swap /
0.62 "x"
6.43
47 -5.38 drop -2 / type swap
"x" 6.12 type dup - 5.91 / -11 dup dup + drop
-5.59 9 6.12 "robot" 32 dup * 43
"robot" -5.36 / type dup - dup "x" + "x" * /
21 "ab" swap 8.16 -1.17 dup swap "q" drop drop -
-8.97 -8.66
"x" "ab" -2.36 "q" -3 + 21 + - "q"
"robot" -8.29 dup drop
-31 -38 + drop 2.32 + 7.73 dup 8.49
-5.52 "robot" + * * -4.90 dup drop
"ab"
-22 7.88 - * "q" "robot" "x" dup drop -7.16
-9.00 -2.22 / dup + +
46 -42 swap drop "q" + / -8.89 6.64 type "q" "q"
"x" 4.74 - dup type + dup 9 drop / -11
-22 -1.01 * swap
-1.26 "x" type
"ab" 38
"robot"
-43 43 -8.27 * "q" "x" 34
"robot" "robot" / -14 0.08 "robot"
"q" -37 "x" * -7 17 22 -7.15 / -0.79 /
"robot" 2 dup "robot" -48
-1.14 -5.66 swap * / swap drop -18 * 40
"ab" -5.93 dup swap 39 type 6.55 dup
5.87 36
24 43 type dup - / dup type
-5.28 "robot" drop type dup 12 -32 8.60
6.59 -3 6.61 18 * type * dup drop "ab"
"x" -1.19 dup type "q" "robot" type
"x" -36 -5.67 - +
"q" 15 0.75 -1.67 / dup - dup + dup dup +
-8.61 "robot" 30 "x" "robot" + swap -5.96 * dup "robot"
"ab" "ab" swap
"x" -6 "x" + type -41 + * * dup 49 /
4.96 -42 "robot" 10 -35 "q"
19 "x" "q" -1.50 drop +
"robot" "ab" 3.28 "x" drop + -2.37 + type + / -8.25
11 "q" +
"robot" "x" + dup / type -0.95
1.79 40 22
"x" -6.31 / type -12 dup - *
-50 -8.38 "ab" + dup "q" drop 5 type "q"
-4.23 1 / -43
-7.74 "ab" swap
39 "robot" 38 "ab" -1.19
"x" 1 + swap type -7.31
-2.97 "q" drop "q" -50 swap +
3.32 "robot" "q" type / 8.61
-45 "ab" swap 7.78
"x" 37 drop -7.96 -1.87 dup
"q" 1.88 28 + + "ab" - -42 - swap
-8.69
"q" -5.64 "x" * drop
"robot" "q"
"x" "robot" + dup type dup "ab" 14 "ab"
2.51 "robot" drop 17 0.26 29 7.51
-6.71 7 - swap +
"x" "ab" drop "q" drop
7.95 -21 + type - swap "x" + * "q"
8.83 "q" - / drop * 4.65
-6.67 "ab" type -3.29 drop swap
"ab" 5 swap /
3.00 -49 - "ab" 18
-4.71 -3.10 36 drop "ab" + -
26 31 type * "x"
6.80 5.84 -11 + -
-12
-20 "x" swap swap * swap - + -5.28
-34 -2.63 * / / / -1.78 +
-10 0.70 drop 32 * swap dup 21 drop + dup *
6 "ab" -7.56 -6.26 dup *
5.43 -1.28 49 - -42 -5.99 /
-2.82 "x" "q" / -28
"robot" -20 dup -13 2.07 * "robot" "x"
"robot" -2.69
26 3.82 * type
-8.17
"ab" "ab" 13 type "q" 2.06 / dup dup 6.97 type *
-5.43 "x" -0.55 type "q"
"robot" "ab" "q" - drop -8 drop
-4.80 22 0.30 swap -3.48 drop * drop type -6.83
-31 "ab" "robot" * -4 - -8.77 swap 22 -2 3.34 8.03
"robot" 7.45 type drop 26 31 -27 swap / "q" 14 46
-19
-6.91 "q" "robot" "robot" + -43 - swap "robot" + swap
6.58 8.77 5 * -3.73 "x"
37 5.54 + drop dup 13 -
"q" "ab" - type "q" - type 18 dup -6.06 type *
-7.79 3.42 "q"
"q" -2.29
6.80 "x" / * drop 15 *
"x" "q" 8.95 -7.10 swap - type drop
"x" 24
-46 "robot" + "x" "robot" * "q" dup - -2.59 type
"q" "robot" dup / type dup type 1.72 "ab"
30 38 swap drop - type 31 type type drop 3.24
1 "x" + type + + "q" / 29
"x" -2.16 10 "q"
"x" -1.09 + - -37 type "robot" "robot"
"ab" 5.21 *
6.84 -4 "robot" 1.57
"robot" "q" "ab" "robot" + - * 3.40 / * - 5
"q" -25 -37 + 1.33 + "q" * 0.03 4.30 +
14 4.70 drop + 4.74
"ab" "x" "ab" + dup
-10 -6.33 + 49
-12 -2 "x" * * * - "q" dup drop drop /
-1.79 "robot"
-4 "q" * "q" + / -2.99 drop drop
21 -3 dup 13 type 6.23
"robot" 33 * -6 -2.11
"ab" -1 dup *
0.48 -50 type -32 - 9 dup dup "robot" 8.65
"x" "robot" * / 5.63 / -6.17 swap -
24 4.98 * / "q" swap -1.52 dup
-5.70 -5.36 swap drop "q" "q" 18 "robot" drop
"q" 9 -2.37 type * dup * drop 46 swap * -
"ab" 27 type
11 29 dup "robot" / "ab" dup -3.11 * "ab" -7.65
-0.06 "q" "x" -5.50 -2.33 -21
0.07 "robot" + / type 7.66 -31
-40 "robot" "q" -5.50 -47 6 "robot" 5 dup type
"x" -5.43 -
-39 14 + -16 + - 3.07 swap
-5.12 "q" + type "ab" drop +
-45 4.06 / type * + type swap 3.50
8.17 "x" type "robot" 18 -2.12 5.66 * dup type /
-1.29 37 "robot" dup - / "robot" 3.73 2.94
"x" "robot" - 3.23 -15 "q" "q" 11 "ab"
7.90 "robot" * 1.90 dup dup type -26 0.70 "robot" "robot"
-3.30 "q"
7.95 "x" / 5.42 -4.90 28 6.66 swap - drop "q"
-17 -6.00 - 11 + swap "q" swap "q" swap
4 "x" dup * drop type swap + swap type "q" drop
-7.80 49 * * * swap drop dup dup *
5.75 3.32 drop 7.20 "ab" * /
29 2 - -26 type "ab" type
0.69 5.19 drop
"x" 8.25 "q" swap / 49 - dup + swap / type
7.88 0.28 drop dup / * "robot" - /
"ab" 45 type / "ab" 2.85 * + type -50
7.09 7.69 dup
"robot" "q" - "x" / * "q" dup -1.35 -7.07 "robot"
"x" "q" dup + type type swap * / / *
8.47 "x" type "robot" 0.51 * 8.11 drop
1 -7 * 7.44 /
-3.09 50 dup / swap 31 drop
-4.86 -13 "q" type + "x" swap -8.45 "ab" / 27 dup
-10 "ab" -0.98 /
"ab" 11 -7 3.92 type swap -2.06 dup swap
-7.85 6 *
"ab" 3.49 6.51 swap type -19 dup drop 5 drop +
-30 -4.62 1.80 -9 * -5.56 "q" drop + "x"
21 "robot" * / swap + * swap 2.11
"ab" "q" + 1 dup drop * - *
3.83 -33 - * 44 / / 37 4.98 dup type 7.18
30 -7 dup - / - + 2.49
"x" -1.23 type -17 drop drop +
8.86 "x" swap swap
-6.79 -3.87
0.39 -1.47 -1.55 type dup swap -18 "robot" drop * -3.03 3.14
"ab" 14 type "x" drop
1 -1.25 drop type / drop type 6.75 5.33 *
0.71 3.35 5.45 5.75 "q" type -
"q" 0 41 * -21 swap
-50 0.44 33 39 swap - swap - 7.04 drop "q"
"q" 35 26 -7.91 "x" 8.67 / "q" -5.66 37 45 "ab"
-4.35 "ab"
23 "q" "ab" / - + drop * type
1.53 37 "q"
36 28 * / swap
"q" -0.06 + * dup -
"x" -6 -
-3.26 "robot"
5.19 7.80 dup "q" type / -6.94
20
-4 -3.58 + type
8.25 -4.47 -38
37 5.40 1.13 "q" -3.72 2.55 type
-37 -6.19 type drop - + type * * -22 -
"x"
"x"
-42 -6.80 -1.55 + -3.59
5.47 -3.93 "robot" / +
35 35
3 -4.25 dup dup swap "robot" 44 dup drop "q" dup "q"
"robot" "q" * -30 "robot" "ab"
"robot" 6.27 -2.27 17 "ab" dup -3.11 * swap swap -6.00 -33
-2.70 "robot" -11 drop drop drop
5.63 1 - swap / + -6.45 * -5.08 +
5.38 -27 * * type 42 * + type *
-19 -15 + type / - 38 drop swap * + swap
-44 -50
-25 1 7.70
-4.83 "x" * 7.79 swap * /
3.44 "ab" * type -21 dup "x" drop "q"
39 4.61 type + -5.86 type type "q" dup swap
3.96
4.57 -29 -3.29 type dup - "robot" "q"
40 8.15 dup swap + dup +
-33 -42 "x" - 50 - dup / dup drop
"x" "ab" dup -0.95
42 "robot" -2.10 "x" / * / type
-1.75 -40 -44 * + drop - -2.68 + / /
49
"q"
"q" "robot" + "x" "ab" "x" -6.56
"robot"
-1.80 "ab" / / "q" - + dup -
6.37 -8.04 -12 +
"robot" "ab" dup - - - + + "ab" "robot" drop "robot"
-4.23 8.27
-45 "robot" swap 3.41
"robot" -0.80
-25 "ab" drop "robot" 48 26 19
"robot" 4.83
3 18 - swap 7.05 18 -42 -
4.40 -13 "robot" type "q" + -26
4.32
"x" -1.49
"x" -10
8.45 3.09 drop -4.90 "robot" / "x" *
"x"
"ab" "robot" type -3.29 + 6.66 * swap 17 swap 22 *
"q" "q" "x" "x" -37 -0.39 * 4.15
13 -10
21 -6.02
4.20 7.47 swap / swap type type drop swap type drop
1.31 -3.05 "x" 24 / -7.63 9
"x" -42 drop type
-8.45 "ab" drop swap
-8.40
3.15 3.54 swap "q" dup "x" 2.29 - drop -7.00
-6.58 6.35 42 -20 -7.18 dup 8.52
7.00 "q" type - "q" - 3.07 * swap -18 1.11 drop
2 27
10 -46 / 7.67 drop 5.61 swap dup -
4.13 -4.03
"q" 32 - -7.66 dup 12 "x" swap -5.58 dup
"x" 48 swap / type "robot" / /
13 -3.68
38 "robot" 31 -6 /
-8 -4 "ab" -21 -19 * * - 4.53 type
4.86 6.77
-8.68 -19 -49 drop - dup
-2.26 49 30 "ab" -7.18 - + dup -
1.85 -49 -2.59 drop
"robot" 2.94 swap 7.59 / type drop * * dup - "q"
-48 "robot" "robot" -0.77 -5.55 + *
-6.54
-14 -6.49 -1.69 -29 2.37 8.84 / * "ab"
-7 0.62 + - - / 2.72 23 swap swap *
"robot" "ab" swap -21 - "ab" "ab" *
-41 "robot" -7 + + 4.87 2.08 -6.09 drop
"q" 47 - drop * / "ab"
"x" "ab" / dup drop -2.82 + "x" *
-6
-23 "robot" / * *
"x" 0.69 swap
"q" -17 type "robot" dup / +
-34 0.12 "robot" dup "robot" swap * / type -7.81 dup
"x" -5.79 -7 type - drop type -42 - +
"q" "x" -43 / 42
"ab" 15 dup 6.71 type 4.26 dup /
6.40 "q" swap swap -4.85
"ab" -0.90 1.71 - -5.14 / dup -34 -40 + 0 5
-19 -8.13 -2.47 dup -0.50 6.31 "x" drop "q"
31 "ab" 1.43 -7.74 / "ab" dup + +
"x" -49 dup -
6.24 "ab"
37 22 28 - drop dup "ab" swap -5.53 -
"x" -4.68 16
"robot" "x"
-0.87 "x" type -36
8.43 -31 - -35 dup + 42 -
"robot"
-45 -8.18 dup -
45 -17 drop / type "ab" 4.36 drop drop +
0.49 "x"
0.35 13 type "q" "ab" "ab" -48 - - 6.17 +
"robot" 1.32 type -
-7.00 "x" *
5.87 -6.03 "robot"
8.89 "ab" type * 40 38
7.44 -5.36 swap type
-5.49 "q" 3 3.41 "robot" - - 6.39 -22 4 -19
1.63 "x" 42
-13 -7.26 0.81 + swap 0.91 -12 -5.00 dup drop *
"x" -6.52 - -27 dup drop -18 * / 4.04 drop
-8.12 "robot" "robot" -8.22
-6.64 "robot" / type - "robot"
"ab" -8 / 2.65
9 -0.61 - "robot" - - type 48 "robot"
-5.77
"robot"
-46 -5.50
"q" "q"
"ab" "q"
"robot" -3.07 "robot"
6
-33 -3.61 -7.72
-16 -19 + -0.57 * / + -38 *
38 7.17 "ab"
"ab" 2.90 - type
-2.14 -5.09 + -
8.77 "robot" dup swap "x" drop
-4.44 7.82 * dup "q" "ab" 21 swap "ab" dup
"q" 7.76 "x" - 7 + dup + drop
"ab" "x" swap
-8.78 "robot"
-36 1.91 - + type "x" "robot" *
"robot" 5.83 * 1 - -
32 18 swap type - 3.63 type -9 drop type
6.78 16 dup -3.15 / 5 0.62 drop
"robot"
5 35 "x"
"robot" "ab" swap "q" dup type
-5.20 -1.85 * -21
"ab" -37
0.73 5.45 -7.01 "ab" swap dup
-27 -6.77
-3.68 0.45 /
"q" -38 -16
46 2 - + type 34 "q" *
36 -4.91 drop 38 drop dup "ab" 12 + 16
-37 38 / dup "q"
"robot" 23 "ab" - "robot" "ab" swap dup -28
"ab" -7.59 6.49 swap
38 "ab" drop
4.75
-12 -21 - type drop
-8.11 31 * "ab" + *
-38 -3.64 / 29 type / "q" "ab" dup +
5.69 "x"
"robot" 1.68 + dup + 0
20 "ab" * "x" *
"x" "robot" "robot" dup type type 7.13
6.44 -5 swap - + -2
-48
4 "q" -6.94 37
-7.65 "q" dup 4.75 *
7.95 -1.49 dup + -2.35 * - swap -
3.50 "robot" drop dup "ab" type 5.13 / - "ab" "robot" type
"ab" -7.84 -38 + "ab" + "q"
"ab" "q" "q" "q" / 0.11 - drop
0.36 3 "robot"
"x" 0.98 4 5.55 type -38 "q" drop swap -3.92 6.67
-5.58 "x" - - + dup dup "ab" "robot" 6 *
6.06
3.22 8.55 drop "x" type swap - -7.59 -1.78 "robot" / -8.69
"q"
-5.69 8.04 8.12 -7.92 0 22 swap type
-2.24 -34 - drop + -49 * dup
"robot" "x" / -22 44 dup type 1 "ab" drop type /
-13 37 drop dup swap -
"q" "ab" + "ab" drop dup -6.88
-0.16 38
0.87 "ab" "q" / swap type / + 37 34 "q"
-8.70 24 - -1.86 dup 23 / dup dup -3.00 -4.32
-5.75 -6.46
"ab" 5.15
8.51 6.86 * / 7.59
"q" "robot" + drop 2.81 swap
"robot" -24 / -19 swap drop -7.76 drop drop
20 -42
-8.65 -3.77 drop "robot" "ab"
-28 -2.20 *
"q" 30 -1.47 25 + / - "robot" - 13
-41 "ab" -42 drop "robot" -2.32 - dup
-34 "x" 13 + type type
35 "ab" swap "ab" drop * -3.72
-15 8 type "robot"
5.08 -1.95
-3.10 -7.05 -5.49 dup -0.71 - "x" drop drop
6 "robot" "robot" - "ab" "ab" 5 -5.19 drop
38 "q" swap -5.18 7.01 / dup 38 -7.10 * "robot"
"x" "robot" * -8.63 "robot" / / /
6.36 -4.35 - type swap * swap dup / swap 0.57
"q"
"x" 4.69 "ab" drop -42 type / swap drop swap
"ab" 25 1.63 swap - "robot" type -8.70 4.79 *
48 "ab" type swap -30 * swap
"q" -5.71 / -1.00 -
-47 -47 type + -41
"ab" 4 / 8.52
-41 -1.50 type +
-7 "robot" - dup dup type
"robot" "ab" + dup - 2.25 -
2.47 0.01 4.69 -15 + / 5.18 -37 * "robot"
37 -0.15 "ab"
9 -31 5.72 type + drop +
"q" "q" * / dup
"x" 2 -4.29 -8.16 drop swap dup / drop -21
"ab" "q" drop / / - dup
8 "ab" dup / "ab" "robot" *
-0.77 "x" 28 drop "q" type + 0.89 + -45 "ab"
2.74 "ab" / -8 29 - swap drop
3.55 "ab"
"x" -7.84 -1 drop "x" type
"x"
46 -7.94 "robot" "q" drop * -6.38 -14 drop 26 31 "robot"
-2.20 -38 swap 0 type "q" drop "x" * /
"robot" -46 swap swap - swap -
3.88 -47
2.75 -7.58 -8.82 48 drop type / drop dup 4.63 "ab"
"ab" 3.75 "robot" * type /
-8.67 -1.72 drop -8.07
-7.38 "robot" 4.81 dup *
8 "x" "robot" 6.71 -1.49 + 4.41 4.36 - drop
"x" "q" dup * - + / "q"
7.13 "ab" * drop
"ab" "ab" 0.47 -13
-2.50 5.83 type -29 type 2 / 5.70 + swap / type
"x" -34 1.75 + type * 10 6.50 +
5.80
-0.40 "ab"
-3.22 "ab" drop / drop + type
-6.08 -6.88 dup / dup 4.62 drop 8.54
26 2.22 dup "ab"
-33 0.24 * - "ab" dup / dup drop swap
-7.02 -12 + -42 "q"
8.61 "q"
"q" 8.15 -4.12 -2.95 / + - -7.82 -
-50 -8 -8.45 -8.98 8.81
-0.78 "robot" type / / "ab" -27 "q" /
-3.44 -1.97 type - type * - + drop dup swap
1.07 "x" dup -1.61 "q" 4.83 dup 5.35 drop -0.36 drop
"ab" 4.31 * type *
-3 -48 43
"x" 8
10 -6.32 -20 33 type "ab" 2.28 -5 - dup
"ab" -3.93 + "robot"
"q" 8.59 type dup swap -16 -
-8.45 7.40 "ab" swap "robot" + dup "x" swap -6.84 type
"robot" -42 -13 -7.58 + 8.26 drop 45
"x" "robot" "x" "robot" -8.25 * 7.79 type *
43 7 - "ab"
-38 -6.66 / *
"x" 38
-0.55 "x" * + swap -21 "robot" swap type * type +
-7.25 "ab" drop "robot" 8 + dup "robot" *
-2.01 37 -3.54 type -48 39 * -8 swap
-4.08 -5.93 4.59 0.72 + "q" 46 / /
-3.99 "x" "ab" type -43 swap - -
"x" 2.49 dup * dup -8.78 dup -0.63 + 11 4.64
"ab" "robot" 45 -46 -43 38
"ab" -7.64 / * dup -28 dup "robot" +
"x"
"ab" 3.99 "x" * - dup -29 drop 19 - 3.47
"x" -2.26 dup -0.76 19 1.42 type drop -27 / type 2.62
-50 2.61 3.49 swap
"x" 8 + / drop -1.34
46 2.23 "q" "ab" type
"ab"
11 -5.13 drop 2.34 -3.69 8.28 -0.46 - drop
-20 36
-7 "robot" "robot" * drop + * "x"
-12 2.07 swap "robot" dup -4.77 type "q" type - type
8.28 -38 type -47 8.56 dup
-1.88 -33 + + / - type *
"q" -47 -2.08 + + -3.68 swap "q" swap
-3.95
"x" "q" "robot" type -13 + "q" - dup -17 - /
8 -5.22 0.81 -0.09 * + - 5.61 / * -
"ab" -8.89
"q" -6.22 -4.76 "q"
36 "ab" drop type type -12 type 40 -3.97 drop * swap
"robot" "x" +
49 -5.79 type -7.37 3.81
7.21
-22 "x" 8 swap - * * "robot" type swap swap
14 5.64 + 44 type *
"ab" "x" / + + + + "q" dup /
-18 -23 -24 7.03 dup type +
"x" -2.08 - 46 * type * drop "ab" -20 *
4 1.55 * "ab" 4.01 * "robot" "q" 31 /
-11 8.03
"robot" 30 -16 "x" drop dup swap dup dup type "x"
43 2.28 "robot"
-4 19 / "x" drop -6.60
-40 -39 / swap type * swap 3.58 dup -8.23 *
4.35 0.15 dup "robot" -1.56 swap 12 "robot"
"robot" 41
-28 "robot" 24 swap / type -6.46 type dup -5.18
4.94 "q" * type - -15 5.04 -
"ab" "x" * -9
-5.60 "robot" type -3.98
7.44 -4.91 +
0.02 "q" - 43 *
"robot" -2.71 *
"robot" "ab"
-9 -8 - 5.65 / -0.50 + -
-23 "x" dup "q" "robot" + drop / - 27
"ab" -0.21 swap
"ab" "robot" / / "x" drop swap 3.00 - * -
46 "x"
6.81 1 type + -7.96 drop * - swap swap
-6.29 "x" - - 5.33 drop -3.91 / -50 5.18 * dup
19 -5.60 -47 "ab" 6.42 + - -0.69 -
-28 24 5.33 / -5.33 "q"
-7.12 -22
-39 -45 * + "q"
"x" -3.93 + -4.39 + - -0.68 + "robot" -5.63 swap
-17 -33 6 "ab" dup dup + -10
41 -3 type - -7.38
"robot" "q" type
-30 "robot" - 24 -6.81
-3.44
24 -2.69 + swap "x"
-6.23 -8.03 dup dup 0.32 type "ab" -8.79 6 "q" "q" /
"ab" -37 dup
"ab" "ab" + drop
-6.27 -6.60 14 type "x" "ab" dup
-7 39 -17 drop
"ab" 43 * drop "ab" -4.45 5.20 -38 -2.28 "q" swap
"robot"
-16
7 -47 15 0.27 dup "x" "ab"
-29 "q" dup / - * "ab" 1.04 drop
-4.37 0.30 -
-18 26 dup * - -7 swap 36 *
-16 "x" -14 swap type dup "ab"
-13 -32 / - - *
-6.65 "q"
-16 "robot" / swap + "robot" "x"
"robot" 13 * 44 10 "q" -10 -
"x" -3.88 swap 19 / "ab" 4.95 4.37 swap * -
23 6.43 42 drop * * "robot" -14
"ab" 7.38 type + + type
"robot" -48 swap * 5.72 dup drop /
"x" -0.46 drop swap * -0.85
"q" 8.04 type
30 9 - dup dup
"q" -24 - - / "x" drop / "robot" * type -2.12
-4.35 -47 - -6.13 + -0.06
4.33 44 type "ab" - 7.32 / - type swap 3.83
8 5.80 -6.53 type -7.49 drop
15 -2 "ab" drop "ab" "ab" drop / type 37
"q" 17 * 7 6.04 - drop dup "ab" * "ab" +
"robot" -4.83 8.00 "q" swap 3.50 "x" 0.55 swap
-2.56 "robot" "q" / dup -47 type
-8.93 "q" + + / "x" type
-6.76 -4.53 "ab"
-39 50 "robot" -
0.88 -6.93 * / "robot" 24 type -3.09 39 + "robot" dup
"q" 47 -21 -8.50 "q" * - 19 +
-1.71 32 -5.89 -35 -1.13 34 0.12 swap +
-2 40
-3.70 2.08
20
"q" 19 -15 dup / type dup swap swap /
21 "x" 5.07 - "robot" -3.01
50 "robot" "ab" dup "x" type "x" 0.96 -39 dup type
-4.27 "x" -6 dup
"robot" "ab" - dup -0.83 -3 / "x"
-34 -35 48 -5.74 * drop -0.13 drop
8.77 -33 -6 46
-1.70 "x" swap
-5.11 "q" type - drop type drop / *
3.64 "q" - dup swap "x" drop swap drop type -1.83
-12 "q" type type dup "q"
26 -5.97 "ab" + type "x" +
0 "x" drop * 6.13 "robot" "ab" +
"robot" 1.46 + type / -2.42 type + swap
3.62 -4.61 / -48 drop "x" + -
-3 -7.10 7.22 37 type "robot" + -29 drop
"robot" "q" 11 / 7.14 swap * -35
-1.05 "robot" drop
0.55 "q" 22 "x" dup -19 drop -17 "x" -43 swap
-22 -40 -5.57 swap - + "x" -48 drop
4.71 12 "ab" + -7.54 drop * * type type
"ab" -2.10 dup "x" dup "x" drop + -20 *
-4.36 -8 dup "q" -42 5
"ab" -29
"ab" -41 + type -35 * /
39 17 6.72 - swap +
-4.95 9 * drop dup * dup
-0.79
"x" "robot" * swap - 6.42 type dup -6.86 dup - "x"
28 0.77 * "q" "robot" "ab" -34 -
-7.39 -36 swap swap "x" -1.35 "q"
"robot" "x" + + * -
"q" 44 dup *
-38 -8.40 +
7.47 2.70 "x" - + 8.81 +
-3 6.05 swap -17 7.57 swap swap
2.14 33 / drop -5 -3.18 + "robot" drop dup *
"q"
-8.14 "x" dup "robot" dup "robot" "q" "ab" 12 drop
"q" "ab" - swap -10 "q" "x" / 46
13
44 4.91 -3.15 /
-5.60 -2.30 type 0.09 dup -
"ab" "q" swap -7.25 dup type - -8 drop dup
5.74 -26 -3.33 1.33
-32 -5.55
"ab" 6.86 + -0.92 -6.48 - -5.13 + dup 6.76
1.27 "x" swap type - + type 3.29
"ab" "ab"
"x" 8.23 44 / "robot" drop type
-7.59 "q" type + / dup / 2.30 12 5.05 swap
0.78 -22
4.60 -37 36 "ab" 6.12 + -28 type -8.99 -17
3.77 0.49 "x" 6.24 dup swap dup 26
"ab" -16 dup dup swap
30 "q" / / + -5.22 type type swap
"robot" 6.32
44 -11 "ab" / - swap
"q" -0.48 dup -32 "x" +
24 "x" - dup 50 5.94 / / "robot" drop
-1.57 -3.29
"robot" -24 "q" 30
"q" -30 type -1.00 -8.43
-24 -18 - -44 type - dup "ab" + / / 40
-31 "robot" type 5.89 / swap swap 50
50 1.54
0.72 43 - "q" swap "robot" 7.13 dup / *
-20 -24 dup swap
-0.50
4.25 -6.11 - dup / 40 +
-1.72 5.59 "ab" "q" type -35 -2.12 /
-4.68 "ab" "x" 37 / 7.66
3.91 -7 / swap -7.30 dup "q" swap "x"
-4.98 -5.70
-7.90 "robot" 35 -6.69 7.64 - dup
-50 7 dup type swap * drop 21 -6.56 "q" 43 -4.83
"robot" "ab" drop / swap "x" type type "ab" -8.08 17 drop
-33 49 4.67 drop -29 3 -19
5.39 20 "robot" "robot" + *
10 8.97 drop swap -2
-9 -3.38 / -0.73 drop "x" 43 37 swap -35 swap
-45 -3.66 "robot" dup swap - "robot"
"ab" -4.73 15 / dup
-0.95 "x" 6 type - 2 * + "robot"
"q" "x" 8.56 + * "robot" /
28 4.42 49 / * -
45 -5.26 dup type + + 1.55
38 25 dup 5.66 type type + swap
"q" 0.94 swap "x" * -35 swap drop 40
-37 1.15 0.01 - 26 -8.68 "ab" "ab" 1.63 +
-6 45 -6.61 dup drop swap -9 -5.79 type swap
"ab" "robot"
"robot" -45 swap drop 46 swap / 30 -17 0
2.95 "ab" swap type dup "robot" / -0.03 -2.61
-5.52 "x" "q" swap dup -6.91 + type
3.21 29 /
-17 "ab"
"ab"
50 24 / - + swap
0 "q" dup 2.19 "x" * "x" 48 / swap type
8.59 -1.80 swap drop dup swap "robot" 17 / 7.48 +
-18 39 * swap swap 2.63 swap -5.83 -45 + -35
"ab" -3.15 "ab" -3 dup -6.54 7.75 -2.75 -44 -1.69
-8.96 16 type
"q" "robot" 39 -29 8.51 swap "robot" swap
"q" 11 *
"ab" "robot" -1.05 "x" -4.47 - 1.79 "ab" dup
49 3.71 -2.55 type +
"robot" -23 -11 + swap drop type "ab" / drop
-43 6.77 / swap * dup 1.03
30 -45 -0.57 drop 8.75 6.60 / -6.15 "robot" drop swap "x"
-35 -0.93 -19 -2.69 -0.70 47 - -5.87 drop
-11 2.14 dup "robot" - 23
5.35 2.53 -12
23 -6.22 -5.00
-8.85 "q" -7.16 / drop 5.12
4 1.36 "x" "q" + type type / "ab" -
42 38 "robot" type
"robot" -0.25 dup drop - -1.63 -7.08
"ab" -20 type - dup dup + -50 * swap swap dup
-8.67
"x" 8.49 drop 7.68 * "x" dup -5 "robot" type
-19 -3 swap -6.91
"x" 38 "robot" type "robot" "x" dup / 45 3.00 + drop
-7 "ab" drop -8.80 type "q" type * 6.32 -3.46 drop
-1.61 "ab" -8.10
-8.48
-26 -3.36 -49 type drop
-41 4.97 7.66 dup drop type 4.03 -1.18 3.57 /
-36
-31 "robot" -6.07 + *
12
-8.47 8.96 type - "ab" type -5.49 -7.15 dup
-7.58 24 swap
9 -19
"x" "ab" "q" - * drop
-3 34 drop "x"
-4.77 -15 type 46 * type
"x" 40 8.80 "robot"
8.81 8.24 "ab" type
-4 -7.40 "robot" -48 "x" / 6.45 "x" swap type "q" type
-23 -10 "x" swap + + swap /
"x" 9 / swap dup -0.07 drop + -
"x" 6.17 "ab" swap 33 / "robot" drop drop - -42
-6.91 -1.84 -15 dup drop * -17 -40 + type 6.25
5.21 20 swap 0.96 -6.86 type drop
-8.68 -5.43 *
"ab" "ab" swap 6.04 * dup -0.57 -
"q" 37 dup type -14 * type
-6.14 -1 + dup
-0.91 -27
"ab" 16 -3.48 - -27 -41 / -47
-4.62 7.89 / -27 / 31
"x" -32 18 2.26 drop dup type "robot" swap + "x"
-40 -7.49 34 dup -8.62 + * type type -2.76
-3 7.56 swap / "x"
2.62
"robot" "q" swap / dup drop drop
3.08 "robot" 27 -12 - /
"x" -41 swap type dup 1.82 * "ab"
"x"
-3.12 -21 "robot" 38 + drop * / -4.67 + "ab" 21
"ab" 2.74 type 12 type -6.91 / + -7 swap
36 -34 drop -15 -1.98
"robot" -6.28 "x" drop / -36 * 5.15 -28 5.22
"robot" "q" / -35 dup type / 9 / 11 "x" *
23 -13 "ab" swap * * dup "x" "robot" drop 3.04 -
-17 4.25 - "ab" - "robot" -1.66
-39
-6 34 type
"robot" 47 * - type /
7.78 -22 dup "q" - - drop dup + +
-1.47 -29 -8.46
"q" -9 swap - swap * swap 1.39 6.32
"ab" -2.75 * drop drop * 38 "q"
"q" 5.71
"ab" -8 -8.14
7.05 1 swap dup -3 -6.63 7.67 dup -21 -4.70 /
-7.34 -8.56 drop + drop + "q" -4.60 -46 / type -
6 -37 "ab" drop swap "x" -4.83 / "robot" + /
5.72 -2.54 -3 20 4.11 dup - -44 "robot" dup
-1.34 13 drop "robot" "ab" "x" swap * 12
4.37 -7.32 * type + swap drop - 45 type
-41 14 + "robot" 5.09 - "ab" 5.34 swap swap type -46
-17 -5.98 / / 22 dup "q" 12 "robot"
-2.27 -47 3.56
"q" 2.97
-4.31 0.69 "robot"
"x"
"ab" 2.93 + drop
"robot" "x" / type type / "q" type -7.80 *
"q" -1.14 4.02 dup + swap "x" * * type
"robot" "robot" dup drop dup "robot"
-33 12 /
-50 5 - / 7.64 * * "ab" swap *
-0.06 3.81 * drop * 5
-10 -0.44 -3.95 *
"x" -3.37 * -8.11
-2.51 "q" -36 * + - 0.09 swap *
-2.74 "q" - swap 7.64 * "x" drop / dup
"x" "x" drop swap / "robot" type "ab" * swap type 16
-3.89 "robot"
50 5.24 dup + -0.92 type "ab"
"robot" 7.70 -2.60 "q" dup swap swap "ab" -
-14 -8.79 "x" * -8.15 drop -5.60 -8.23 * -5 8.97
-48 "x" type
-5.59 9 drop 7.94 - type -4.07
-10 "robot" drop - drop drop 6.80 / + - type dup
7.83 2.37 -36 * type
"ab"
"ab" "ab" dup
5.05 -7.46 32 "robot" - 1.62
"robot"
"q"
"robot" 1.76 -33
17 "q" swap -3.65 + * drop 8.62 + type swap
6.47 "x"
4.08
-45 "q"
-48 36 swap + -2.92 3.89 "robot" + 5 type
5 -3.79 dup - 50 "q" *
2.92 7.06 / "q" / -5.27 swap
-2.92 "ab" -3 -2.07
-34 7.47 dup -4.92 / -12
-8.10 -0.10 - 10 + + / -0.81 -8
4.58 2.82 -3.56 - swap / "q" / + *
-2.41 -6.39 -
4.29 "robot" /
-39 "q" "robot" 8 type - drop -5.95 / -29
2 0.28 -13 drop -2.00 -
"ab" -2.54 / -10 + /
"q" 2.01 * * dup dup -4.36 * -46 dup + *
-5 42 20
3.28 3.04 "q" "x" drop / 0.51 "x" 3.48
"x" -4.83
-35 "ab" - "ab" * * - 7.15 -30 drop
"x" 2 + swap "x"
42 "x" dup "x" / swap + "robot" swap
"robot" -1.91 -6.55 / - "ab" type -39 - drop "x" 2.16
"robot" -8.11 dup
"robot" -5.16 "ab" "q" / - swap * drop
7.15 "robot" "x" "q" 2.84
6.87 -5.26 29 + "x" -8.09 -31 "robot" -
19 27 type * / -6.97 -1.27 drop drop * 20 "q"
"q" 8.09 -6.22 -6.72 "x" type
0.34 "q"
"robot" 1.79 / swap drop dup / - -5.36 - swap drop
29 -47 0 dup * "robot" "q"
4.93 "robot" -2.42 * 7.67 1.64 type type 26
-23 8.00 + drop swap -1 - 2.56
"ab" 2 - 13 -6.70 0.79 type -47 type
15 -38 swap -4.23 "ab" swap + 40 39
4.79 -19 dup 5.08 type swap dup dup swap 3.47 "q"
"robot" "q" "robot" type +
7.92 -4.14
7.02 -7 -4
-18 6.66 drop * type * -43 dup - / "q"
-49 -39 / "ab" dup / drop * - 1.90 drop
"ab"
-8.13 -6.75 -0.23
5.46
"ab" -15 "q" +
"ab" 29 / / "x" 3.85 drop 2.84 8.99 3.35 6.95 *
-2.26 "robot" "robot" -8.51 /
-0.77 1.79 4.81 "x" -33 dup "robot" -4.44 50 dup -26 /
"x" -3.14 "ab" -49 "q" drop dup * 3.03 /
"ab" "robot" * dup 0.57 /
28 -4.59 -4.15 8.04
-24 -5.78 dup + swap -0.89 dup "x" swap * swap "q"
7 18 34 * -6.19 -8.37 + 4.29 type drop dup -
33 12
24
"q" 5.66 - drop dup type 34 drop - 0.26 "robot" /
"ab" "robot" swap type "robot" "q" type "x" 4.21 12
-23 11 "x" swap type
-3.68
42 3.77 dup / "q" * 20 type +
-3.78 -5.20 / drop swap "q" type type /
"ab"
-5.44 6.63 swap -37 "q" "robot" 26 swap drop
"q" 4.40 -
-28 "ab" 5.58 "q" / -25 drop swap
"ab" 4.99 type 2.90 7.55 drop drop
-35 "ab" / 43 29
-7 7.64 -6 21 dup
19 -0.73 swap dup
-33 -39 "x" + dup type
5.75 -13 dup swap / drop drop drop + "x" -
-4.21 -33 3.44 19 dup 8.75 - -
"q" -24
-1.09 "ab" "robot" dup -2.33 swap + swap / - "robot" -6.69
6.89 4.16 dup
"ab"
6.37 "x" dup
"x"
"ab" "robot" / -40 -4.35 "q" -8.28 -19 + "robot"
24 38 type -48
"q" -49 "q" drop / dup
"q" -8.17 -5.86 + dup "x" 8 type dup 23 /
"q" "q" "q" "robot" "robot" - dup swap dup * *
"robot" -2.38
44
"q" "robot" 16 swap dup * -3.42 drop 5.85 -7.74
"x" -0.39 *
"ab" "ab"
"ab" "robot" -
-6.53 1.52 "q" / -0.14 - -5.81 / / -49 *
"ab" -4.24 "q" - 2.55 dup - + drop + "robot"
19
-3.48 "q" "x" "x" -1.05 "q" * drop 8.86 dup
7.74 -7.51 * 8.74 6 "x" 3.22 -
"q" "ab" drop "ab" "x"
"robot" -37 drop 45 -6.50 -0.02 -37 "ab" swap -1.37 30
-2.57 -12
"x" "q" drop dup type "q" 5.25 drop 6.76 /
2.69 -19 drop 4.65 - -46 "q"
13 -40 -4.34 - -0.81
"robot" "x" 8 5.33 dup - 0 - swap
5.65 -1.60 "q" -2.86 0 3.95 -8.24 *
2.21 -1.33 * dup drop -7.81 / dup -8 -
"x" "x" swap + swap dup - dup 4.87
-14 -8 24 36
-32
4.84 "ab" + + - type - "ab" "q" + -
-41 -7.15 10 + dup "ab"
"robot" -7.31
45
1.69 7.65 -18 + -0.35 + * -34 + *
1.62 7.41
-17 -3.02 * -14 0.93 type + type dup 19 dup
2.50 -4 type -2.92 +
4.83 4.34 dup - 0 dup 25
-32 1.06 -1.59 type drop "robot" type swap type -6.77 / 5
25 22 3.34 13 + type
"x" "ab" "x"
-6.76 2.49 * -8.61 - -3.72 "q" /
"robot" 3.29 /
6.95 "ab" drop - 36 drop
2.88 -13
-5 0.82 -22 -
-16 -5.60 - -17 -5 drop 3.45 type
-47 "ab" drop dup - type "ab" + - - - dup
"x" -15 -10 type "ab" type -3.63 -
-19 32 dup drop 11 -0.29
0.65 -4.46 type +
"x" 35 dup swap drop "q" * drop swap drop
5.88 -11 "ab" type 3.48 type type / swap *
-36 37 "robot" swap * "ab" drop -36 - type
"ab"
"robot" 32 -20 type swap / - -2.70 -2.45 + "q"
-3.83
"q" -8.84 / drop drop
-44 8.19 "robot"
7.69 8.17
-50 "x" drop -7.75
"robot" -8 + +
2.98 -6.26 / swap drop "robot" 45 -4.61 dup
12 46 / type type type type drop type "q"
13 -3.10 "q" / -3.68 / / -1.54 swap dup 35 /
13 "ab" * "q" / dup -21 drop 6 drop dup
"robot"
-3
0
"x" "x" + 8.28 dup swap + "ab" "x"
"robot" 15 / -7.65 "ab" drop -0.02 type - drop
-17 -48 *
"ab" -1.46 / -50 dup -1.85 * dup -4.05 -8.66
8.38 22
"q"
-7 43 - drop drop drop 47 + * /
-1.12 "robot" - swap dup "ab" +
"x" "ab" / -28
0 -7.47 type * * * dup
"robot" 50 + * / -23 25 swap * "ab"
-0.38 -31 -3.94 type type
-4.34 "ab" type drop dup / 2.37 *
11 "x" "x" 23
-46 -7.39 * "ab" 50 type - dup type swap
"q" -4.51 -27 -8.72 6.19 drop -3.72 - dup + / dup
"robot" "q" "x"
-3.04 -6.61 -8.15 -26
-34 -17 "q" drop -0.78 drop type
"robot" 25 swap dup + "robot" swap * 0.85
5.64 0.35 4.43
"ab" -8.32 drop 7.79 -21 type type
-49 7.47 40
2.76 20 -4.50 24 type type / 32 -24 drop dup 20
-1 5.68 "q" "robot" "q" swap
"x" -7.16
-24 "x" "ab" / "robot" drop / "x"
-2.93 -35 * / "x" + drop dup -39 -0.73 /
"ab" "x" / 35 "x" +
-0.89 27 drop
2.86 14 1 "robot" dup
15 "x" swap -36 swap 31 drop dup *
3.04 8.81
-2.65
47 27 - "q" / dup * + 7.48
-13 "robot" -6.16 - -0.77
"robot" 2 drop
-8.55 "q" * -15 type "q" drop drop swap type "x"
25 10 -2.67 / "x" drop dup -7.60 -6.34 -2.62 8.38
41 -6 -3.43 + "x" dup
"ab" "q"
"robot" 0.41 "q"
-42 7.50 type swap
"q" 12 "ab" + swap * -19
"robot" "q" drop dup "q" -45 + "robot" * "x" drop
"x" -17 -6.75 "q" type drop 6.83 / "x"
-8.29 "q" -22 drop -7.59 "robot"
-6.77 47 swap
"robot" 2.36 / -2.28 * -4.63 type / "ab" * 43
"q" -0.55 - * + - 13 "q" -4.33 dup
"ab" "q" - / drop 34
-6 24 drop
2.74 "q" -1.87 45 drop 8.16 -12 5.88 + drop /
"ab" "x" dup - -4.74 + type 6
-0.44 -21 "x" -49 +
-0.62 2.46 6.21
"robot"
27 "q" swap dup 4.25 "ab" swap -13 "ab" swap -47 /
"x" 5.90 /
12 8
27 14 type "x" / "q" type -5.47 7.95 "x" drop swap
-2.69 "q" type drop -11 1.77 drop type 25 "x" 28
-3.57 "q" swap -31 "ab" -30
"robot" -4.03 -25 "x" + -1.71 -4.32 swap swap drop
-32 0.37 7 "x" "robot" "q" - dup "q" dup 3.10 type
4.13 "ab" -3.34 -6.75 * - 39 /
"x" 39 18 *
"x" -4.95 -0.10 -5.30 / 11 type swap / -22
-48 -8.88 drop
-2.47 "x" + 4.57 * +
5.86 29 35 -29 type + 16 swap dup
43 "ab" / / type -3.57 type + 1.47 "robot" drop "q"
-3 5.01 drop - - drop / swap
-12
"robot" "q" swap dup
-7.85 "robot" "ab" -8.82 - swap / - -
"ab" "q" / -7.11 - "x" "x" drop "robot" dup
-6.98 "x"
"ab" -12 4.11 "ab" drop 49
"ab" -2.32 type 2.50 -27 "x" "robot"
2.26
-5.75 -2.00 swap "robot" 8.15 0.29 29 "q" 1.56 "ab"
-7.21 -0.93 type +
-4.03 0.02 * - -32 * dup /
-14 17 -32
7.24 4.94 - -37 - swap dup 8 6 -
2.68 31 /
-5.08 "ab" drop drop
0.38 "robot" type 5.62 -4.48 29 - -4.41 drop +
"robot" -19 swap * swap "x" "q" -49 type dup -6.63
45 6.63 / type 7.14 "ab" swap
25 8.32 -15 "robot" + "robot" "ab" 33 swap dup -2.47 -39
8.84 5.31 1.74 drop drop + + "robot" -27 -3.32 type
-16 -5.43 4.83 + swap - drop -7.62
"robot" 3.36 type -2.20 "x"
7.00 6.58
-1.91 -41 drop / swap swap type "ab" * swap
-7.45 "robot" -
-6.59 -13 1.82 "ab" * type + "ab" dup
2.51 2.94 8.34 -34 type + 18 +
41 "x" dup +
"x"
-25 -3.78 2.86 "ab" 20 "q" "ab" swap "robot" -16 - /
2.39 9 * swap 8.66 4.41 - "ab" -35 +
"ab" 45 * "ab" drop "q" type dup
"ab" "robot"
-5.87 "x" type type -
3.09 -1
"q" 8.04 + 48 "x" type swap + drop
"x"
4 "q" drop / "ab" swap - "q"
20 -0.85
"robot" 5.78 dup
"ab" "q" + "ab"
-2.49 1.76 drop / * 2.84 + drop + drop
-4.55 -30 + -43 drop * -6.52 swap -2.03 +
"q" "x" * + "q" type *
8.65 -38 - 7.28 swap swap "q" type swap dup
7.53 -6 + * dup "ab" + 39 drop / "x"
"q" "q" / -
0
-28 13 - * swap 29 swap / "q" 31 dup
"ab" -12 drop - swap drop type dup "ab" dup
-1.75 16 - "x" -28 -13 14 / "ab"
-6.24 "robot" -7.55 -0.59 25
-6.03 -1.94 swap type "ab" 6.57 "ab" type 3.15 *
"robot" 0.58 "x" * swap "x" type 46 -8.16 1.46 3 -1.92
0 7.93 "x" -
3.55 -47 "robot" * / drop 2.25
4.80 "ab" - 3.03 /
"robot" 7.74 * *
"robot" 4.41 + -1.63 30 + / *
-0.21 5.35
"robot" 0.09 type + swap + drop "q" drop
"q" 3.71 * "q" type / + dup - "ab" - *
"x" 0.45 "robot"
-18 -0.37
-33
28 -41 -0.19 type 6.06 "x" + / -14 drop + type
0.55 0 "robot" 6.62 dup type "q" type 5.29 swap swap drop
32 "robot" drop type + - + "robot" 4.06 swap
6.88 -8.43 dup -1.35 dup 6.67 - type
-47 -48 -7.53 - -33 drop * -18 dup "q" +
"x" -2 type - dup "x"
3.77 -18 dup "q" * "q"
-5 24 0.72 type
0.25 "robot"
1.46 2.00 type - -1.78 swap "ab"
"robot" "q" drop dup 19 dup -36 "robot" drop drop
-13 -30 - 0.51 -0.99 -47 -1.04
-2.10 "robot" type 36 dup "q" 3.65
-4.67 -3.91
8.72 5.28 "q" 42 "ab" / + swap -6.29 type *
-3.57 -47 dup 5.35
14 3.44 + dup "x" dup -1.30 drop swap -4.79 / -
"x" "ab" dup "x" + drop
-0.84
-0.39 -5.45 - "q" - + type
"x" "x"
9
"q" -38 type / dup
20 "x" "robot" "x" -2 drop dup "ab" -8.12 -47 *
-0.65 "x" type + 6.70 + + "ab" "robot" 6.94
"x" -4.72 -7.57 -2.64 "x" "x" 0.36 + drop 3.93 * type
"robot" 6.69 35
-8.07 -1 + 0.99 11 "ab" dup
"x" -34 5 swap dup -19 +
-50 "x" -44 swap 23 / swap + 3.14 -11 type dup
-5.83 "q" drop * dup "ab"
18 31 type 2.28 - "ab" dup -6
"robot" -1.46 * -3.66 type type "x"
19 48 + -8.52 - -19 dup 0.39 31 * -2.65 *
"ab" -2.99 drop "q"
"q"
"robot" -4.44 swap + * - * -13 drop
-1.65 "robot" -24 "q" - type +
-2.25 6.28 + "q" drop 19
"ab" -29 "x" type
16 24 "robot" swap 5.69 + swap * 46 -48 swap *
1.01 "ab" -13 -6.02 -2.58 2.23 dup 7.53 "ab" drop
"q" -2.58
5.58 "ab" "x" 26 -0.70 / / drop - swap "x" 5.57
6.56 12 swap dup / type type
-13 -0.21 7.88
7.14 "robot" /
-2 -7.80 34 * drop -4.09
-3.18 30 - "x"
-45 8.42 + 5 / * type - +
-3 34 type drop "robot" -5.06 -5.58 drop - "x" 8.08
-16 -15 -1 swap - -0.21 2.25 /
39 20 / -49 / -27
-14 -33 - swap dup "robot" drop - swap swap -4.56 /
"robot" 4.53 dup "x" - dup 6 type
-44 -16 dup type "ab" swap
"robot" "ab" - / -
0 -34 - + swap / + +
40
"x" -7.51 -40 + dup "robot" 36 "x"
12 24
"q" "ab" swap * 0
-14 7.61 / swap -19 dup /
6.97 "x" + drop dup
"robot" "q" - +
"robot" "ab" 3.13
"q" -41 swap
-2.08 -37 swap "q" "ab" "ab" /
-26 -38 "ab" + - dup type swap "robot" /
3.67 "q" *
-0.71 "ab" "q"
"ab" "q" "q" 33 * + "robot" * -
40 3.42 dup swap / + -5.59 swap -4.71 -24 "ab"
"ab" 5.92 21 * - drop 7.77 dup -0.04 0.09 "robot" -0.98
"x" "x" dup type type - + -40
"ab" "x" "q" dup dup - * -
5 0.18 / dup * + + + swap
"ab"
-5 -4.40 "q" swap
"x" -5.17 type 5.32 11 type drop "robot" "robot" -5.57 type
-25 "q" swap "q" - * /
-3.02 1 + drop -15 type * 6 "ab" "x"
-8.97 5.02
-3 -49 swap + dup
"robot" "x" -50 type dup 0.25 -1.36 -5.45
45 -1.01 0.91 7 dup
-3.90 -11 type
-3 -2.29 - 3
-12 2.31 -0.93 7 / "robot" swap * -16
"x" -6.61 "ab" -12 * swap -0.51 drop -
-1.63 "q"
-6.82 "x" 2.95 -7.95 drop -26 -7.26 / -13 dup -
6.74 "ab" drop drop dup "robot" 1.38 "q"
0.15 "ab" * + type + swap "robot" swap + type +
4.42 "q" swap 8.03 -0.75
-39 0.63 type dup drop - -30
"robot" "q" 4.78 + swap -31 + -42 -
4.50 0.65 type 17 3.67 drop -7.79 drop drop + * -5.48
"q" "q" type -5.07
2 39 16 dup 28 -42 swap dup
-4.24 6.31 31 /
-20
-38 "q" -
8.61 -7.30 / drop
0.26
30 -18 *
0.31 8.52 swap 1.74 -7 type
-0.54 -6.89 -4.20 6.18 drop
-4.38 -42 type * 8.02 "ab" * *
12 "robot" "ab" / "q" / 46 "q"
6 -1.49 2.67 *
"robot" 23 "q" - drop drop
-43 1 -37 * "ab" / dup
"q" "q" -48 + "robot"
-5.53 37
-12 5.90 1.32 dup -6.12 dup
"robot" -0.83 -4.30 "ab" * 4.74
-27 "x" dup / drop type / type 7.09 "q" "robot"
-17 45 38 "ab" type 4.62 28 -
-2.40 "q" / "q" swap dup / drop
1 -4.10 / dup + -16
"robot" 7.05
"x" "ab" -4 type
1.75 12 * dup drop -26
3 3.03 4.52 / - drop swap / -5
-0.25 -30 + "x" + drop "q" swap
-36 "ab" type * type / 7.48 "robot" -40 type *
46 "q" * dup drop type * swap
9
-5.23 8 "x" type 50 -38 + +
-27 -29 18 drop dup dup
-9 "robot" "robot" + - * "ab" - / swap -6.74 -0.06
-7.32 -6.61 -4.31 -8.06
"x" "q" + type "ab" / -7.71 swap dup * / 4.06
43 -5.26
-45 34 -
-3.52 42 type / -3.36 drop "ab"
40
8.02 "ab" dup swap - -7.47 type /
27 4.35 "robot" -42 "robot" type "x" -6.65 drop
33 "x" -44 dup * 4.79 +
1.95 "ab" dup 4.69 drop type "q" 0 -16 *
-5.96
-6.66 "x" / type + * "ab" type -10 type "q" 1.99
-11 14 /
"q" 3.91 swap drop
"robot" 33 type 1.30 "q" -5 dup -3.42
-7.52 "ab" + 8.09 "robot"
"robot" 31 "q" 38 1.50
-5.32 "x" -2.42 * dup -6 swap -39 "q"
-2 "ab"
6 27 drop dup * * dup "x"
41 "robot" drop / drop "robot"
"robot" 6 *
-24 -4.82 -32 31 - - drop 14 10 -6.16 * -
7.08
23 6.11 type -43 + type swap swap type swap -47
"q" -4.39 +
-5.44 14 23 7.79
-40
-2.23 "q"
49 "ab" drop - / - + 6.46
-7.83 -9 + 7.94 49
"q" "q" / swap + * + "robot" / 8
"x" "x"
-48 -12 "x" dup 20 swap drop drop swap "robot" +
-10 12 type 46 "x" 1.59
12 4.71 -7 * - 8.25 50 -7.37 0.47 swap + swap
-15 -27
-7.53 -9 "x" "ab"
-1.63 -8 -31 * "x" / swap "robot" 19 dup "ab"
"robot" 4.40
33
"x" "ab" -7.47 swap drop - type 6.37 swap -31 -
"x" 2.10 swap type * drop "x"
30 31 "robot" "ab" type swap
6.94 "q" "ab" swap * 10 swap 8 type
7.89 -8.67 dup "ab" * swap -6.58 swap
"ab" 7.65 - -7.41 "x" type / * -4.45 38
-4.72 8 dup - / -26 / / drop
"x" 34 dup swap - swap drop + * -2 -2.52 /
-17 "x"
25 -0.44 "robot" -6.13 dup swap 3.80 + drop /
30 -4.68 * * -2.91
39 "x" -1.62 swap dup 2.76 "x" 14 "q" -8.84
2.01
"robot" "x" "ab" swap + +
-16
"q"
6 -14 *
"x" "x"
-4 "q" "ab" "ab"
-25 "x" -2.82 drop -
3.64 "robot" / swap / * -49 -47 3.78 + dup type
-4.72 -8
"q" -24 dup -4.91 / - + dup "robot" dup "ab"
8 1 +
"x" "x" 28 swap 24 2.60 - dup 8.87 "x"
39 "x" * + swap / -11 swap
"robot" -5.99
24 32 -50 drop dup "q" -0.45 dup
9 25 -37 8.69 "robot" drop swap type drop
2.43 2.01 * -3.50 * * dup type / -2.28
9 -3.36 "x" 4.85 "q" / *
-1.29 -21 "x" -7.30 -5.57 + drop dup
"ab" "q" 43 - swap
"q" -17 swap / dup 2
"robot" "q" type 39 19 drop swap * * "q" -
"robot" -49 +
0.53 -6.20 "robot" dup + 3.20 dup 0.19
25 "q" swap -18 41 type
"x" -6 -3.30 "ab" -42 -8.27 dup * / swap type
"ab" 3 + + -14 42 0.66
6.82 -28 * 0.90 -8.75 - swap 1.73 5
-1.48 -4.00 type drop + "q" * / / 5.01 + /
-36 "ab" "ab" "q" / swap "ab"
-2.21 "robot" * swap
15 "x" drop
-18 -4.85 swap type dup dup * 32 - * drop -4.95
-8.87 5.41 *
-4.43 -2.63 * type - "robot" 49 - dup type 7.35
40 "x" type "x" dup
"ab" "x" "ab" - drop type + "ab"
1.03 "robot" type "x" -8.48 "robot" 0.90
-7.27 "ab" type
0.94 7.44 - + "x" "robot" *
-0.05 2 1.70
-3.56 "robot" 4.44 -33 / "ab" dup "ab" -9 /
-38 -2.02 6.55
1.87 "q" * - 38 -38 * * "robot" * / dup
4.91 "robot" * "q" "ab" drop * -
-14 7.51 swap "robot" * -44
"q" "q" "ab" 34 -27 - dup drop "x" + / "x"
"q" 18
-30 "ab" dup type "ab" -
"robot" 6 "robot" / 4.84 drop swap "robot"
32 "x"
-1 -49 35 * "ab" swap dup
3.60 -6.53 - 22 dup "x" / / "robot"
"ab" -7.54 type - + /
-6
"q" "ab" * dup + + 8
-4.81 "q" 4.34 dup 4.82 dup
-16 "q" 8.97 -7.90 49
19 -6.09 "robot" dup dup "x" -34 "x" type + dup
15 -7.98 "q" type
5 -5.96 - dup "robot" 2.10
-25 29 4 -35 5.35 -36 * - * drop "x" -8.58
-15 -5.87 *
24 -4.22
"x" "q" -6.58 24 * type
"x" "ab" - dup drop
33 -33 type dup dup * +
"x" 3.98
-22 2.84 + "x" "x" * 6.93 -27 / swap dup
"x" -1.93 "x" 10 + - drop "q" + type
-4.84 "ab"
"q" -3.10 swap -0.92 dup 1.49
-19 2.66 2.66 * "ab"
"ab" 17 "x" / *
7.02 "x" type *
5 6.09 / * * drop 5.19
1.71 "x" -18 drop dup - * 8.95
1 -7.73 + * swap "ab" / / +
-5.49 "robot" 7.22 -7.19 3.95 "ab" type "x" - * 23
"x" -29
"q" "robot" *
-4.20 "q" "robot" / * drop "robot" - - 43
8.13 "robot" "q" drop - swap -
-0.93 6.85 dup drop "x"
-5.87 -2.20 + + dup swap *
"x" 32 dup "robot" - + 31 3.83 drop type
4.01 45 dup drop - type 1 *
"x" -43 / swap 5 42 dup - 5.39 swap dup drop
"ab" -5.59 dup
"q" 0 33 swap + 32 + drop
-3.45
3.15 "x" + + * -43 type -50 swap / - +
23 -3.22 -39 8.08 "x" "x" 5.05 * * 44 drop "q"
5 -15 drop type drop + -38
48 39 42 * -14 drop drop /
-1.90 "ab" * / "q" drop - + -6.54 -0.04 19
-3.98 "ab" "q" * type
"ab" -6.02
6.25 "robot" * dup -43 30 2.05 swap / -18 swap
"q" 6.95 * / * / * "x" "x" +
"q" 3.99 + type + -19
41 "q" * swap
"robot" 7.91 -3.19
"x" 8.54 drop
-5.10
45 50
5.38 "robot" drop - type "ab" -44 drop type
-13 31 drop + - -2.91 / swap drop "robot" -0.55
-6.89 11 21 drop
-8.21 23 0.70 "robot" -0.46 - drop *
5.50 -7.26 - swap drop drop + 19 dup -2.98 18
-13 "robot" 4.96 type - "robot" 13 + / drop -9 2.93
5.15 -21 "q" swap / 45 / drop type swap
"q" "x"
"q" -8.16 -8.34 - dup "ab" 27 +
-35 -5 * type
"x" -8.81 type drop - 5.28
-2.72 -7.46 + -
7.32 -25 9 24 type "x" drop "robot" -
-39 -5.80 swap + - * dup swap "x" /
"robot" -39 *
12
0.08 "ab"
1.64 21 + swap -48
"x" -37 type type - swap swap swap 17 / + swap
5.43 42 + 36 "q" -41 / - 0.53 -25 -41 *
3.95 -7.52 + "ab" - - type drop - 7.83 dup "robot"
23 -34 -0.68 drop -4.18 swap
-3.87 45 3.75
-3.85 -49 * type swap +
"q" -5.53 5.05 + + * 21 - -
1.84 "ab" dup drop "q" * - type * -2.00 - /
-3 "x"
"robot" 45 drop 47 "ab" drop "robot"
-5.85 "ab" / -
-32 7.35 - * + 36 -0.15 -1.64 *
-3.27 2.70 * "ab"
"robot" 2.18 swap 4.10 -8 drop 50 / *
"x" -10 dup dup type 6.99 -0.01 drop
37 38 / - -0.71 - drop "x" type "x" type
10 "q" dup type drop * * dup
-26 -26 drop * "x" / -35 -1.62 / "x" swap -24
"x" 1.68 type dup swap - 8.98 -42 - / -
"robot" -3.25
"x" -0.96 swap 7.75 6.43 21
6.80 "x" type / * "x" swap 4.57 drop * "ab"
-23 "x" -
-4 "x" / drop / 42 26
-27 5 swap
37 48 * dup dup "q" swap type "x"
-46 "x" +
-8.76 -1.39 type 29 -1.11 type + 36 * type / -34
"q" -8 -
"ab" "x" 1 dup type type drop /
-49 -4.62 * / -1.48 type -6.65 -4 swap type -
"ab" 6.59 - "robot" * * / dup + / 0 /
-7 -43
-2.89 45 "q" swap dup swap / / dup 1.54 type
-11 "robot" / swap -
5.51 -1.94 "ab" "robot" -28 "x"
-5.64 "ab" swap swap -6.60 "x" -43 drop - swap *
"ab" "x" dup drop "robot" /
1.89 19 type
-1.66
-43 -3.34 "x" drop 1.64 -9 -0.20 -0.99 * 3.47 -3.06
-7.19 "robot" drop -2.87
"robot" 8.10 / *
30 "x" "robot" + swap swap / swap type *
-8 "x" dup -28 - /
"x" -31 0.01 "x"
41 "ab" "ab"
"x" "q" drop + -20 swap drop dup 1.70 "robot" type +
-4 "robot" drop / dup type / -35
"robot" "robot" - -13 "robot"
-44 -4.54 drop drop / -1.49 4.80 "x"
0.88 "x" type dup
"x" 19 -4.95 "x" / type - drop dup dup
"x" -32 / / + drop
"robot" -4.76 / swap -6.00 21 25 drop "robot" 50 * 4.78
"robot" "x" + * type 2.24 swap -6.34
-43 48 type -2.55 type "q" + + drop -3.57 / -4.37
50 "ab" type dup drop drop + *
6 -27 type "x" -19
42
-24 -2.71 16 type * * -0.35 / "robot" type type swap
"x" "robot" type
-14 -43 dup 0.93 "x"
-4.74 22
-25 -7.45 -39 -4.94 / "robot" "q" "q" swap type +
"q" "x" -49 - - swap "robot" drop 0.37 type "ab" swap
"q" -5.92 "robot" swap * * 2.41 swap swap -9 * /
-22 3.20 drop
26 "x"
"robot" "x" "robot" "x" "q" + - drop -0.83 "x" 5.75
"ab" "ab" 0.40
-8.84 -2.35
-8.09 0 / * dup - "x" swap 28 *
-20 "x" type dup "ab" / / type -10
-3.31 -2.55 - -50
-28
2.49 5 / drop - "robot" 34 5 "ab" swap 5.79 "x"
"ab" 0 * / -2.82 dup dup "x" "ab"
-46 0.44 dup drop "q" swap 5.42 -5.44 8.86 10 /
-3 "ab" "robot"
-0.20 -25 +
"x"
-7.28
3.12 "ab" swap
"x" 7.27
"ab" 44 - -26 dup
"ab" "robot" - "robot" type 22 4.29 + 7.07 drop dup 27
-43 "q" 11 dup 29 drop -2.46 dup
"robot" "robot" -
8.04 "robot" -0.78 / - dup dup *
-3.18 6.30 swap
"ab" "robot"
-37 -5.42 drop 6.88 - dup 32 38
-3.99 -5 "x" + 2.57
37 "x" swap drop 1.85 - "q" - type type -28
"x" "robot" / + drop / "ab" +
-49 "q" type 7.06 drop -2.80 drop
"q" 48 * + "robot" - * 6.33
"robot" 9 "ab" drop swap "x" "x" swap
-6.16 -1.01 / *
6.11 "q" * 5.82 swap
-35 6.18 "ab"
-50 -3.05 swap -11 * "ab"
"x"
-8.81 -5.48 swap swap "robot" "robot"
-3.79 -16 8.53 "q"
"q" "ab" -3 / - drop drop -16
"q" 9 *
"ab"
-26 34 + -1.57
"x" 7.94 "q" "q" * + dup
-6.53 "robot"
-49 3.41 * 7.96 23
5.79 -8.79 -23 / dup "x" * 26 -42 drop -
22 -8 swap - / type drop "x"
"x" -0.79 * * type drop swap type -40 -8.43 "ab"
-7.42 3.62 * -34 4.46 * 7.54 "x"
"robot" -5 + -8.09 drop dup "ab" swap "q" -
-20 1 "robot" 43 * "x" 0.11
8.68 -6 type type "ab" 48 2.89 - dup
0.97 -6.81 swap swap "x" "robot" type type
-3.71 "q" -36 16 "ab" -50 -8.55 type - - drop
-6.65 "robot" + -3.79 - "x" "ab" 5.38
2 8.80 - -4.89 drop dup - drop swap drop -5.56 swap
1.60 "robot" swap + type drop 25 - -45 drop
"robot" 5.81 / 8.31 drop 8.27 swap 5.39 drop * / -
"q" 1 / / / "q"
-7.70 "ab" / -3 swap "robot" * swap * * type
"x" 8.62 / / 7.55 + drop -41 -5.81 1.68 dup /
5.24 -43 dup / +
"x" "q" - * /
"ab"
-50 "q" + * "robot" - - "ab"
6.92 0.54 swap + "robot" + type
48 "x" 33 - -49
"q" 0 "x" 5.29
"robot" "x" -37 - "x" 6.95 dup + dup "robot" dup
19 "ab" -5.58 "robot" -26 "q" dup
-13 "ab" 49 drop "x" -
1.97 11 / drop 20
41 4 + + -29 - 0.42 "robot" swap 44 + drop
2 -3.91 type 4.67 / / swap drop /
-2.70 -1.80 swap "x" /
"ab" "x" "ab" / 7 swap / swap -
"q" "q" swap * * + * drop swap -50 + dup
-4.78 -19 3.89 -2.17 -7.31 swap
"ab" -42 30 type "q" -21 "x"
14 -34 type * -8.20 type 6.85 +
-48 45 "robot" -0.29 "robot" "x" *
"x" 8.07 swap +
32 "x" + -18 "robot" - 2 dup 31
5.47 -15 / / / / drop
1.34 "ab" * type
-5.34 -6.97 19 / swap
-10 "q" 43 / + + - "robot" + 38 swap
5.38 "q" -6.67 + drop type "x" swap drop
"ab" -3 4.17 / dup "q" - * dup type 20 8.70
-2.49 -4.10 "robot" - -31 - swap -4.47 -15
31 49 swap -1.08
-21 -41 + -44 type drop / dup -39 33 "robot" *
4.66 20
-7 "robot" 6 "x" - /
29 "ab"
-30 5.24 - -11 "q" +
26 "x" type / + drop 6 -6.36 "ab" + drop
44 14 type -5.58 + swap dup -
"q" -1.84 swap -2.91 type * 50 -2.38 -25 -0.92 -34 +
"robot" -10 * 7.65
"ab" 6.63 -6.86 type /
-2.00 6.32
"robot" "q" swap 8 type type * swap dup
-5.85 "x" -45 / 4.56
"ab" "ab"
"x" -14 + type 7 "x" -6.20 dup "robot" -3
-8.20 "robot" -4 * -21 10
"ab" 35 -4 * "x" dup drop -7 +
-25 -46 drop -12 6.18 - * - * + *
"q" -19 dup "robot" drop + dup type 21
-10 "x" type drop 0.84 - - - - dup
-4.34 -0.93
"x"
-20 -8.79 * -4.93 / "robot" "q" type 3.98 13 7.00 -
0.17 "q" dup 19 type 7.45 / "x" swap 27 31 -
"ab" 32 "ab" - "robot" "q"
-13
4 -7.43 drop /
-3.49 3.91 "x" dup / "ab" type * * -4.71
-8 -31 "ab" type * dup 3.60 + 29 drop
"ab" "q" 5.06 - - -5.05 "q" type swap dup /
0.65 0.60 -3.66 "x" "q" -16 type dup swap dup -
-8.45 "ab" -49
-8.02 "q" swap
8.71 -2.66 swap type 6 47 -8.08
"robot" "robot" / * dup type drop /
3.45 -6.06 * swap "robot" "ab" "x" type -21 - 2.40 swap
29 -13 "ab"
36 12 -
-19 "ab"
"ab" 2.74 -29 -31 / -24 type swap
11 "robot" "robot" drop - type
2.36 "ab" -0.32 / "robot" swap -24 30 -
-2.67 -3.42 swap -15 6 * -
"x" 8.62
1 -7.32 * type 6.18 / - 7.39 * -1
"q" -8.25 "q"
"q" -7.05 * drop + / / "ab"
"ab" "ab" type - drop drop dup
4.31 -1.98 dup -5.28 30 drop / "robot" type "robot"
47 5.28 type "robot" 50 * / "q"
"ab" "ab" + "x" - drop / type + -13 /
34 -6.78 type -8.63 1.64 swap - 19 dup + swap
-44
"x"
"q" -8.08 "x" "robot" +
-4.56 -50 -8.24
30 "x" / -24 * - / 5.91 dup - + -
4.35 -26
-41 5.44 -34 swap + -7.94 dup 41 - 46 dup "x"
"robot" "q" -21 drop -0.88 type
3 "ab" -43 swap * drop "ab" 44 /
-6.05 -15
"q" "ab" -17
5.44
-1.18 "ab" "q" - 4.01 / "x"
-43 "q" 0.46 swap * drop -3 "x"
-1 -1.78 + + - dup "x" 41 dup "x"
-6.83 "q" "ab" -13
5.44 -2
2.75 -8.65 dup - drop +
"q" "robot" type type type "robot" + "q"
38 "x" 5.39 / 2.37
43 -43 swap / * * swap "q" 13 *
21 -7 -3.34 drop drop + dup "x"
-16 2.92 * + + swap
19 "q"
19 -6 "robot" 35 "q"
"robot" 29 * drop dup -44 "x" "ab" dup "q"
"ab" 31
-16 -11 * +
"ab" -3.67
-8.88 -8.39 1.65 "ab" 49 swap 19 "q" -0.29 * /
-41 -34 drop 43 "q" 4.19 * 16
"robot" 30 -29 drop / -4.85 + 5 swap / 0.32 "robot"
-42 "robot" "robot" type
7.32
"robot" 27 "ab" -3.85 -8.15 + 1.46 "x"
"robot" 6.91 swap dup dup swap -48 drop type "ab"
-39
"robot"
21 -46 / -15 / -8.68
"x" 32 "ab" drop drop -9 / 3.18 dup swap 27 type
28 20 drop -0.86 -6.51 type drop drop swap - swap /
2.04 "q"
"x" "q" * + -
3.59 "q" dup "x" "ab" dup *
30 "q" "q" dup * dup + -28 -9 type type
"x" -22 - * -4.72 type
"x" -48 1.38 "x" "x" swap
7.72 "x"
-7.99 -8 "robot" * "ab" dup type
-46 21 + type "ab"
"q" 39 -3.74 swap + swap +
"robot" -17 + / * -2.86
"x" -3 -3.00 -8.18 -
"ab" "robot" 7 type * -5 3.48 -5.63
"robot" -7.44 -20 -31 47 /
"ab" "q" -6.81 45 dup 5.23 + "robot" swap *
"q"
-3 5 49 - dup - * -4 * type swap "q"
"ab" "robot" -8.32 18 drop "x" 7.57 / 6.22 3.03 -
-6.92 -43
-42
"robot" -3.97 -15 * 7 7.50
-0.58 -6.30 -9 45
-39 "robot" type "ab" "ab" type type "ab"
-18 -0.86 drop -7.84 "q" 8.82
0.72
8.54 -1.83 drop + - "robot" -3.42 "q"
-21 "robot" + / + -10 -
7.42 "robot" "ab" / * + - swap dup drop
"ab" 2 drop - 14 swap swap * * swap
"x" 0.82 * -6.95 swap + swap 6.74 swap + -14
"q" "x" -15 "x" type 7.12 * dup 17 +
-4.79 "ab" 33 type * * 4 34 "q" 8.61 - type
-5.48 -2 /
8.57 -2.92 dup dup -26 swap
-4.55 "x" -17 16
24 -30 "robot" * / / type type -2.32 -3.80 -1.36
9 -34 drop 36 2.41 drop + / drop
0.06 32 dup
-3.90 18 * 6.24 "q" type +
1.43 25 -25 "ab" * "robot" "ab" - swap
-5.96 14 "q" type 24 "x" "x" /
"q" -7.90 dup
-23 -29 3.24 type drop
3.91 -4.95
8.19 -16 7.28 -49 "ab" 42 dup "x" "ab"
4.69
-7 -3 5.89 -4.93 -
-8.83 "x" "ab" - -4.13 * dup * - type *
-5.28 8.50 + drop dup
48 -1 - drop type 40 swap swap
"q" -4.23 "x" * 13 8.74 swap drop / 18
"robot" "robot" - -14 + "robot" "q" + swap type drop type
"robot" 0.76 drop "x" type dup -
"ab" -9 "robot" 6.62 type dup drop 46
-34 "x" type
"x" 46
"x"
15 1.92 type -8.40 / 6.07 + * drop drop "q" dup
0.49 7.10 dup dup "q" 26 drop "ab" + -1.82 "x" "x"
7.82
49 -0.90 drop dup - drop
3.58 -3 type -15
-36
41
-3.84 -46 drop
"robot" -2.82 "ab" type -
"x" "x"
"ab" -27 * * dup "ab" drop swap - /
"q" -5.69
"robot" -0.60 dup - drop + "ab" -49 drop "q" 4.80
-43 "q" -7.26
8.91 -3.50 +
5.33
5.54 -38 swap "robot" * - + -4.19 -3.56
"x" -37 -42 -1.80
6.04
-7.35
"ab" -31 + - / -6
-0.94 -49 8.14 "q" dup "q" +
"robot"
-0.61 "q" -7.12 "ab" -6.80 / type 7.31 - 23 type
31 -8.55 3.77 type swap
"q" 2.83 + + /
"ab" "ab" dup -6.39 / "x" swap * -1.18 37
47 22 "robot" - 4.66 dup swap drop 34 "x"
"robot"
"x" 2.32 "robot" * + drop type + + - drop /
6.34 16 type swap swap -34 -4 * swap
3.18 "q" "robot" "q" -1.92
7.17
-8.47 -0.22 6.20
"ab" -31 / - -8.54 -50 * / * 42 / swap
-7.37 -6 swap -4 * / type dup
-7.53 "x" dup
0.39 14 swap "x" drop swap type -0.48 dup
"q" "q" "robot" -2 type swap * 26 dup -43 swap +
"robot" 2.92 drop / -
"ab" "q" "ab" type "ab" "x" dup
-3.48 -5 type
-10 -7.19 * "ab"
-0.93 -4.04 "ab" dup swap * drop 5.38 - "q"
"x" 7.36 4.91 swap type -33 type / dup * -3.16 -26
"q"
"x"
-50 "robot" "ab" / swap
12 "robot" "robot" type swap -
7.74 7 + + 8 swap
"x" -8 4.97 43
19 1 7.38 "ab"
50 -17 * dup -44 20 type -6.84
"x"
"ab" "x" + + 0.99 swap -6.36 / 45 * type +
-34 1.32 -8.43 0.66 / "q" + / swap dup dup
-7.26 14
4.76 19 / "q" / / 5.13 type drop / 0.11
2.93 "ab" dup type + -38 +
3.01 "x" / type 22 type "robot" swap
"x" -1 swap 4 + "ab"
33 -2 dup -2.81 / * 7.16 25 - 41
"x" -1.00 - - * + 28 "x" - drop +
-8.24 "robot" + + * - + swap dup /
"x" "ab" swap type
"robot" 21 * * swap type
0.75 0 + 49 -18 "ab" "ab" -8.63 8.60 30 -8 dup
-15 -7.58 / - 13
6 5.95 "x" - - -30 7.72 swap
"q" 3.65 "q" type "robot" + -3.47 / 9
-0.84 -20 -6.22 type - + "x" "x" 35 - type *
42 4.20
-2.59 "ab" drop -33 type
-20 -17 50 2 "robot" * "x" drop -4.38 type type "ab"
"robot" 1.04
-3.64 -6.04 4.75 -18 -38
-7.74 -8.55 -4.11 34 dup 2.45 dup swap
5.44 "q" "ab" -25 -10 1.81 swap drop 6.31 / +
8.29 3 type - -
18 "robot" type
6.67 "x" drop
31 32 - * "x"
"q"
"robot" 3.61 -2.68 "ab" dup 3.60 * "q"
"x" -3.28 - *
-46 2 type -6.79 / / * / dup drop
"robot" "x" dup drop type drop type "ab" 3.86 dup "x"
"robot" -0.31 24 drop - - -
1.66 1.06 -8.62 "ab" type dup 41 type "robot" * "ab" swap
7.38 -0.77 * 2.11
"x" 27 dup "x" swap *
"ab" "ab" *
8.89 2.64 -48 -3.93
-44 -13 -3.62 "q" -39 swap * "q" "q" / +
"x"
2.01 3.52 13 + swap /
4.72 "robot" drop "ab" 40 + + "robot" swap - swap
-0.87 23
24 -4.87 3.85 swap 8.69 drop
0.41
"x" -18 * type "q" dup swap dup 0
-5.05 "robot" * "robot" dup
"ab" "robot" +
50 1.78 "q"
5.34 -1.47 "q" type dup drop / "ab"
13
22 1.97 -17
48 1 / 38 "q"
-8.82 11 dup swap swap * -2.35 "robot" swap -3 type
-0.22 7.38 21 / * type swap drop /
-49 "q" swap - - -25 type 26 / type dup
39 -17 + type type swap + * drop 7.82 * 48
39 "x" 21
"ab" "robot" -
-1 -3.35 - - dup *
-23 8.08 * * "x"
-46 44 12 + / "q" * dup * 0.96 + /
5.76 1.78 dup "x" -6.91 swap
50 -3.16 -
"ab" 7.54 -35
-29 -6.04 dup
"robot" -38 -
-8.52 -4.07 "q" - 3.67 5.74 - 3.24 swap /
"ab" 7.56 "robot" swap 1.59 / 7.61 6.41 /
"x" "ab" 7.50 "q" swap
-2.35 "robot" / "x" -7.39
"q" -6.06 "robot" "x" / / 25 + 6.54 drop * "q"
3.27 16 "x" swap 33 "robot"
6.63 -42 / -36 / drop -7.29 dup 5.71 - -28
5.16
21 -6.20 23
-7.10
"ab" 2.39 -2.26
"robot" -16 + * type *
18 -5.86 * -28 drop -35 type 44 4.41
"ab"
7.18
-0.63 49 -8.22 * + -5.49 type + dup swap
-5.82 31 + - type * / +
-24 2.86 -40 * -6.76 -0.26 drop + type "x"
"ab" -5.95
"robot" -47
4.10 -40 - drop swap / 7.23
"ab" -4.98
-35 -5.43 dup drop -33 -1 "x" / swap
16 -8.36 +
"ab" 13 + "ab" - "x" "robot" -3.90 "ab" dup + *
"q"
2.52 -3.99 -14 "ab" 37 -1.15 swap -31
"ab" -1 swap "q" drop / / swap + *
-5.21 -5.25 swap 23 dup * + type
-4.34 6.25 "q" type -26 + -1.38 7.18 -
"x"
-8 -5.75 14 - - /
7 "ab" / dup -44 / / * "x"
16 3.00 drop -1.24 swap -0.59 1.70
-31 0.27 13 dup / * * type
"x" "x" type "q" dup -1.81 -0.04 "x" * "ab" swap
-8 -46 -31
"q" -2.79 2.81 + "x" type type 8.37 6.89
-49 -7.12 dup "q" -6.54 43 * drop -24 drop
0.35 "robot"
-50 -37 swap /
"q" "q" "robot" /
"ab"
6.85 -43 "ab" -8 type -0.44 type -24
-36 3.91 "ab" swap 5.08 * 2.62 -1.50 5.89 / "robot" -48
31 39 drop swap - "q" - * type
"robot" 8.48 * / type dup -28
-17 "robot" swap -
-2.68 -7.58
"robot"
-7.16 -23 + "q" drop 6 5.63 dup
"ab" 9 + "x" drop
"q" 5.64 * / type
"ab" "x"
"q" -6.81 drop
36 25 -29 "q"
20 -6.38 "x" dup -8.94
-44 "q" "ab" -1 + -5.77 swap -16 swap dup
7.03 "q"
-5.00 "robot" dup "x" 34 dup 44 type *
"q" 2.34 drop - -29 41 / 37 type 1.98 "robot" drop
"x" 7.64
"ab" 7.15 dup -2.45 swap 17 type dup
"robot" 4.94 drop "x"
"robot" 0.26 "x" / drop / * -
"q" "q" /
"x" 39 - "x" "ab" swap swap 5.67
2.52 6.99 + "x" swap
8.21 -14 *
"x" -2.55 -37 * dup 26 * / -18 / + -16
"q" 16 22 swap swap -5
"x" "robot" 32 "robot" "robot" 0 -49 21 dup +
"ab" -10 10 "q" - 42 dup * -13 -22 -8 -14
-7.81 "robot"
-24 -0.51 -8.62 -0.81 -3.43
4.85 7 dup type
-3.94 "x" -6.96 dup "ab"
4 4.65 drop "x" -4.30 "robot" * + drop -38 - swap
"q" -9 "robot" "x"
38 -1.97 20 + type "q" type
19 38 "ab" -1.01 "robot"
"robot" 40 "robot" + / swap / "x" -44 -5.00 "q" 2.39
"robot" "x"
"x" "x" -3.91 dup -7.03 dup + + - * 45
"robot" 12 -10
"q" "ab"
-7.06 45 type dup / 8.79 dup /
8.04 -18 + + dup drop
-37 -8.00 * dup 33 * type
-45 16
26 -3.67 4.45 dup *
-44 6.55 "q" * +
"ab" -36 42 -
"ab" "robot" / + 6.15 dup
"robot" "x" 17 "ab" -30 * / -4.64 + 25 -9
"robot" "q" 3.39 + "ab"
-43 "ab" -12 1.46 / "robot"
5.17 4.07 dup -3.80 * -6.58 type 44 *
"robot"
-2.20 -4.78
"q" 0.53 drop swap swap 2.70
-3.07 "robot"
"q" "x" / - -2.45 1.51 8.09 "x" 12 -25 -50 dup
"robot" "q" drop 0.70 "q" + -36
21 -6.50 * dup swap * / drop "ab" 2.17
8.25 -1.82 7.42 "x" "q" +
-1.59 4.52 dup * drop "robot" -
"x" 7.48 type 45 "robot" swap * 33 +
3.62 9 -16 "q" drop dup -5.52 type "q" +
-2.92 "x" -1 39 type 44 "robot" drop
4.06 39 "ab" swap - "robot" dup 3.29 -7.08 +
-48 -3.51 swap swap "robot" dup "robot" "ab"
"x" 4.94
18
"q" 17 "ab"
"x" 6
1.83 "ab" 5 -5.54 *
-43
-10 "robot"
48 8 dup
"q" -19 swap dup 0.17 8.34 type 3 type
-39 3.13 - -0.28 drop * -0.36 / "robot" 6.20 -42 drop
0.88 0.22 "robot" - * / 46 *
17 -0.86 -33
"robot" -4.68 -6.74 swap -44 + 6.98
1.30 9
-8.12 3 "x" 30 - type -1.89 +
"q" "robot" * -42 dup drop / "x" -22
"q" "q" "ab" + / 7.55 -1.99 - "q" -4.90 "q" drop
-19
49 25 + -8.07 "x" * "q" - -43
-4 "x" swap swap
-34 -49 - 3.27 48 * type -
-0.10 -4.15 *
-18 6
"ab"
"q" 1.05 "robot" + * drop
23 27 * dup 21 - +
-13 6.20 49 -5.00 46 type dup swap
8
3.17 2.28 8.78 / -3.24 swap dup type "x"
"ab" 5.33 type -29 + type drop
"robot" -41 + 13 -2.82 swap -8.83 - "robot" -
"robot" -23 drop + / -36 type 46 45 swap
-20 29 11 / swap "x" + dup
-39 -26 +
"q"
"q"
"x" "robot" -7 -30 "robot" drop dup + +
-8.57 -1 31 swap 28
6.30 -21 drop - "x" 48
0.11 3.97 type
"x" -1.16 dup dup * type 5.25 -6.77
"q" 18 drop -1.18 9 swap "x" /
-4.31 3.11
-1.72 8.52 swap "q" dup "ab" swap dup drop swap
0.42 11 / -8.17 drop drop "ab" dup
-26 3.51 + + "x" 1.47 dup drop / "ab" drop 8.03
"q" -8.16
-26
2.41 -2.30 "robot" 41
"x" -16
"ab" -1.51 type /
-26 -0.48 "robot"
1 8.37 0.28 drop dup - *
-29 2.28 type 2 -34 1.78 drop -4.35 3.21
-40 -0.89 - + dup -8.32 "x" -24
"robot" 0.99 -49 "q" -7.35 "q" 4.98
-15 "robot" type dup 42
38 -35 - dup 0 4.25 - /
-4.70 0.68 dup 6.82 - -7.77 drop drop drop -7.79 * drop
-5 -39 - 39 swap drop drop - "x"
2.93 "ab" swap "ab" -6.49 -24 drop dup swap dup + 19
-2.13 45 type + dup -20 - type -44 dup swap
"ab" "q" type dup dup 2.83 dup "ab" 3.73 -5 "robot"
6 "robot" 2.52 - swap type
"ab" 38 -9 dup * - 7.02
31 -40 +
-4.03
0.37 -31 / "q" -4.05 / drop
4 "q" "robot" * * drop *
5.56 "ab"
0.37 -36
19 35 -27 "x" *
2.38 "robot" * dup dup type drop 39 swap - drop -
"q"
"x"
4 4 type -1.43 drop 2.30 + "x" type type /
"robot" -1.41 "robot"
"x" 14 * swap
-6.68 -1.23 -39 / * "q" "robot" "robot" - /
-8.57 "x" dup swap - "q" "ab" * - 43 swap /
-1.01 7.33
"q" 13 -7 * -6.36 0.43
8.92 "x" 7.94 13 1.30 "robot" -6.64 * dup swap
7 -19 swap - swap
-38 5.10 "x" dup drop
"ab"
-5.00 "ab" "ab" drop
2.57 -47 / "ab" - -23 -7.89 swap drop dup
7.56 -17
-22 0 +
"robot" "ab" type + -41 0.25 / type -25 drop type
"robot" "x" dup - +
4.66 "x" swap 0.55 -
-0.98
48 "q" type -42 -38 "robot" swap - + "q" 20
3 -1 "robot" drop dup drop / 8.79 + dup -8.49 swap
"x" 25 drop +
-8.21 "ab" - 7.92 + swap 25 * * drop "ab" type
"robot" -7.31 type "x" swap *
7.75 13 * type
"q"
38 -2.16 * -8.26 35
-7 "x" "x" "x" - "q"
-10 0.93 "robot" dup dup - + / "robot" *
2.89
"q" -7.53 *
5.98 -0.16 "x" -3.71 16 - "q" - "robot" drop type
0.58 2.20
-28 19
-46 38 swap + -5.81 drop -5 "ab"
-7.94 "robot"
1.14 19 type dup /
22 -8.90 * - type drop -0.16 / drop 50 44 "q"
2.84 "x" / drop "q" - -43 "ab" -
0 18 / - "x" "x" - drop drop 41 6 -3.49
"q"
"x" 30 -0.09 swap
16
-7.80 -6.09 "robot" dup * "x"
30 -3.61 -18 * dup -3.25 + - -23 dup
5.52 "robot" 12 6.27 -41 5.97 0.49 "robot" type 2.07
"robot" 11 -32
13
"x" -29 / dup
5.48 "x"
"q"
"q" -4.38 * + 7 20 +
-20 47 29
"x" "robot"
5.85
"x" 34 25 -24 7.94 type dup drop /
"q" 4.21 dup drop / drop dup 16 "q" type -33 +
"robot" 3.11 swap 29 - -1.50 5.71 7 7.93 * swap
"robot"
19 28 / - type 8.66 "robot" / dup dup swap
"robot" 6.10 swap swap -2.77 44 48 * 30 / "q" "q"
"x" "ab" -30 0.20 -11 * "x" dup swap *
-35 "ab" - type -7.26 * 33
-36 "robot" * 48 -45 / swap "ab" / dup
3.92
4.11 29 - * swap "x" / -6 /
5.09 "x"
"robot" 49 * 6.15 - + +
"robot" "ab" + type drop 0.29 / -6.63 -6.91
4.26 -14 20 "ab" dup dup drop -8.49 -12 23
1.65 "robot" / -6.24 "robot" drop drop + type
-2.18 33 type
"robot" 6.51 "robot" drop 22 swap dup 8
"q" 46 -47 * -10 "q" 32 -36 "robot" *
-2.01 "q" swap -39 -13 5.69 19 swap type
"x" -47 / "ab" + "q" drop -
"x" "q" swap "robot" + 3.06 - -
"x" -6.64 2.15 -11 dup -45 drop dup
"ab" -45 - drop -5 "x" / * /
-32 -22 48 / 41
-5.91
"robot" 14 "robot" -1 1.62 + / dup -6.91 "robot"
5.52 -11 drop + 27 -33
"x" -3.80
"ab" -5 "robot" -30 swap -6.84 "q" 1.72 "ab" 5.36
-0.73 -4.86 + drop
-49 -41 type 18 swap
4.77 "q" "x" "x" + "ab" / dup
"q" "robot" -42 type "x" drop drop "x" -42 -6.35 swap +
"robot" "q" type -10
"ab" "ab" 7.79 *
1.77 -4 -1.93 dup / swap type dup swap
"ab" "robot" +
"ab" 2.67 + -38
"x" -20 - + -
"robot" "x" dup + drop dup
"q" "robot" * + 6.25 "robot" "q" / + type
"q" 2.32 -8.29 "ab" "robot" swap drop
-0.41 "q" type "x" 24 swap /
0.07 "q" / /
49 "robot" swap * +
"robot" "q" + + + 2.48 * 4.24 19 *
0.44 45 "ab" "ab" 4.29 "ab" +
14 "ab"
41 "q" * -4.19
3.11 35 -17 dup type + swap
"robot" "x" "ab"
-14 "robot"
-37 "robot" -14 3.91 type -1.09 drop
22 "q" "x" * dup "robot" 4.90 * 3 "robot" drop
-39 4.53
7.63 "q" "ab"
6.80 "q"
26 "robot" * swap / swap swap -2.24 -44 /
2.66 "q" drop dup -30 -6.59 dup drop
"x" "robot" + drop + / swap / / 35 - 42
-7.60 -0.62 dup drop + "x" swap "ab" dup 15
-25 7.26 "x"
50 2.51 41 * drop / + -0.13
31 "q" 37 "ab" "ab" drop drop dup +
0.71 1.60 0.74 "x" -0.57 swap 2.59
9 -3.86 -9 "robot" type swap / type
"ab" 7.89
-46 -8.65 type -46 drop - -34 * 5.24 drop 8 drop
"q" 48 "x" - 0.80
-38 4.52 -3.31 -41 "robot" dup 2.41 "robot" 34
-7.16 "x" "robot"
-45 "q" / * "ab" -0.69
"q" -5 "robot" -
4 -38 34
"x" "ab" type "x" type swap / drop /
6.26 -32 - type
"ab" 4.49 36 -22 type type "x" * 43 swap 23
-5.96 -17 -14
36 5.82 swap -36 - "q" / -3.87
-23 -2.34
28 47 16 38 dup 18 dup * / dup -
-11 "q" "x" / 1.27
-7.57 "x" -6.45 * * drop
24 "q" "x" drop drop 22 type -2.51 / "x" -0.90 swap
-2.34 "q" + -35 -3.14
-5.41 -2 - type swap dup 8.90 5 type 18 "q"
8.81 0.39 type "ab" - dup "q" type - type -
"x" "ab" + -1 -
4.56 24 drop * * - / dup type type
"ab"
"robot" -41
23 35 * / -8.35 8.94 drop
-13 "q" -30 -6.33 type
"x" -2.94 drop type swap "x" 6.32 dup "ab" 37
3.77 -47 dup + / 6.67 dup -6.57 type
-3.04 7.15 "q" type type drop "robot" dup + -
-4.30
-6 "q" drop type type *
-0.18 6.24 - drop - / swap / swap / drop
-2
-9 5.08 * swap + -5
"q" 9 *
-0.21 -23 49 16 "x" + 3.77 -8.08
3.16 6.41 "ab" swap swap -2.84 -7.67 * 14
8.09 21 "robot" / "x" -0.74 drop
"ab" 8.01 7.67 "q" / dup -15 "q" + dup 30
18 "x" dup 1.40 + - 4.87 drop drop 5.87 dup
-2.97 -3.79
29 -17 -44 / "q"
"x" -6.15 33 "robot" -3.92 -47 -40 "x" / dup -50 swap
2.49
"x"
"robot" -44 swap "ab" "ab" -11 / -6.72 5.11 -0.15 "x"
-0.13 -4.08 "q" 5.83 dup type *
"ab" -5.45 swap * dup type -23
-0.35
4.94 "ab" swap
-50 "ab" drop 2 drop type "x" 22
-11 "robot" - +
"q" -5.96 25 1.01 drop swap -6.54 type 1.39 / -42 -
-18 "q"
"q" "x" -7.70 + "q" 4 swap drop / / swap
-45 "x" type - type drop drop
"q" "x"
1.27 "robot" "x" dup dup - "robot" - drop *
"robot" -5.59 type + - drop / -7.16 -1.94 swap
-2.14 -36 37 drop +
-29 5.28 1 "ab" "x" + type type dup
"robot" 31
7.21 -27 38
45 -4.38 21 + drop "ab" drop * * "x" "ab"
-33 -29 dup + 23 "x" "ab" -6.79 type
42 7.04 - -11 - dup
"robot"
"ab" 41 + drop -1.44 swap / + swap -2
-6.84 -2 "q" + dup * + 1.31 dup - swap 33
7.54 5.59 + * drop drop / type
1.23 "robot" "robot" / dup -36 -40
-3.62 "q" type "q" 2.41 - 4 - + -50 swap type
-0.31
-1.06 7.47 drop - - type
10 -5.07 dup -4.20
"x" "q" "q"
"ab"
"robot" 8.53 swap swap dup
"robot" -0.05 + drop type
0.48 -4.98
"q" 37 swap dup -8.77 -37 -44 dup "q"
-8.41 -32 -8.02 5.05 swap dup / / swap
3 "robot" drop * -1.65 swap
50
-1.04 2.61 +
-37 8.90 1.32 -3.45 24 43 "ab" type
-3.13 "robot" swap dup
-0.87 "robot" 28 / drop drop 8.84
"q" 35 type + / type "q" - -3
"q" -20 swap * "q" 28 swap 29 type "robot"
8 -13 / + type
-36 "robot" drop type dup 0.51 + dup 42 -4.66
-3.92 "robot" / / swap 0.55 -50 -1.64 "x"
-28 46 type drop -6.08 + / -1
45 "robot"
-5.56 -47 19 drop dup 7.55 -
2.83 -1.63
4.71 -42 8 "x"
8 -34
"robot" "q" dup / "ab" 41 1.35 + /
41 -15 -2 -14 -15 swap swap * + drop
-15 -18 drop + * + + dup -5.29 type -
8.27 11 -26 dup * * swap drop
-13 "q" "x" 0.37 swap type -4.13 dup type "ab" drop -28
"ab" -46 + swap "q" 1.94 swap + 46 + / +
-2.31 49 * / 2.48
48 -50 + * - / / -7.59 -48 swap -3.33 -
"ab" 6.65 - -4.33 33 type "q" dup drop *
36 1.93 drop drop drop drop
23 23 "x" "robot" / type -0.97 4.93 dup /
"ab" 1.42 drop
"robot" -20 * drop "x"
4.36 18 swap -32 type 49 "q" / type swap dup drop
"robot" -20 drop 43 "ab"
"x" 15 type + type swap * +
-7.71 "q" - swap / * swap
-10 41 "x" dup
"x" "x" dup / / dup dup swap / /
"q" -50 swap + type / 47 * swap dup -
"x"
-2.66 0.12 * dup -3.93 *
-21 "x" "ab" "robot" type "robot" / /
"q" -5.37 "ab" -4.45 * drop 25 dup * type dup *
"x" 4.99 drop -0.81 type "x" -5.50 /
-15 17 -25 - + * swap "ab" 5.34 "ab" /
"x" 4.18 * -38 "q" "x" "robot" 9
"robot" "ab" "q" / type * "ab" - "ab" drop dup -
"x" "robot" - 5.05 "robot" "ab" dup drop "x" 7.16
39 "ab" "ab" drop "q" 6.02 swap "ab" type +
-8.59 28 7.38 swap dup dup
"q" -8.60 / -37 dup -7.94 49
7.69 "x" type swap -8.16 +
"ab" "q" /
-6 -5.58 dup
-28 -5.53 + dup
"robot" 4.51 * *
-4.49 7 "robot" "ab" type -8 swap +
"q" -6.85 / + * "x" type swap -4.36
"ab" 5.44 15 -29 drop / "ab" /
1.40 8.55 dup 3.11 *
-37 6.23 "q" 2.90 drop swap
"robot" 6.31 * 23
3.68 "ab" type -48 -3.50 "x" / 4.08 - +
-49 18 dup "q" type * swap -8 dup
"robot" -7.79 drop -0.54 "q" +
0.49 4.63 * -8 "q" -2.94 drop
-25 -1 swap -0.11 swap -8.21 "ab" 3.44 *
-6 37 - / -3.07 swap
"x" 44 type swap type "ab" *
"robot" -22 / drop drop * 5.67 dup
-2.76
-40 -2.31 - dup drop "ab" / "q"
"robot" -1.97
"robot" -5.14 / 0.41 / "ab"
"q" -5.94 / dup -2.72 swap
"ab" -4 dup / swap type 3.10 36 *
-42 -5.42 /
"x"
7.58 "ab"
27 7.55 / -30
33 39 + "ab"
"robot" 31 4.69 + - * / 28 -44 swap 3.40
7.31 48 * swap 7.38 "ab" "x" type "q" drop swap
-0.06
-2.72 -5.35 "robot" "x" "x" - - 46 drop drop
1.31 1
-39 "x" "robot"
"x" "x" drop
25 "x" swap + -1.39 + /
-10
-5 3 "robot" 10
0 0.30
4.13 5.67 * swap +
7.55 -28 * -1.12 -25 -5.70 -
"robot" "robot" drop "robot" "robot" 41
-6.74 14
18
2.24 "robot" - "ab" / / 0.20 - type type - type
14 8.73 -0.92 -
9 21 * * 38 * /
3.16 1.61 - / dup -8.35 12 swap -1.99 dup
14 "robot" / swap type type * type + "x"
8.18 "q" drop dup dup swap 47 6.38 "ab" / dup 46
-30
-7.99 -25 type swap type
"q"
45 -4.06 type / / 0.53 *
31 -5.44 * drop / /
37 "x"
-39 8.49 dup dup type "x" type *
-47 1.28 "robot" -5.51 / swap + / * / +
"x" -10 type - -2.31 * -6.85
-0.20 "robot" * 34 2.26 6
"x" 1.50 swap
4.51
21
"robot" "x" 6.12 * type
0 1.18 2 -5.08 dup "robot" - -5.49
-3.53 7.25 -1.23 swap "ab" drop type "x" / 33 13
"x" 17 * 7.26 3.07 / 16 swap
10 "ab" drop -4.31 - "ab" type type dup 3.29 drop
"ab" 50 drop dup -2.98
0.36 "robot" "q"
"ab" -31 * "robot" "x" + 31 +
-50 25 / -6.69 8.19
-41 "x" "x" 31 "x" swap
2.55 20 - -2 -1.70 / "q" -
7 -30 swap + "q" swap "robot" 2.37 * -45 dup
-5.03 -3.28 + - "robot" type "ab" - -13
"x" 14 drop 3.49 "x" /
"ab" "robot" / 5
"robot" "robot" 1.42 - "ab" 7.65
-11 "q"
43 "q"
-1 -47 dup * / -9 * / /
32 -3 dup drop dup 6 -6.21 + drop - type
"x" "x" swap + dup - + -2.80 + 20
"ab" -1.15 "ab" / 3.31 "x"
18 -3.69 + * drop 3.19 3.01 3.72 swap -2.80 dup
-32
5.61 42 drop
"x" 8.25 swap - * drop drop -1.37 -1.52 6.92 / "robot"
30
"ab"
9 13 -0.75 2.96 "ab" - /
-30
-36 -47 + / -5.44 swap - 7.74 * -
36
7.29 7.38 43 type swap - drop -39 swap /
43 "robot" dup -2.41 7.40 dup
-0.05 "x" swap type "robot" -30 -
-5.78 "ab" "robot" + "x" "x" -3.25
0.31 18
"q"
"x" 4 type -31
"q" -3.41 34 dup "ab" 11 type + type -4.01 35 +
"robot" -5.14 swap +
"ab" -1.84 * + / - -
1.21 13 type 36 / /
"robot" -2.15 type * 49
"robot" "x" "q"
-4 "x" "q" 3 swap swap dup
4.04 -11 + - - drop / -22 dup type swap
"ab"
"robot" 2.75 8.89 "ab"
-7.35 -4.60 "robot" swap
-26 20 "robot" / - "robot" -
34
-45
"ab" 3.46 37 type dup
-40 2.21 swap drop "q"
0.38 5.49 swap +
0.65 "ab" type
-26 -5.64 type type "q" -3.58 type -
-4.77 -50 "q" swap "ab" drop + / "ab" * 8.26
"ab" 4.17 -
0.49 -41 drop / -26 "robot" + -3.38 + 31 / type
"ab" -20 * 30 3.45
"ab" 47
-5.71 36 + drop / swap
"robot"
7.53 "robot" / - -3.46 "ab"
33 0.46 * - + dup type "x" / 29 swap
7.40
9 "ab" -5.70 - "x" dup drop 42 -4.78 -
"ab" "x" "ab" -1.58 "x" + "robot" swap "ab" -6.27
18 -7.74 dup 5.32 -38
"x"
23 39 dup "robot" "q" + "x" type / swap drop
"x"
-6.28 "robot" dup type * 10 swap "x" -9 "robot" / drop
-17 "robot" - / 37 swap +
-16 -18
"ab" 29 - * swap / * /
"x" -4 32 +
31 -7
"ab" 8 -8.57 dup "ab" 1.79 - * - type type
34 3 drop / type -3.01
3.73 0.35
50 -3 / -6.07 * * * *
-0.99 -6.11 swap type dup - 12 -
7.19 -4.29 1.55 swap swap * 0 -25 15 / type
20 0.65 type
-15 "x" 2.82 -
-0.57 "q" "ab" + drop -7.04 0.48 swap -4.61 swap dup
8.87 7 drop / / -4 "ab" "x" -3 dup 3.80
"robot" 45 + drop
"robot"
-21 -5.60 1 31 dup "ab" type / swap / swap -
-7.92 -7.79 - 2.00 3.43
"robot" "x"
-40 4.11 -13 - + dup - * +
-3.48 41 + + 20 drop type drop
"x" "q" drop 0.80 dup * 4.88 + drop dup
"q" 0.31 type "robot" -3.40 dup -48
-41 1.96 "robot" * -14 swap
"robot" -1.13
-50
46 "robot" dup -
"ab" "x" "robot" "robot" * * 4.78
2.95 -4.88 / -29 -7.31
"robot" "q" swap 32 23 dup dup 1.34 / + /
-10 -16 *
6.01 -7.28 * "x" type drop *
"x" -8.17 / "ab" swap + -
-17 -0.94 * drop 35 dup 7.57 "ab" /
13
-7.07 3 -3.46 + * swap drop dup swap - +
2.07 "ab" "x" / + "ab" -2.35
7.17
"q" -7.62 dup + dup 1.93 -0.27 "x" - + -34 swap
1
-31 "x" type /
-15 1.36 type 43 drop type -2.59 -8.28 36 "x" 10 -
-8
-2.09 -50 - "robot" dup drop swap
10 -1 30 "q" / / type - -45
"q" "x"
-3 -7.24 swap -7.19 * / "ab" "robot" dup 7.62
"q" 44
5.47 "robot" / + / * "ab" swap + swap 23
2.13 0.75 "robot" type type swap "x" + type 3.08
"x" "x" -4.87 swap -
-27 8.89 drop * dup - - / dup
-8.81 46 drop -1.58 +
-36 "robot" type "q" +
1.05 39 "ab"
-8.85 "ab" 31 "q" / swap
"q" 8 8.64
20 7.74 -36 "x" -1.84 dup - + "ab"
-0.01 5.20 5.64 + + / dup /
6.37 "q" swap -6.39
-2 "ab" *
8.20 "robot" dup type / * drop -48 / 10
"q" 5
-0.61 -48 drop +
"q" "q" 0.89 drop dup dup / drop *
"x" 38 type "x" / "q"
43 "ab" swap 17
5.59 "robot" -
8.13 5.49 -7 5.79 drop / -2.80
"x" "ab" "robot" 7.75 swap "ab" *
"x" -6.48 drop swap 4.12 -0.19 - dup 3.40 + dup 3.11
15 -8.09 *
27 "q" - 7.92 "q" 2.48 -1.78 * +
8.10 -16 7 -6.90 / "x" type "x" 22
-8.48 27 - "x" -7.32 * * + -1.95 -31 dup +
-44 "q" 5.41
"robot" 8.32 * dup 8.35 -7.19 -5.88 * drop
0.99 -4.00 drop 35 swap drop
-7.45 "robot" -2.88 type drop "x" + 28 -5.10
-2.17 1
-1.40 19 * "robot" 7.66 -1.56 /
"x" 38 drop -28 8.10 dup type
"q" -3 type drop / / * + "robot" 0.96 0.04
-5.12 -15 -47
2.83 31 "x" drop
-8.24 "ab" -
"x" -37 swap / -5.24 drop +
-3.90 8.96 -7.11 + + * 4.08 * -3.74 dup
-1 -19 swap
5.32 "ab" 47 -26 "q" -0.49 -6 "robot" swap +
"x"
37 "q" swap swap 6.70 "q" + -1 10 "x" "x"
"x" 4.22
"robot" "ab" swap dup * 8.23 - *
45 35 -8.23 / swap / dup "ab" + 26 drop drop
46 -36 -47 dup type * 36 / swap -
5.44 "x" -34 - 2.87 dup -3.67 * drop
-4 "ab" + * drop * swap "robot"
"q" -27 +
-6 "ab" drop / -30 "x" 6.35 type
-8.89 40 type drop swap - swap -2.91 drop 5.41 -5.74
5.65 7.70 swap swap + dup
46 -2.06 + -3.84 * 50 drop 0.70 -2.19 swap 23
-30 "x"
"x" "x" + 16 7 -5.92
"robot" 0.13 +
"x" -2.48 type * - drop + 38 dup -1.11
-1.99 -14 * -36 drop "q" 4.74 "q" + dup
"x" -2.94 swap "x" 14 + - "q" + / 6 -14
28 44 + -4.58 + + "ab"
0.80 -21 -3 4.21 type * "robot" swap
"ab" "q" -23 12 36 type * drop "q" drop drop "x"
"ab" "x"
-8.49 -29 3.59
-4.79 44 type -7.72 dup
42 20 drop
"ab"
"robot" 7.13 dup swap -12 + -13 * type
"ab" 5.67 swap "q" drop
-1.90 -3.65 +
1 -7.29 type
-32 "ab" / * / 34
0.98 -3.64 "robot"
0.06 -3.43 + - type 7.69 drop
-1.86
48 12 drop + drop swap / -23 1.43 -5.06 5 -3.20
24 "q" + * * dup / -5.33
31 "ab" 5.80 type 8.46 + -1.03 dup "robot" type
"x" -7.67 -3.83 - - "robot" - - dup
-15 "ab" drop drop "x" -29
48
"q" -14 * type / -23 drop
49 -6.66 swap "q" "x"
23 37 -5.44 -7
"ab" -7.94 /
-19 -2.11 dup 2.74 -34 + "robot" - * /
8.58 "ab" - dup dup * * "q" + "q" 3.21 type
29 50 "robot" "q" drop -3.98 5.53 21 3.16
10 "x" -5.24 type 8.47
-26 28 - swap -35 - "ab" dup
"robot" "ab" -8.49 swap type drop
-3.18 -33 + swap drop -41 "x"
3.16 -3 swap * swap + swap / "q" -1.18 "ab" drop
"ab" 12 + +
-3.87 "robot" -6 + dup
-19 "ab" -0.04 - 6.50 type type 37 28
-32 26
44
"robot" -44 -2.93 type "robot" type type "q" - * /
"ab" -5.56 5.94 /
5.60 0.52 drop drop
33 -18 "robot"
"q" "ab"
-38 6.73 - swap drop -4.23 -7.89 "robot" swap "q" "robot"
43 "x"
-38 -5.75 / "q" / "robot" dup "x"
0.99 "x" dup type drop "robot"
-0.26 28 * 4.18 + + swap
-14 49 "x" - - drop type -45 "x" type
"robot" -7.23 8.32 * dup / -6 2.90 drop "ab" type /
-3.26 "x" / -6.04 13 - 8.18 + type "robot" +
19 "ab" - type type drop -28 -
-49 43 * "q" + + drop drop
"x" "x" drop - type dup type -36 -5.99 "x" -25
"q" "robot" 31 / "q" swap - + "robot" 46 swap 1.65
-3.07 1.72 +
5.75 -1.32 15 / -6 -1.63 "robot" / + -29 * type
"x" -7.44 "ab" "q" 26 "x"
"ab" 10 -50 -0.46 type
"robot" "q"
3.18 -43 * drop drop
40 -0.33 36 * * dup - 0.10 + /
-47 -22 / -47 "q" "ab" 36 - + swap
"x" -8.74 + dup 23 "ab" type +
"q"
4.19 "robot" -0.93 dup "robot" 5.04 swap 35 drop
11 "x" -39 -19 / -33 + type
1 10 -7.33 1.85 -4.50 drop + / 4 7.41
10 -36 39
29 -38 * type - drop dup - * dup type
"q" 45 swap
"ab" 23 "q" "ab" "robot" "robot" 4
"robot" 31 / - + -
-34 "q" / 5.12 "ab" swap swap 2.68
7.23 -3.81 drop * swap / drop
"q" -16 *
0.75 0.31 "x"
"x" "q" 37 - 5.95 - "x" 34
19 -0.23 * type drop "x" drop 4.60 "q" dup
"robot" "q" swap swap dup drop * -10 -5.83 -14
"robot" -41 -35 type 5.23 *
0.23
"x"
18 -2.65 dup 0.59 -7 -8.76 "x" swap +
31
"q" -13 6.91 - 3.45 drop -12 32 type
-4.34 -1.59 dup "x" * * -21 * -4.08 drop -48 *
49 -7.85 type - "x" - * "q" swap "x" -7.76
6.08 8.04 8.40 - -7.01 /
2 -28 / drop / "x" -
9 -3
"q" 4.90
"robot" -40 type drop "ab" / 24 / type
"q" 1.71 47
35 4.96 "ab" "x"
-3 22 swap 8 "x" -0.58 +
-28 "robot" / + dup -25 -
43 -5.90 dup -50 "q" swap
22 -1.97 -0.62 * / 32
-26 -7.84 +
-21 -8.74 -4.34 dup "q"
40 -6 type 27 "robot" dup swap "robot" *
"ab" "robot" 4.91
-3.34 6.84 * * drop - drop type "robot" -7.95 drop 3.10
-3.90 "x" 5 -7.24 swap "q" "q" drop
0.13 "x" - "ab"
1.31 "x" / 48
39 "x" +
3.56 2.78 + -25 + drop swap -0.73 -3.27 / -3.07
"q" 2.22 + drop "ab" *
7.38 "robot" 34 4 "ab" / 14
-4.23 3.11 type "x" type * "x" 21 dup drop
5 "q"
"robot" 1.70 type * drop * dup -3.86 drop - "ab"
"q"
"robot" "robot" -48 * drop * + type
-3.65 7 37 swap type * 24 0.60 * drop type +
-30 1.59 -2.39 drop -5.56 drop * -
-13 "x" /
-12 "q" 7.33 -35 type -4 drop type * * type
8.37 -19 "q" 8.18 23 3 "robot" 13 21
"q" "q" 4.12
-2.69 "robot" /
45 -2 drop drop drop -36 -7.54 4.45 + dup
-41 "ab" type 3.46 * + / * /
5.58 -8.82 "ab" drop dup "ab" 7.41
7.12 "robot" "x" "robot" -1 drop drop -8.29 * -39 drop
16 "ab" "ab"
"q" 6.47 dup -6.88 + -48 drop * + / + "x"
"x"
-0.98 4 drop + "robot" drop "x" swap + * + -
-42 "q" -29 -2.32 + -17 "q" swap -37 + -48
"q" "ab" swap dup * swap swap swap dup -3 "x"
"q" "robot" type 6.16 swap /
-22 1.18 4.51 type dup dup
"x" -6.53 type drop "x" "ab" / swap -43
"q"
12 -2.77 type
"robot" 4.15 type drop * swap -5.50 +
11 "x" -3.89 "q" "q" 6.04 "x" + * "robot" + 0.37
-5.46 -25
"x" 5.40 drop -37 / - -4 "robot" swap "ab"
-3.94
-40 6.22 -8.04 8.46 -11 0.42 -4.94 "ab" -4.10 -3.19 "x"
4 -3.47 "q" drop + "x"
47 "x" type 2.96 41 swap "q" 40 8 swap type
-19 "x" -1.86 +
-38 47
-0.56 -9 - swap -6.04 type 2.46
1.62 -28 -5.09 "robot" - -1.98 "robot" swap "q" / drop
"x" 7.36 "x" 31 * "x" type type 42 "robot"
"ab" -4.62 -26 -41
-2.78 "robot" "q" drop -4.01 + 32 type *
"q" -50 / 26 "x" dup -2.58 -6.82 31 / /
-23 "q" dup "x" type 4.48 swap / 3.76
30 4.12 -26 / + type + * *
47 "ab"
"ab" -0.92 - - -24 - dup "x"
"ab" "x" swap + 0.06
24 7.11 2.54 2.13 -0.63 swap
"q" 0.83 -5.03 dup "q" drop swap - dup / dup
-24 "ab"
-0.79 -7.60 drop - - 0.44 48 - type -7.22 41
3.32 -6.93 4.50 -
36 -6.89 * dup
6.52 8 dup "x"
-6
"ab" -7.10 swap swap swap drop -
9 -7
-30 7.76 / 15 / 4.66
"robot" "robot" swap / dup -4.72 41 swap type * type 6.06
"ab" "ab" - / / dup
0.05 10 type
"x" -4 "q" / "ab" dup swap "q" type
20 "q" / drop drop 2.46 drop 30 - dup -18 -
-3.96
"robot" "robot" 19 + * swap "ab" /
20 "ab" * type type
"q" 22 + drop + + * 43
"x"
7.50 -5.37 5.94 "ab" / + / -15 -2.04 -5.08 -45 -31
29 "robot" type type drop
"q"
"x"
-4.47 2.88 type type
2.60 45 swap -8.02 + / - "ab" 2.61 - dup
"x" 0 type type -8.73 / -15 /
31 12 -3.47 * dup -18 swap swap / dup +
-44 36 - "x" swap drop "x" "robot" drop "q" - type
"x" 43 /
44 -8 -0.34 -13 type * "x" -48 *
-7.87
-10 "x" drop -1.48 + drop dup type "robot"
-34 22 + -1.37
"x" 15 -4.54 * dup swap + "q" dup "q" *
"q" -26 drop + -3.12 * + dup -26 "ab" drop
2.38 "x" 5 -46 *
"q" "robot" * type - "q" type -6.90 dup "q" type -
-37 "ab"
-8.10 10
39 "ab" "ab" * * -3 - * / type drop "x"
-42 -49 + dup 7.23 + * -38 dup -
"q" 2.21 dup dup
2.76 "q" swap type 1.90 type 48
-45
"ab"
6.95 "ab" type 8.78 50 43 swap / drop
-2 -6.76 swap
6.69 -1.99 41 7.27 "x" -3.42 + -44 - 3.74 "robot"
0.77 "q" + -5.22 6 40 "x" -33 type dup
-4 8.85 "q" - -41 "robot" swap dup - drop
-0.62 -41 1.95 - -0.31 drop
2.04 48 *
-38 6 dup + - - 47 "robot" -8.38 /
"q" 7.61 4.61 "robot" swap dup -3.54 - 24 -37
"x" "q" + "q" dup "q" - - +
"x" "q" "ab" swap type dup "x" -
2.59 -7 -22 swap / + type - "x"
-36 -2.62 -38 + type "ab" "q" / drop 1.44 swap
6.70 "robot" -50 dup type
-20 8.03 - - "x" type type - dup "ab" -39 drop
-27 6.82 * drop -26 -2.56
31 "ab"
-4.25
-28 "x" 38 * "x" * 2.50 - dup "x" 1.50
6.58 -16 type drop + dup "robot" "q" / / -46 dup
"ab" -26 swap
7 "x" 6.26 -
"ab"
16 7.86 dup -22
-6.31 7.08 -48 -1.54 / - -31 + dup * type
-41 8 + -18 swap "x" * drop dup swap -4.61
3.09 -4.32 - 0.31 31 swap "robot" dup
"q" 38 /
11
-8.58 41 drop - 48 swap drop
"ab" -10 / swap * type drop dup
3.64 7.16 -20 "x" 36 swap dup
26 32 0.61 "ab"
-8.85 -4.14 7 type -41 * "robot"
"robot"
0.57 4.41 - type 31 * type * swap type "ab" drop
8.53 "robot" + 35 type -2.57 -8 type
"q" -7.80 "x" dup * 1.45 -15 type
"q" 5.80 "ab" "robot" * -4.70 /
"x" 2.94 -1.77 0.58 swap -30 -0.23 *
2 -33 "robot" 15 37 "robot" * swap -28
"x" 0.09 -23 drop
27 -50 * * -0.96 / -2.94 swap swap +
23 0 "q" "x" "ab" 29 swap 11 -27 / dup 3.95
-5.99 22 "ab"
"x" "robot" -8.80 20 / -5 + 29 swap -35 dup
12 -22 * dup -7.84 type -23 / *
1.01 "robot" "x" "robot" /
"ab" 5.28 swap -5.66 -29 + swap
3.10 "ab"
-39 -4.40 "ab" / / -0.11 * 0 type dup
-2.11 "ab" -8.85 "ab" "robot" -9 * -5.13 -5.96
"x" -7.68 dup swap -1.21 drop * / type drop
-28 "q" 36 drop "ab"
-21 "ab" drop 1.09 drop - "ab" 23 type
38
"q" 41 -5.33 / swap dup "robot"
0.94 -1 + 35 "x" "x" / swap
"x" -2.32 + swap * dup / - "q" / 2.46 drop
"q" -6.09 -0.04 "ab" -10 swap / -20 *
46 -48 drop *
3.62 "x" "robot" / 7.36 32 * 7.12 + *
3 -2.57 + 2.62 16 - - drop
5 2 "x" 27 * + dup drop "x" +
"x" 10 swap / swap -8
"ab" -0.63 / 33
"ab" 2.06 0.95 /
"q" -3.22 "q" + -
18 "ab" / / + + - * swap
-45 -6.02 - * -2 - swap - + swap
38 6 6
-4 "x" *
"x" -43 + - * +
"q" "robot" drop "ab" + 1.64 drop -5.10 -42
33 "robot" "ab" *
12 0.90 3.82
1 "q" swap "robot" dup -18 type
37 "x" -6.66 2.63
6.19 5.31 swap
44 -5.39 / "ab" dup
48 "robot" drop
-7.46 -2.55 + swap
-33 6.49 + -28 + 5.22
46 -2.40
-4.50 "robot" -6.48 swap *
3.79 1 swap /
"robot" -8.69 / / - - "x" - -34
"q" -12 - * -30 "ab" type 7.01 + / "ab"
40 "q" "ab" * 8.24 32 swap 1.72 "ab" 8.64 "q" type
"ab" -22 2.57 8.48 + -19 drop / - 28
"ab" -44 type
6.33 6.13 - type
-49 "x" 34 swap -27 + type type *
7.69 -3.24 type
46 -2.52 -39 + "q" swap - swap type "q" / +
"robot" 8
13 -7.62
-41 "ab"
-36 -14 type + 9
"ab" 40
-46 -17 drop drop -0.12 + dup / swap
-22 -0.77 "x" "q" /
-24 -6.09 * dup drop -27 -
"robot" -3.16 "q" * type * 36
-6.62 -6.82 * -1.74 "robot"
-21 "robot" 44 type "robot"
"x" -1.51 type dup - 30 / type - dup
-2.15 6.24 -4.37 -6.82 +
-14 "q" + -17 swap swap "x" -8 + /
4.66 -4.55 + swap -27 * + -6.47
4 18 swap 37 - * / 7.36
-33 "x" type -6.85
"ab" -49 2.28 + - *
-37
1 -15 "ab" type -24 1.29 "robot" + drop dup swap
41 36 type * + 31 - + -3 "ab" 40
17
-3 6.56 "robot" drop -3.72 swap - + type drop
-5 15 * dup "robot" "q" * + type -2.87 0.61
"x" 13 drop drop -1.59 dup drop swap -4
"ab" 0.30 swap swap
-4.60
"robot" -4.52 type - dup swap swap drop / swap -47
40
-0.96 "ab" -19 swap *
1.62 -37 dup
"ab" "ab" / drop 2.77 "ab" + + "q" 21 5.02
0.04 -3.91 drop type
"x" 28
18 "robot" - -4.36 -3.81 / / *
"q"
-3.35 -14 31 "ab" 3.77 "ab" "robot" dup "ab"
16
-46 -23 swap +
-22 -37 "q" swap 0.62 * - "robot" "robot" -9
-4.89 "q" "robot"
"q" "ab"
-1.16 -3 1.41 "x" 28 7.97 * * type "robot" type
2.53 "robot" 6.87 5.46 28 5.89 - -13
2 9 + 3.10 13 "x" dup / type dup 50
-5.53 25 -7 -48 - -8.50 - + 6.60 -10
"robot" 2.49 -6.69 / - - -3.09 - swap 8
-5 "q" -5.96 "robot" * dup drop -6 - -15
7.01 4.43 18 - / dup + / -7.10
4.68 -8 type -9 - -22 -29 -2.35 dup 1.94 dup
48 "q" swap 29 type -2.82 + -1.69
"q" "q" - type / -4 21 12 type *
49 6.92 type - swap swap
0 12 11 + swap 4.38 / -39 swap
"ab" "ab" dup "q" + + "q" 8.68
-18
-0.03 42 0.68 dup + + -20 39 dup
-1.62 8.02 drop type type / type 2
"x" "q"
-5.31 13 * 1.51 5.46 -1.11 -49
"robot" -6.98 - "ab" 6.64 + dup 0 -4.83 / dup drop
45
"q" -3.19 type drop + "ab" 2.10 49 dup dup swap
-7.98 5.17 - / / type / swap / dup 2.34 -29
-25 "x" drop type 44 47 swap / / drop
6.71 7.12
0.67 -37 - *
-7.00 24 7.97 dup / -5.16 dup *
-0.78 12 -22 / swap / -
-20 -14 swap dup + "robot" 1 - dup swap "ab"
36 8.21 -4 / dup dup 7.00 * * -38
-4.86 2.50 swap
36 -40 -8.89 swap type drop drop * 5
-13 "robot" drop 33
"robot" 27 -8.10 "ab" 7.10 -20
46 0.63 * "ab" "ab" * + * +
"x"
-20 "q" * -6.29 17 6.48
32 21
26 -31 -16 -5.43 1.23 type - type - 2.59 "ab" swap
-5.87 20 -2.33 + - "ab"
-8.28 28 dup -1.52 "robot" -0.91 + -
-8.07 39 drop + dup "x"
"q" "x" -17 drop "q" -2
"q"
45 17 * + / +
"robot" -0.51 drop / / type + drop
-6 -1.93 -23
8.24 2.37 "ab" / "ab" "x" + swap
-36 "x" "ab"
"ab" -2.54 - 2.55 49 - 33 "ab" swap "q" -20 /
-20 "ab" drop
3.46 -0.76 -8.05 - swap -
1.46 "q" + type 6.30 27 / -40 drop
-39 "ab" swap - dup "x" 3.50 *
-44 -6.87 "q" dup -16 dup -1.31 + - "q"
16 "robot" / "ab" -41
-1.37 -3.49 -5.90 "q" dup
2.45
"x" -3.18 type *
2 8 + swap drop
"x" "q" dup 25 9 + dup
-30 5.82 +
48 "q" swap -30 + swap drop * drop 8.87
"q" 35 -3 -0.83 + type "q" type
-5.49 -2.22 -2.46 dup - dup
-3.20 "x" 10 "q" -6.26 7.30
"robot" 22 4.41 / /
"q"
-5.91 "q" * "q" / drop dup "x" swap 3.57 * "x"
7 1.76 - 4.84 swap * 49 drop swap dup "x" 26
"robot" "q" * dup type 7.04
0.21 0.86 dup -19 16 20 / -35 dup dup drop *
8.74 "x" "x" 19 -
47 6 - + - 8.77 drop -2.16
32 -10 "q"
9 14 "robot"
"q" "x" swap type dup dup *
"q" -4 swap * dup "ab" dup dup + 43 type
3.92 49 34 "robot" / swap "ab" "robot" dup 20 /
"robot" -4.34 -33 + -2.68 + "ab"
24 -2.51 type "q" / - -0.83 -44
"x" 6.64 swap + drop /
-26 -8.26 drop type "ab" "robot" -1 "x" 8.55 type
"x" 7.03 type / "robot" "robot"
-0.80 "ab" -27
-42 -4.16 -7.43 swap * 5.94 7.95 *
"q" "q" "x" type swap *
46 "robot" 3 6.40
-48
8.35 4.53 + swap -8.12 drop * type drop swap
-5.09 3.70 drop type swap drop -0.45 -7.64 29 swap
8.41 -36 dup 16 2.21 * -7.87 "x" * dup 8.42 30
-26
"ab" 6.04 / - drop "q" -
-39
32 "ab"
32 -3.33 "ab" "robot" type 1.36 + 43 dup
"x" -1.46 /
-15 "robot" swap -
7.79 "x" drop 5.23 + dup
"q" "x" drop + "robot" /
-8.94 6.30 / * dup - "q" / 4.91 drop -5
"robot" "x" dup 5.10 "x"
7.65 49 + dup drop "ab" -7.99 drop
"robot" "robot" dup "q" -36
23 -7.61 -3.07 type -35 dup 35 14
-26 "robot" / - drop dup /
-6.50 41 type "x" swap swap -49 4.47 swap -11
-12 6.05 dup "ab" -16 - + drop -5.48 type -5.17
1.92 5.27 / type 48 -
"x" -7 8 * type
4.67 -2 dup / 8.04 swap + "q" 5.00 type 42 15
-7.66 13 + / +
5.50 "x" swap
8 "ab" - "x" / "x" drop drop
43 -32 47 31
"ab" 4.02 -46 swap -48 - drop + + -0.13 /
"q" -8.23 swap -
"robot" -27 drop / swap swap
-8.79 2.58 swap type -20 type swap drop - -4.62 "q"
-1.08 "x" "ab" "ab" type +
-1.29 "ab" - * / "robot" type swap swap swap -4.96 /
-50 "ab" "robot" 26
-0.91 "x" -42 1.04 swap -41 swap -21 * type - swap
8.95 -32 - 7.69 + - /
1.61 "x" swap -6.55 3.43 * *
"x" 4.07 -4.65 type / /
30 -7.01 -1.74 / * 36 "ab" + type
3.31 7 type 4.33 23 drop "ab" type type
40 8.96 40 "q" / +
"x" -5.15 / type - 4.08 8.32 -38 dup
-39 -1.44 - dup * 31 -45
4.87 -4 -49 / type dup "ab"
-1.73 29 swap * -2.46 drop + 7.39 -2.66 8.30 swap
-6.81 "robot" "robot" drop -32
"q" "robot"
4.17 -23 - * + type
-14 13 "x"
-7 -5.96 drop type "x" swap 6.38 -
"robot" 45 - - -46 "x" drop - 11 -2.84
1.62
"q" "x" type swap -14 8.51 25 / dup drop * /
25
48 "x"
48 -38 * dup 5.04 14 44 7.71 "x"
45 -1.45 -44 *
5.77 -5.97 -0.26 "x" -35 "x" + / -43
-39 "x" 4.79 -21
"robot" "q" * -7.35 2.49 -
-8.14
-3.42 1.88 type swap 1.05 "robot" drop type "q" -
-1 -0.12 type type
2.34 26 -
-2.28 -4.80 -17
-3.91 "q" "x" drop dup -6 *
8.95 29 - -45 "robot" swap 4.44 /
-7.70 "robot" swap 30 / swap +
6.90 6 30 *
29 2.39 * / "robot" 40 / * / swap -
-0.87 -3 / / "x" swap swap /
4.36 "ab" 8 * dup type "ab" - *
0.90
-5.21 -17 "robot" + dup dup
"q"
23 "robot" -8.73 / drop -1.19 type type *
7.01 "ab" "x"
6.88 8.43 * / type
-5.84 -1.37 * * swap 5.33 44 - * / 3.81 /
41 "x"
3.74 -3.13 -4 -18 * type type + * 7
-19 0.33 -5.02 1.71 drop type 3.77 type type -
6 3.48 drop
3 "q" + swap
14 -2.28 * 42 * /
-5.10 -40 "q" 1.54
-8 -2.30 -8.29 -19 -0.08 "q" -
"q" -8.48 16 -39 drop - type "robot"
44 "ab" * drop - 4.54
26 "q"
7.22 -5.81 dup * type -1.35 -17 dup - * *
"q" -20 type "x" type - -28 0.57 "x" 10 + type
"robot" 18 type 11 dup *
-16 5.43 - -2.87 swap + "ab"
"q" -1.74 -2.90 "q" - / / - drop
43 0.18 "x" "robot" -31 swap - * -
-0.63 14 drop
"x" -17 type
36
"x" "q" - type type / drop dup -5.87
-32 "ab" * 29 / "q" drop type -23 "q" "robot"
"robot" 2 -31 drop swap - type + "q" -
"ab" 11 dup -19 dup dup "x"
8.51 3.24 type -14 swap / -46 *
5.74 8.04
23 "q" swap - / "ab" -4.78
1.45 -31 + swap swap
3.06 -28 drop -2 * +
"ab" -50 -32 -18 -7
-0.83
"q"
-6.80
6.94 "x" dup drop * -47 39 18
"x" "x" -44 -1.55 swap dup / type -0.92 0.63 "ab" "x"
-1 -1.90 "q" "x" - - -6.24 +
8.68 -43 drop drop *
"robot" 31 * +
8 -6.60 9 drop "q" type / 13 swap drop
6.73 "robot" drop / + / / +
-32 32 type 0.87 "robot" dup
-5.75 "x" / + -6.18 "q" 40 type
-14 -3.31 dup "q" * / 4.64 + drop
"ab" 10 3.33 "robot" 4.42 -27 -
8.79 44 drop 4 - "q" 1.43 2.15 / "x" *
-27 "q" * / 0.63
-3 -49 "ab" 35 + 0.95 drop -
5.11 "robot"
-31 -5.91
29 "robot" / - type drop 1.24 -1.68 type drop swap
"robot" -0.73 + -3.90 drop - -40 drop / type dup "ab"
8.32 "robot" / "q" - drop - 36 "ab" "q" - type
-5.19 -38 - -11 / -26 dup
-19 1.67 * "ab" -28
"ab" "q" type drop "q" - drop - 4.70 28 "x"
-6.19 -49 "ab" -3.93 drop swap swap drop swap
47 -4.14 "robot" swap swap * -
7.41 "robot" 7.75 "x" 0.59 / 2
36 17 dup
-14 31 / drop + type
"ab"
"ab"
29 4.81 2.44 -17 dup - swap type drop
"robot" 8 * / drop "ab" -39 - - "robot"
2.07 -7 type -31 swap 19
"ab" 3 30 10 -3.20 * 6.03 swap 3.44 dup 35 -37
26 "robot" drop + swap 6.05 type "robot" drop
-31 -1.96 8.72 "ab" "robot" dup + drop 3.56 30 -6
"robot" "robot" -8.01 / drop / * 38 7.48 /
-2.63 -19
"ab" "x" drop dup dup swap 43 2.52 1 * 0.67
"robot" 37 -6.96 swap / dup
"ab" 3 "robot" dup
-4.59 -19
37 "ab" "ab" "ab"
-33 "q" / dup -4 0.91 type dup *
"ab"
"q" -24 * * * 8.73 type
1.41 "q" 42 swap 8 - drop +
"q" 43 * type * * / "q" dup swap drop
6.13 39 32 -8.39 3.95 drop
44 3.27 / 39 dup "ab" 8.74 -5.15 /
6.06 "robot" "x" -14 swap 3.87 swap
-0.61 -0.97 "x"
"x" "ab" swap drop swap -4.42 * "ab" 8.43 type 46 type
"robot" -29 "robot" / swap * drop type drop 7 40 dup
-7.12 -3.55 -30 "ab" "x" dup -0.38 -2.38 - * * /
-5.47 -5.29
7.16 "q" + drop 7.83 -7 30 type -2.50 "x" +
"robot"
40 "robot" -8.14 / 37
14 "x" dup
"x"
-5.35 2.62 type / 35 + -3.40 * "x"
-1.00 41 / 8.54 * drop type *
-5 40 swap "q" "q"
0.59 "q" + "x" - "ab" * 3.46
"ab" "robot" 0.30 8.64 swap 2.28 "robot" "robot" -2.33 37
25 48 "q" - / swap + *
"robot" -6 * - dup -32 swap drop 7.77 - "q"
-35
5.54 "ab" dup dup swap -6.31 +
"robot" "robot" "ab" drop drop 22 3 "robot" 42 + drop
-32 3.80
"x" -18 type / 6.50 -23 + 22
-8.94 "robot" * / "q" "x"
-33 -47 "robot" + / + + dup 2.89 38
"robot" -12 + 49 * + "x" -42 dup
"robot" 41 dup / + +
8.37
0.06
"q" -2.40 + dup -1.37 / -15
-1.77 -2 dup drop "ab" + type * dup type "x" "q"
"x" -6.87 + 44 -5.10 35 dup /
"robot" -2.05 swap swap -38 - "ab" * -1.96 drop - drop
-5.25 -46 "robot" -36 type + -25 drop drop swap
-3.49 -8.10 -4.75
8.51 "robot" swap swap / 3.57
0.93 43 5.11 - 29 swap * + 43
"robot" 46 dup - / /
"q" "ab" swap - 3.54 7.23 -17 type type
8 37 - -3 24 "ab" dup -4.40 * swap
"ab"
-16 -20 -50 -3.87 4.66 "robot"
38
"x" 20
"q" "x" drop "ab" dup drop "robot"
-8.82 19 - * + / "q" "ab" dup + -0.58 -
-11 2.15 / type
7.43 38 "x" * 8.05
"robot" "x" -32 type + dup -4.19 / * "q" / 5.25
8.88 34 8.38 dup 6.34
3.79 "ab" drop - 15 dup * 7.30 6 "ab" swap -8
-5.88 -0.40 drop - 37 / dup "q" *
12 -8.88 * *
"robot" "q" type "x" dup
47 33 "ab" dup 1 40 /
7.99 2.04 * -2 50
"robot" 5.26 - swap * dup 4.30 - 39 * 0.88
25 46 + dup drop "robot" + dup + 42
5.05 "x" -7.40 + dup
-36 21 + drop - dup dup
-0.39 3.23 /
8.65 11 "robot" * 1.85 + dup -43
1.14 "q" -26
-50 "q" swap
"x"
7.29 -19 swap drop -28 + * +
5.42 5.09 -0.52 * type + "robot" swap -29 "x" -22 +
-34 "q" drop "robot" - 33 -38 swap -6.40 -13
"x" "x" "ab" type "ab" -24 -8 -6 4.33 type type
"ab" -15 * / - -9 8.20 dup 6.33
-40 "q"
47
"robot" "x" "x" / dup 6.77 -21 -12 2.11
"ab" "q" "robot" -5.34 35 dup 13 type - / * 17
7.36 -17 "q"
30 -3.44 "q" /
-10 -12 + 41 3 +
"ab" -31 * type 44 - type * drop drop -13 swap
-2
-4.55 9 1.69 + * * -4.56 swap swap
-40 "robot" - "ab" type swap "q"
"ab" -12 "q" "robot" "ab" + type "q" "x" 0.99 / +
"x"
"ab" "x" dup * 1.61 + "q" -9
8.90 "x" "x" type "robot" dup -33 -48 "robot" dup
-17 -22 -21 14
43 -17 dup dup -4.35 -37 20
8.73 "x" dup * * -8.76 6.61 drop -19 "robot"
-7 "ab" "q" type -34 * + 6.64
-8.19 17 dup type -6.66
-40 "q" swap "x" swap 45 "q" * -16 "ab" -4 dup
"q" -1.81 - + swap "q" type dup -3.96
42 47 -0.09
-33 -7.67
-22
-2.35 50 "q"
3.78 -6.67 / type - dup type 6.17 / / dup
"x" 7.52 swap * dup
-7.11 -8 * -4.52 type * drop type * 0.34
-40 "q" - dup dup
"x" -4.02 / drop -1.17 - "x" 3.68 /
-4.47 -39 -20 "ab"
"q" -8.19 -38 dup / -36 swap "robot" -7.85 "q" +
"ab" "robot" dup - swap dup
-8.87 "q" "x" dup type / 3.46 swap
39 8.80
"robot" "ab" + "robot" * -24
"q" 6 31 drop / drop swap
"q" -4.04 swap "q" dup * * / dup - dup -8
49 41 * "ab" dup 11
-7.18 "q" 8 dup * * "x" 27 29 + type
-8.55 -3.38 "q" 5.74 dup -47 "q" * +
31 3.47 3 + type -4.94 swap drop -4.79
"robot" "ab" / swap + + "ab" drop swap +
"q" -6.34
-26 -39 7 "x" * / - /
"q" "robot" 48 - 5
-37 "ab" drop "x" "robot"
47 2.28 drop + * -35 * "ab" swap -2.68 * +
-1.81 6.56 -8.39 - dup drop 6.24 dup
-18 6.38 swap -8 swap drop - 6.56
-1.46 "ab" type "ab" * +
-32 26 29 * "robot" type drop -8.56 swap +
6.51 -20 type type drop swap 8.80 -
-0.12
-3.12 2.66 * dup -20 swap 5.03 dup / -45
"ab" "x" dup
-4.26 "robot" + -1.15 dup "q" dup dup dup drop
"robot" "ab" "x" / 8.01
2.44
1.06 -48 + 6.24 + type swap + swap -0.96 5.00
-14 -1.16
"x" 4.67 "x" 5.80 type type / swap /
"ab" -0.94 / - 17 type * + * "q" "robot"
-7 8.58 * + swap 28
6.42 "x"
"x" -5.54 + / / dup / "x" - dup / 41
-6.55 "ab" -0.67 type type type + "q"
-1.39 -47 -36 swap -
"robot" "q" -49 - type -25 swap * -46 * swap
"q" 41 4.62 - drop -4
4 "x" drop -2.32 - * type dup
"robot" 39 "q" swap / -3.99 drop "q"
5 -14 +
"ab" 42 type * + - / -42 -6.64
-2.56 6 + type 36 "q" swap
40
"robot" -16 1.88 8.18 -7.95 / -19 swap -46 drop
-27 -4.91 -5.42 "robot" / "x" "ab"
-4.93 "x" -29 -32 dup + 19 - - type
"q" -39 * + drop -4.53
-1.43 -5.28 + "x" dup 8 dup dup -1.92 -3.61
-49 -39 * / -3 6.82 dup
"x" 13
19 -14 dup 8.54 "q" -
-16
"q" 5.38 *
"robot" 4.71 - "q" 2.54 -1.29 8.59
-0.82 -5.81 / 10
-6 "q" dup type -
6 "ab" "x" dup *
-36 "x" + "x" / drop -0.85 / -4.15 + 37 -38
-6.43 -50 - * "ab" -8 -41 + * 1.89 -
"x" -19 - / * dup "ab" /
"ab" "x" -4.08 / / + + 14 type /
"q" 26 * / + + swap "robot"
-14 "robot" - drop + + *
"ab" "ab"
"ab" "x" 41
"x"
-2.16 -4.02 + 5 36 -15 dup "x" swap 25 + drop
-28 4.63 8.28 -0.57 "ab" / + -3.31
3.81 -0.93 4.92 -0.27
-9 -15 37 -49 + swap / type -8.17 type 1.63
"x" 0.64 "robot" dup - / *
-3 "robot" drop -4.95 4 "x" "q" +
5.85 -8.51 dup "x" -3.50 -3.51 +
"q"
7.24 "x" "q" drop "x" 0.01 "q" swap
"robot" -49 drop +
"robot" -4.96 swap drop dup dup 3.48 dup "q" "ab"
"x"
"robot" "ab" 8 -38 + type "x"
6.07 "ab" + "q" dup + dup * "x"
-1.84 "x"
-6.61 18 - -6.03 28 19 / -
-31 2.00 type "x" swap dup / type type
"q" "q" 3 * - swap 5.80 drop "q"
"x" "x" swap dup 16 + drop 3.78 34 +
-49 -5.83 "ab" * swap
"ab" -37 type swap "x" "x"
"x" -39 "ab" dup / * drop * 42 /
"q" "ab" / -41 "q" - 7.55 "ab" / - "ab" swap
-5 -21 drop -5.68 type / 7.80 drop -31
5 -8 * - drop drop 49 / / * dup type
"robot" -3.91 -16 - drop / dup - 24 drop *
2.21 0.74 "robot" -5.41
-5.36 -9 "q" - -48 / drop + swap dup drop
"q" -49 / drop swap dup "robot" 5.44 + 1.54 +
"ab" "ab" type * "q" 49 / "x"
"ab" "robot" type
-3 "robot" "robot" swap + "ab" drop 4.65 / - 38
29 "x" "q" swap swap * 6.76
0.49 "ab" swap dup drop -0.84 +
"x" -0.64 -8.73 15 -4.81 1 * -4
"q" 1 + drop +
"robot"
-8.36
8.38 "q" * / type 3.85 -2.28
"x" -26 8.56 "ab" - 1 dup * / type
3.49 "x" + -39 "x" 4.10 / "ab" +
2.00 12 - dup
8.28 -8.70 type *
"x" "robot" type -7 * dup
6.93 "x" type type "robot" "q" / drop drop "robot" - +
-7.53 -27
2.30 -28
-19 -2.26 dup 8.42 7.47 type 50 swap "ab" + swap -1.93
"ab" "q"
"x" "q" type * -30 "q" dup type
"x" "x"
-34 -0.45 "robot" / -25 "q" swap + / swap "q"
-14 -18 "q" -1 type -2.44 / 24
"ab" -15 "x" type -3.75 swap "x" dup 19 swap
"q" -44 * -3.95 +
-30 -3.19 -48 8.12 +
"ab" "q"
-23 "q" - 14 + 2.18 * * -38
-25 "robot" drop + type dup "robot" -6.71
20 -17 type / "ab" - dup -5.76 - dup 8.14 swap
6.16 29 * -13 +
12
32 -1.06 type - - "x" "x" drop 47
"q" -1.51 "ab"
"q" 1.04 - type "ab" type swap / "ab" -37 4.99 41
"ab" -6.52
"q"
"q" 24 * type dup 15
"ab" 7.91 -1.74 drop 39 * swap
0.22 "x" drop drop -50 swap type / type
6.25 "ab" dup -18
"q" 5.23 / "robot" 45 *
40 1.87 -8.66 swap 4.47 - drop swap "ab"
"x" -17 swap 3.82 "q" * / 1.97 drop
44 0.57 / "robot"
8.00 -1.61 / *
-2.81 "ab" drop + - 41 drop "x"
"q" "ab" type
8.08 -5.51 / -32
19 -20 * 2.60 / - type swap drop swap type
"q" 0 drop drop / *
-2.58 "ab" drop "robot" -12 drop -2 - drop 6.86
-38 6.24 "ab" drop + + 6.09 -2.07 "ab" - - swap
-0.66 39 -7.91 -
"x" -5.99 -11 -2.92 type type -18 type -
4.68 -1.56 dup /
-17 "robot" type + type -6.99 / /
-19 4 swap type / swap / 3.39 33 swap 5.13 dup
-1.56
"robot"
5.87 "robot" -28 dup type dup
19 "q" 14 -1.28 7.15 +
2.39 "robot" -2.34 type -1.13 drop -14 swap swap "ab"
"ab" -7 - * / -15
"q" "q" + - type "q" drop swap -0.81 / "robot" swap
37 16 type -1 "q"
"x" -24 -6 drop swap dup -5.67 "x" * -0.03
-8.04 "ab" *
-37 46 dup * - + "x" /
"robot" 0.82 swap -21 7.27 5.19 type "ab" *
"x"
-4.60 7.29 dup dup + 3.18 drop dup / "x" type "robot"
"robot" "ab" drop dup
7.71 -4.84
18
9 -25 -24 -18
25 -11 dup type drop - / "ab" -8.47 "q" 2.93
-2.76
"robot" -31 "x" * 14 20 dup -
-8.44 6.51 "ab"
18 8 -3.57 *
-0.46 "robot"
-17 "x" * - + 34 2.86 -2.24 type drop
-14 -22
34 1.57 type / 8.32 / dup 6.82 type / -0.86 drop
1.45 "x" "x" dup 40 swap
"x" "x" -3.29
"x" -42
"x" -32 / 2.58 27 -2.39 type -25 swap * dup swap
36 22 -26 - swap type "q" "q"
3.84 3.86 type -4.24 / drop 4.55 *
12 8.14 type swap -20 type - -29
7.50 38
-25 "x" * -28 * -8
8.92
-35 -4.69 -7.21 / "ab" dup "ab" - dup dup drop
-28 -34 dup / swap *
0 -31 - swap * type / "q" swap
0.29 2.04 * - - / type / / dup -35
"ab" 19 dup - swap dup + 5.20 -3.06 - dup 7.91
4.58 -41 "x" drop type / 50
-3
-8.11 -1.95 -29 dup "q" - - 43 - * * 25
"robot" "q" "x" "ab" swap 46 "robot" 5.40 / swap - /
"ab" "x" 5.74 / -22 -49 13 * / + -
"x" -7 -31 / 19
-1.65 "ab" 6.53
"robot" -49 * drop +
1 "robot"
38 41 -24 32 / 5.55
-5.94 -33 - -41 / + swap - - -6.02 8.55 *
7.22 "robot" swap -41 dup - 1
43 "robot" - type drop / "ab" "x" 25 +
-7.24 "robot" / -38 "x" 17 swap swap "x" drop "x"
-42 "x" -2 dup * + type dup
6 8.50
-29 "ab" "robot" type swap
-1 "ab" dup -12 swap "q" * "robot"
-8.13 -3 7.14 1.49 *
1.29 "x" type swap dup * "x"
42 -5.91 dup dup dup "ab" dup + -
"ab" 1.37 5.92 - drop *
-14 3.38 12
-19 -3.82 -
"x"
"q" 6.20 * + *
6.14
-48 -2.68 / "robot" * -6 + + 24 swap 7.59 -49
-5.56
"ab" "x" /
8.53 -9 - "robot" - / dup
9 "x" "ab" drop swap drop drop type *
"x" "q" + dup "x" "robot" -48 -14 50 -8.27 "ab" type
-41 -6.88 + "robot" 0.14 -6.54 2.38 14 - -1.27 drop +
"x" "x" 8.18
-26 -7.21 "robot" drop dup "ab" * "robot" +
"robot" 3.64 swap + drop type / * / dup -30 /
"robot"
7.30 2 * "q" dup drop
-5.40 -31 "robot"
-6 0.40 dup
"ab" 42 type 8.06
"q" -49 + - type drop 36 / 8.99
"ab" "x" "ab" swap 4.48 + dup +
"x" 4.15 0.92
-43 -0.70 - * "robot" -7.91 "ab" dup * *
13 -8.66 + -2.62 type 37 + * / -
6.11 "ab" "q" "robot" / -
-25 -0.12 32 type
2.25
6.14 "x" dup * 0.58 "ab" 43 /
20 -34 +
48 -11 - * / "robot" drop 6.02 -20 type dup
2.19
"q" 23 type dup 4.10 type -43 -36 0.95 - "x"
20
6.93 -8.50 type dup "robot" dup type
"q" -46 dup -21
"robot" -2.28 type + -
-12 8.44 drop 3.56
34 -34 * "q" + dup dup 13 "robot" / + -50
-40 "ab" * dup + dup 34 drop dup
"q" -0.58 + drop "ab" * type 4.44 0.34 swap /
-19 "x" drop dup swap -1.99 drop "robot"
-39 "q" swap -6.53 -
"robot" "x" drop dup
-48
8.31 32 21 -1.13 swap 26 * + -39 drop type
"q" "ab" swap -17 -6.34
-7.35 33 "robot" / + dup
-41 -41 type 38 * 2.18 dup -23
25 -0.07 -2.05 -8.73 / 42 * type
25 6.02 26 -27 -24 type * 5 / / type
-0.38 "q" type "ab" -10 - * 3.54 type / - -
4.79 "q" "x" drop
19 "x" 8 * - dup
15 "robot" drop 6.27 swap * 31 drop swap 7.49 +
"robot" -6.99 "ab"
-49 -0.13 drop 5.99
7.55 8.30 "ab" "ab"
0.39 8.20 *
"ab" "q" + dup 0.74 type drop 17 / 5.79 swap
-23 "x" + type + - + -20 5
-12 "q" "ab" drop dup
4.77 "x" + swap * 2.99 -21 -2
-6 -9 swap swap - / / dup + drop 6 44
3.46
3.63 1.07 + "ab" -8.83
"q" "x"
"x" 6 swap
"q" 0 1.20 -27 dup + type -27 "robot" swap
4.56
1.84 "robot" dup "robot" + drop 41 + "robot" -38
-8.20 -32 "robot" -4 "q"
0.81 "robot" type -7.04 - 12
42 -22 -8.11 "ab" "q" * - *
"q" 0.37 3.51 + 19 -2.86 - / "x" - -1.65
-24 10 drop * 8.77 dup / / - / dup +
4 8.02 -8.53 39 type / dup / + + "q" "q"
4 -4 dup + / / dup - * "ab"
30 "robot" - + 28 *
-23 "ab" -8.36 + dup / "ab" dup type drop
4.68 "x" *
"ab" "q" swap 0.80 - type * /
"q" 4.30 drop "q" 26 - drop * -0.59 drop
-5.44 -4.70 -5 dup drop
"ab" -48 "ab" -5.19 8.06 + + * 2.86 -26 "x" drop
-16
"x" -7.70 + + dup
14 -6.38 -0.12 -17 - drop "ab" -
50 47 7.63 * -2.27 "q" + dup dup * 11
-4 34 -22
-31 44 drop type * "ab" type 6.15
"robot" -7.03 type - 4.03 + "q" 27 drop
-16 "ab" -31 - type * +
"q" -6.65 swap - "x"
-35 -2.90
-49 "q" "robot" type -9
3 -1.13 * type
8.41 "robot"
-2 -7 - 6.50 5.01
30 -48 "ab" "ab" -5.40 -13 dup type swap
-19 -8.80 -6.75 / -4.36 swap 4.59 + /
-35 "ab" - swap -12 * drop -17 - * "robot"
-28 "x" - 43 "ab" type 27 drop -49
-37 0 * + "x"
-1.77 "ab" type /
-13 -41 36 14 dup swap "robot" -
41 "robot" 4.04 -7.54 2.76 26 + type
"robot" -0.03 + dup 7.23 "x" dup dup dup
"ab" "q" "x" drop + -33 type * type -
"x" 7.54 type "q"
3 44 "robot" drop -39 dup drop 6.44 +
27 33
-11 "q" * drop "x" / -50
-6.71 "robot" 7.44 dup
-6.17
"ab" -3 8.13 + dup
7.68 27 dup dup -6.59 -2
-3 0.02 - 0.65 / dup dup -
-50 1.74
"ab" 6.04 drop 30 dup - 7.76 *
"q" 1 - * + * swap
-45 -2.15 * -
-6.25 19 -8.32 swap "x" type dup 8
43 5.70 drop -32 drop -3 drop 2.35 "x" * / 43
-1.86 35 dup
7 -8.25 type + - 4 * *
4.88 -44 dup
"ab" 48 38 dup + dup 8 + "ab" -7 type "ab"
-43 "x" + -14 dup
-39 -8.14 "q" -2.68 + -
24 -18 4.59 / / "ab" dup -43 * 32
-10 -0.76
-15 "robot" "robot"
30
"q" "x" + + - * "ab" "x" "q" drop
"ab" 13 type
25 -37 "x" drop drop + * dup * 13 type *
"ab" "x" "x" swap
"x" -7.65 - type -
"ab" "ab" -4 6.14 drop swap "x" * "robot"
49 5.86 drop * - 4.76
-6.00 "robot" dup * -7.75 -45
-2.71 "x" swap "ab" -6.79 dup -
"ab" 6 "q" swap "x" "robot" * * 4.40
31 3.36 17 5.65 dup swap -37 -
-5.26 "robot" "q"
3.55 8.99 swap "q" swap + + swap
"q" 13
6.59
"robot" -1.22 + -4 drop type
0.75 47 1 4.94 "q" / dup
-3.75 38 -2.87 type / dup "ab"
"x" "q" + swap -
"q" -28 + "x" dup "q"
"robot" -4.19 0.12 * type * - swap + drop /
"x" 44 "robot" / -33 * dup -
"q" "x" 5.03 3.28 -
10 "ab" dup dup dup type 5.83 drop dup 29 +
6.39
"ab" 48 * drop swap -4.53 swap
47 -1 +
21 6.51 18 + +
"q" "robot" 46 dup -3.63 *
"x" -1.78 type 35 - 2.41 drop * 8.16 drop *
26 18 +
-3.60 "x" + + drop drop -1.29 type 7.05 drop
"x" -5.04 * dup drop
3.19 1.60 type type / * dup + + 6.26 swap 13
"robot" "q" dup 5.50 8.61 * / + + 4.03 + dup
"q" -42 - 2.01 "ab" * "q" + swap
-2.47 "robot" "x" - + dup + -35
-30 -36
-49 0 -3.30 dup dup type + 38 * dup
-1 "x" type / "q" swap swap 0.15 -3.92 drop "robot" swap
-6.77 "q" -
-6.74 8.86 "ab"
-20 -7.25 dup swap 5.50 + - "robot" dup
-3.18 "robot" "ab"
1.97 "q" - dup / * / type drop
"q" "q"
8 "q" + -11 -7.98 * dup + "ab" drop "q" dup
-28 4.40 + * * *
"q"
"robot" -36 "q" -3.55 -37 4.99 swap "robot" swap type "ab"
16 "ab" drop - "q" type + "q"
-0.16 8.35
46 5.24 -3.87 - * - type "robot"
"q" -2.34 dup + + "q" drop "robot" "robot"
"ab" -30
3.65 7.91 43 dup "robot" "x" + * 50 "robot"
"x" "q"
-49 4.16 * -39 -1.57 0
-0.36 -7.82 * + - - 41 * type
-39 3.11 / type "x" drop / swap - +
"x" 0.38
"x" -34 swap "q" +
8 -28 drop - swap * * * -5.90
"robot" 5.00 7.66 * - "ab" type 3.99 -38 -8.91 dup
-14 20
-3.70 15 swap 24 -39 + swap type swap drop -
-49 5 / dup drop -5.28 47 / type -3.05 type "robot"
"ab" -2.81 * type + type dup / -41 + -13
"q" 0.05
7.11 -5 type
"ab" "q" / /
"q" 5 -33 swap "q" + type
11 5.65 "robot" drop 49 * "q" drop - * type /
36 -2.82 -26 "robot"
"robot" -4.10
-0.52 32 swap 7.29 -2.18 swap 28 8 2.16
-26 -36 + dup "robot" / -3.58 -6.14 "q" -3.30 type "ab"
"ab" 1 "x"
34 -22 * type * -5 / 9 + swap type
1.22 -11 6.24 type -7.77 drop -4.15 "robot"
-4.46
"q" "x" 17 type dup / "ab" "q" / "robot"
"robot" 9 * drop
-36 "x" - type 3 drop 7.04 "x" dup 38
"x" -18 4.41
-37 "q"
"x" 23 "robot" + -37 swap "q" 2.70
-3
"q" -40
"robot" 5.54 drop * 44 type 38 0 45 29
-5 "x" / swap
"robot" "robot" 3.63 -0.13 - dup -8.16 swap dup * -19 -4.07
23 "q" + drop
-0.36 -8
0.69 "q" -0.50 -6.13 drop - /
"x" 45 "ab" "ab" -43
-8
16 "q" -14 + drop / type * * "robot" type "x"
-1 5 "x" dup
1.84 "q" type * type
33
-21 8.74
"ab" "ab" /
"robot" "ab" 13 type / * type dup *
"ab" -14 -13 11 / drop -5.40 "robot" 2.32 -45 type
-5.43 -7.14 "ab" 0.74 type - / dup /
-44 20 6.85 "ab" type "x" swap -1.26 swap 26
"ab" -5.22 "q" -1.33 swap dup 4.80 8 "x" "x"
-33 "robot" drop swap -7.05 drop - drop drop type
"q" "x" -8.48 swap swap "q" "ab"
-3 -8 4.68 / type 0 31 drop -7.48 type 34
-6 -1.98 dup / "x" 27
"x" -16 - + 25 drop / swap 0.02 dup swap
"q" 5.40 - dup / "ab" 39 dup
-2.97 4.28 drop dup drop drop drop -13 6 swap "x" +
7.76 "ab" "robot"
-7.15 0.73 "q" - type 38
-8.05 -7.33
22 "q" swap dup * * type dup type "q" 1.06
-43 -10 "x" type "robot" - dup 8.14 +
49 32 "ab" dup 37 dup -32 drop 17 34
"robot" -3.28 - drop
"ab" "q" "robot" dup -7
0.03 8.87 - swap "x" + 3.96
-38 0.68 47 dup / - * + -3.91 "x" "ab" -8.01
"robot" -13 -4.88 drop swap 2.93 / swap - 32 "robot" 1
19 -22 - / "robot" dup swap "x" - +
-3.41
-6.06 -6.65
40 3.99 -0.61
"q" "robot" 0.37 * -50 type -22 + drop
"ab" -20 + 41 -2.78 - / / + 17 44
-8.93 "x"
12 33 3 0 *
"robot" 50 -13 swap type "ab" type + "robot" 3.55
"ab" "q" "ab" - swap - dup + + + 0.18
"ab" 4.56 swap 5.07 + -
-0.55 -8 2.30 swap "robot"
"x" 1 type - drop 3.63 "ab" dup "x" "q" 25
-27 "robot" dup dup -33 dup swap / swap -1.34 -47
-45 -10 dup swap "ab" dup
7.01 16 "ab" type * "ab"
4 3.46 type / -10 * 34 "x" - type *
8 3.53 drop * 5.23 - - 13
"robot" 8.69 -31
-8.19 "x" swap type -1.97 -
-42 "robot" 5.36 type -43 swap / 1.96 "q" -15 swap dup
3.01 -16 *
-1.83 "ab" / / * type -1.65 *
6.31 -3.33 -2.74 type +
-4.84 47 -12 "ab" -6 -48 type type 7 -20
7.16 1.20 dup * type drop + -2.43 34 -2 drop
18 "q" 29 drop "ab" dup type 6.87 "robot"
"q" 7
"robot" 8.52
"x" 6.82 dup / 36 -7 -
4.02
-0.01 "x" swap + "robot" -44 drop
-28 41 21 + type * * -8.88 -50 "x" "robot"
1.84
49 -4.28
"ab" 31 -22 "robot" 7.82 -47 + dup 6.05
-13 8.40 -41 dup -1.46 dup
4.90 2
-7.36 39 "q" / "q" + -27 / 12 drop swap type
-48 -18
"ab" "robot" * +
"x" 35 "x" "x" swap 7 "robot" 29 -

## Hints
- Write small helpers: `Value make_int(long long)`, `make_float`, `make_str(const char *src, size_t len)` (allocates), `value_free(Value *)` (frees only STRs), and `print_value`.
- Treat the stack as a growable array of `Value`. Popping transfers ownership of a STR's buffer to you, so free it once you've used it.
- For arithmetic, `switch` on the *pair* of types. A neat trick is to compute `a.type * 3 + b.type`, or to promote: if either operand is FLOAT, convert both to double.
- On error, free every remaining STR on the stack before moving to the next line.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum { T_INT, T_FLOAT, T_STR } Type;
typedef struct {
    Type type;
    union { long long i; double f; char *s; } as;
} Value;

enum { OK, E_UNDER, E_TYPE, E_DIV0, E_TOKEN };
static const char *errname[] = {"", "underflow", "type", "div0", "token"};

static Value make_int(long long i) { Value v = {T_INT, {.i = i}}; return v; }
static Value make_float(double f) { Value v = {T_FLOAT, {.f = f}}; return v; }
static Value make_str(const char *src, size_t len) {
    Value v = {T_STR, {.s = malloc(len + 1)}};
    if (!v.as.s) { perror("malloc"); exit(1); }
    memcpy(v.as.s, src, len);
    v.as.s[len] = '\0';
    return v;
}
static void value_free(Value *v) { if (v->type == T_STR) { free(v->as.s); v->as.s = NULL; } }
static double as_double(Value v) { return v.type == T_INT ? (double)v.as.i : v.as.f; }

typedef struct { Value *data; size_t len, cap; } Stack;
static void push(Stack *s, Value v) {
    if (s->len == s->cap) {
        s->cap = s->cap ? s->cap * 2 : 16;
        Value *t = realloc(s->data, s->cap * sizeof *t);
        if (!t) { perror("realloc"); exit(1); }
        s->data = t;
    }
    s->data[s->len++] = v;
}
static void clear(Stack *s) { while (s->len) value_free(&s->data[--s->len]); }

static int arith(char op, Value a, Value b, Value *out) {
    if (a.type == T_STR || b.type == T_STR) {
        if (op == '+' && a.type == T_STR && b.type == T_STR) {
            size_t la = strlen(a.as.s), lb = strlen(b.as.s);
            Value r = make_str(a.as.s, la);
            char *t = realloc(r.as.s, la + lb + 1);
            if (!t) { perror("realloc"); exit(1); }
            memcpy(t + la, b.as.s, lb + 1);
            r.as.s = t;
            *out = r;
            return OK;
        }
        if (op == '*' && a.type == T_STR && b.type == T_INT) {
            if (b.as.i < 0) return E_TYPE;
            size_t la = strlen(a.as.s), n = (size_t)b.as.i;
            Value r = {T_STR, {.s = malloc(la * n + 1)}};
            if (!r.as.s) { perror("malloc"); exit(1); }
            for (size_t k = 0; k < n; k++) memcpy(r.as.s + k * la, a.as.s, la);
            r.as.s[la * n] = '\0';
            *out = r;
            return OK;
        }
        return E_TYPE;
    }
    if (a.type == T_INT && b.type == T_INT) {
        long long x = a.as.i, y = b.as.i;
        switch (op) {
            case '+': *out = make_int(x + y); return OK;
            case '-': *out = make_int(x - y); return OK;
            case '*': *out = make_int(x * y); return OK;
            default:
                if (y == 0) return E_DIV0;
                *out = make_int(x / y);
                return OK;
        }
    }
    double x = as_double(a), y = as_double(b);
    switch (op) {
        case '+': *out = make_float(x + y); return OK;
        case '-': *out = make_float(x - y); return OK;
        case '*': *out = make_float(x * y); return OK;
        default:
            if (y == 0.0) return E_DIV0;
            *out = make_float(x / y);
            return OK;
    }
}

static int parse_number(const char *t, Value *out) {
    char *end;
    if (strchr(t, '.')) {
        double f = strtod(t, &end);
        if (*end || end == t) return 0;
        *out = make_float(f);
    } else {
        long long i = strtoll(t, &end, 10);
        if (*end || end == t) return 0;
        *out = make_int(i);
    }
    return 1;
}

static int run(char *line, Stack *s) {
    for (char *tok = strtok(line, " \t\r\n"); tok; tok = strtok(NULL, " \t\r\n")) {
        size_t n = strlen(tok);
        Value v;
        if (n >= 2 && tok[0] == '"' && tok[n - 1] == '"') {
            push(s, make_str(tok + 1, n - 2));
        } else if (n == 1 && strchr("+-*/", tok[0])) {
            if (s->len < 2) return E_UNDER;
            Value b = s->data[--s->len], a = s->data[--s->len], r;
            int e = arith(tok[0], a, b, &r);
            value_free(&a);
            value_free(&b);
            if (e) return e;
            push(s, r);
        } else if (strcmp(tok, "dup") == 0) {
            if (s->len < 1) return E_UNDER;
            Value top = s->data[s->len - 1];
            push(s, top.type == T_STR ? make_str(top.as.s, strlen(top.as.s)) : top);   /* deep copy */
        } else if (strcmp(tok, "swap") == 0) {
            if (s->len < 2) return E_UNDER;
            Value t = s->data[s->len - 1];
            s->data[s->len - 1] = s->data[s->len - 2];
            s->data[s->len - 2] = t;
        } else if (strcmp(tok, "drop") == 0) {
            if (s->len < 1) return E_UNDER;
            value_free(&s->data[--s->len]);
        } else if (strcmp(tok, "type") == 0) {
            if (s->len < 1) return E_UNDER;
            static const char *names[] = {"int", "float", "str"};
            Value *top = &s->data[s->len - 1];
            const char *nm = names[top->type];
            value_free(top);
            *top = make_str(nm, strlen(nm));
        } else if (parse_number(tok, &v)) {
            push(s, v);
        } else {
            return E_TOKEN;
        }
    }
    return OK;
}

int main(void) {
    char line[4096];
    Stack s = {0};
    while (fgets(line, sizeof line, stdin)) {
        int e = run(line, &s);
        if (e) {
            printf("error: %s\n", errname[e]);
        } else if (s.len == 0) {
            printf("(empty)\n");
        } else {
            for (size_t i = 0; i < s.len; i++) {
                Value v = s.data[i];
                if (i) putchar(' ');
                if (v.type == T_INT) printf("%lld", v.as.i);
                else if (v.type == T_FLOAT) printf("%g", v.as.f);
                else printf("\"%s\"", v.as.s);
            }
            putchar('\n');
        }
        clear(&s);
    }
    free(s.data);
    return 0;
}
```

**What the tagged union buys you:**
- `Value` is 16 bytes (an 8-byte payload plus the tag and padding), whatever its type, so a stack of values is a plain array.
- The `type` tag drives every `switch`. Reading `as.s` when the tag says INT would reinterpret an integer as a pointer and crash, which is why every access is gated by the tag.
- **Ownership:** a STR owns its heap buffer. Pushing transfers ownership to the stack, popping transfers it to the operation, which must free its inputs. `dup` deep-copies so the two values never share (and double-free) a buffer. `clear` frees whatever is left after errors.

This is a miniature of CPython's object model or Lua's `TValue`. Compiling with `-fsanitize=address` locally verifies there are no leaks across all 5000 random lines.
