# Operators and Precedence

C's operators look like Python's, but several **behave differently**: integer division truncates, `%` follows the dividend's sign, there's `++`/`--` with prefix and postfix forms, `=` is an expression, comparisons don't chain, and logical operators return `0` or `1`. C also has more operators (address-of `&`, dereference `*`, `->`, `sizeof`, the comma operator) and a precedence table with known traps. This lesson makes every expression predictable.

## 1. Arithmetic

| Operator | Meaning | Note |
|---|---|---|
| `+ - *` | as usual | overflow: unsigned wraps, signed is UB |
| `/` | division | **integer ÷ integer truncates toward zero**: `7/2 == 3`, `-7/2 == -3` |
| `%` | remainder | integers only; the sign follows the **dividend**: `-7 % 3 == -1` |

```c
printf("%d %d %d %d\n", 7/2, -7/2, 7%3, -7%3);   /* 3 -3 1 -1 */
printf("%f\n", 7/2.0);                             /* 3.500000: one double operand → double division */
```

> [!DANGER]
> `double avg = sum / count;` with two `int`s does **integer** division first, then converts: `5/2` gives `2.0`. Cast one operand: `(double)sum / count`. Python's `//` floors (`-7//2 == -4`), but C truncates (`-3`). Guard division by zero yourself: integer division by zero is UB and usually crashes (SIGFPE).

## 2. Increment and decrement: `++` and `--`

| Expression | Effect on `i` | Value of the expression |
|---|---|---|
| `i++` (postfix) | i becomes i + 1 | the **old** value |
| `++i` (prefix) | i becomes i + 1 | the **new** value |

```c
int i = 5;
int j = i++ + 1;     /* j = 5 + 1 = 6, then i = 6 */
int k = 5;
int m = ++k + 1;     /* k = 6 first, m = 7 */
```

> [!DANGER]
> Modifying a variable twice, or reading and modifying it, without an intervening sequence point is **undefined behaviour**: `i = i++;`, `a[i] = i++;`, `printf("%d %d", i++, i++);`. There's no "right answer". Use `++` only as a standalone statement or in the simplest expressions.

## 3. Assignment operators

`=`, `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `<<=`, `>>=`. In C, **assignment is an expression** whose value is the assigned value:

```c
a = b = c = 0;                 /* right-associative: c = 0, then b = 0, then a = 0 */
while ((ch = getchar()) != EOF) { ... }   /* assign, then test: a classic idiom */
if (x = 5) { ... }             /* BUG: assigns 5, always true. gcc -Wall warns */
```

## 4. Relational and logical operators

- `== != < > <= >=` produce `int` **1** (true) or **0** (false).
- `&&`, `||` short-circuit and produce 0 or 1. `!x` is 1 if x is 0, else 0.
- Any non-zero value counts as true; zero (and the null pointer) counts as false.

```c
int x = 0;
int r = (x != 0) && (10 / x > 1);    /* safe: the division never runs */
printf("%d\n", 10 > 5 > 1);          /* 0!  (10 > 5) is 1, and 1 > 1 is 0: NO chaining */
```

> [!WARNING]
> C comparisons **don't chain**. `a < b < c` compares `(a < b)`, which is 0 or 1, with `c`. Write `a < b && b < c`.

## 5. Bitwise operators

`&` AND, `|` OR, `^` XOR, `~` NOT, `<<` left shift, `>>` right shift. They're essential for embedded and robotics work (register flags, packed data):

```c
unsigned flags = 0;
flags |= 1u << 3;            /* set bit 3 */
flags &= ~(1u << 3);         /* clear bit 3 */
flags ^= 1u << 2;            /* toggle bit 2 */
int on = (flags >> 2) & 1u;  /* read bit 2 */
```

Shift rules: shifting by ≥ the type's width or by a negative amount is UB; left-shifting a negative signed value is UB; right-shifting a negative signed value is implementation-defined (an arithmetic shift on gcc: `-16 >> 2 == -4`). **Do bit manipulation on unsigned types.**

## 6. Other operators

| Operator | Meaning |
|---|---|
| `sizeof x`, `sizeof(type)` | size in bytes (evaluated at compile time for non-VLA types) |
| `&x` | address of x |
| `*p` | the object p points to |
| `a[i]` | array subscript (`*(a + i)`) |
| `s.f`, `p->f` | struct member through an object / a pointer |
| `(type)x` | cast |
| `c ? a : b` | conditional |
| `a, b` | comma: evaluate a, then b; the value is b |

## 7. The precedence table (highest first)

| Level | Operators | Associativity |
|---|---|---|
| 1 | `()` `[]` `->` `.` postfix `++ --` | left |
| 2 | prefix `++ --`, unary `+ -`, `! ~`, `(type)`, `*` (deref), `&` (addr), `sizeof` | **right** |
| 3 | `* / %` | left |
| 4 | `+ -` | left |
| 5 | `<< >>` | left |
| 6 | `< <= > >=` | left |
| 7 | `== !=` | left |
| 8 | `&` | left |
| 9 | `^` | left |
| 10 | `\|` | left |
| 11 | `&&` | left |
| 12 | `\|\|` | left |
| 13 | `?:` | right |
| 14 | `= += -=` … | **right** |
| 15 | `,` | left |

> [!DANGER]
> The famous trap: **bitwise `&`, `^`, `|` have LOWER precedence than `==`**. `if (flags & MASK == 0)` means `flags & (MASK == 0)`. Always write `if ((flags & MASK) == 0)`. (Python is the other way around, which is why this bites Python programmers moving to C.) Likewise, `*p++` means `*(p++)`, not `(*p)++`.

## 8. Order of evaluation

Precedence decides **grouping**, not the **order** in which operands are evaluated. In `f() + g()`, C doesn't specify which function runs first. Only `&&`, `||`, `?:` and `,` guarantee left-to-right evaluation. Never write code whose result depends on that order.

## 9. Exam-ready answers

> [!EXAM]
> **Integer division and modulus in C.** When both operands of `/` are integers, the result is an integer and the quotient is truncated toward zero (C99 and later), so `7/2 == 3` and `-7/2 == -3`. The `%` operator yields the remainder such that `(a/b)*b + a%b == a`, so its sign matches the dividend (`-7 % 3 == -1`). To obtain a real-valued result at least one operand must be floating point, for example `(double)a / b`. Division or modulus by zero is undefined behaviour.

> [!EXAM]
> **Prefix vs postfix increment.** Both `++i` and `i++` add one to `i`. The value of the prefix expression `++i` is the incremented value, while the value of the postfix expression `i++` is the original value. Modifying the same object more than once between sequence points (for example `i = i++`) is undefined behaviour.

## 10. Cheat sheet

| Need | Code |
|---|---|
| real division | `(double)a / b` |
| is it even? | `n % 2 == 0` |
| safe bit test | `((x >> k) & 1u)` |
| set / clear bit | `x \|= 1u << k;` / `x &= ~(1u << k);` |
| range check | `lo <= x && x < hi` |
| mask test | `(x & MASK) == 0` (parenthesise!) |
| increment | `i++;` on its own line |

> [!INTERVIEW]
> **"What is printed: `int i = 1; printf("%d %d", i, i++);`?"** Nothing defined: it's undefined behaviour, because `i` is read and modified in the same expression and argument evaluation order is unspecified. Different compilers and optimisation levels print different results. Explain sequence points (C11: "sequenced before") rather than guessing a number.
