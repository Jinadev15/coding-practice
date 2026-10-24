# Operators and Precedence

Operators are the verbs of expressions. You already know the arithmetic ones. This lesson completes the set: comparison (including Python's unusual **chaining**), logical, bitwise, assignment, identity and membership operators, and the **precedence table** that decides how an expression without parentheses is grouped. Several rules here differ from C and C++, and the differences are classic interview traps.

## 1. The operator families

| Family | Operators | Result |
|---|---|---|
| Arithmetic | `+ - * / // % **`, unary `-` `+` | number |
| Comparison | `== != < <= > >=` | `bool` |
| Identity | `is`, `is not` | `bool` |
| Membership | `in`, `not in` | `bool` |
| Logical | `not`, `and`, `or` | an operand, or `bool` for `not` |
| Bitwise | `& \| ^ ~ << >>` | `int` |
| Assignment | `= += -= *= /= //= %= **= &= \|= ^= <<= >>=` | (statement) |
| Assignment expression | `:=` (walrus) | the assigned value |
| Conditional | `a if cond else b` | `a` or `b` |

## 2. Comparison operators and chaining

Comparisons return `True` or `False`. Python lets you **chain** them, as in mathematical notation:

```python
x = 5
print(1 < x < 10)        # True: means (1 < x) and (x < 10)
print(0 <= x <= 3)       # False
```

> [!KEY]
> `a OP1 b OP2 c` means **`(a OP1 b) and (b OP2 c)`**, with `b` evaluated only once. Evaluation stops at the first `False` (short-circuit).

This is very different from C, where `1 < x < 10` means `(1 < x) < 10`, which compares a 0/1 truth value with 10 and is *always true*.

Chaining applies to **every** comparison operator, including `==`, `in` and `is`, which produces some surprising expressions:

```python
print(3 == 3.0 == True)      # False: (3 == 3.0) and (3.0 == True) → True and False
print(1 < 3 > 2)             # True:  (1 < 3) and (3 > 2), legal but unreadable
print("a" in "abc" == True)  # False: ("a" in "abc") and ("abc" == True)
```

> [!DANGER]
> Never write `x == True` or `cond == False`. Write `if x:` / `if not cond:`. Combined with chaining, `== True` produces results like the last line above.

### Comparing different types

`==` between unrelated types is simply `False` (`1 == "1"` is `False`). Ordering comparisons (`<`, `>`) between unrelated types raise `TypeError`:

```python
print(1 == "1")          # False
# print(1 < "1")         # TypeError: '<' not supported between instances of 'int' and 'str'
print(1 == 1.0 == True)  # True: numeric types compare by value; True == 1
```

Sequences compare **lexicographically**: element by element, and the first difference decides.

```python
print([1, 2, 3] < [1, 3])      # True: 2 < 3 at index 1
print((2, "a") < (2, "b"))     # True
print([1, 2] < [1, 2, 0])      # True: a proper prefix is smaller
```

## 3. Logical operators: `not`, `and`, `or`

| Expression | Result |
|---|---|
| `not x` | `True` if `x` is falsy, else `False` (always a `bool`) |
| `x and y` | if `x` is falsy → `x`, otherwise → `y` |
| `x or y` | if `x` is truthy → `x`, otherwise → `y` |

`and` / `or` **short-circuit**: the right operand is evaluated only if needed. They also return **one of the operands**, not necessarily `True`/`False`. That's covered in depth in the next lesson.

```python
n = 0
print(n != 0 and 10 / n > 1)   # False: the division never runs, so no ZeroDivisionError
print("" or "default")         # default
```

## 4. Bitwise operators

Bitwise operators work on the binary representation of integers, bit by bit. They matter for flags, masks, low-level and embedded code, and a whole family of interview problems.

| Op | Name | `5 op 3` (`101`, `011`) | Rule per bit |
|---|---|---|---|
| `&` | AND | `1` (`001`) | 1 if both are 1 |
| `\|` | OR | `7` (`111`) | 1 if either is 1 |
| `^` | XOR | `6` (`110`) | 1 if they differ |
| `~` | NOT | `~5 == -6` | flips every bit |
| `<<` | left shift | `5 << 2 == 20` | multiply by 2ⁿ |
| `>>` | right shift | `20 >> 2 == 5` | floor-divide by 2ⁿ |

<div class="figure">
<svg viewBox="0 0 520 170" width="520" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="16">
  <g fill="currentColor">
    <text x="40" y="35">  5 =</text><text x="120" y="35">0 1 0 1</text>
    <text x="40" y="65">  3 =</text><text x="120" y="65">0 0 1 1</text>
  </g>
  <line x1="110" y1="78" x2="220" y2="78" stroke="currentColor" stroke-opacity=".5"/>
  <g>
    <text x="40" y="102" fill="#3fb950">5 &amp; 3</text><text x="120" y="102" fill="#3fb950">0 0 0 1</text><text x="240" y="102" fill="#3fb950">= 1</text>
    <text x="40" y="128" fill="#2f81f7">5 | 3</text><text x="120" y="128" fill="#2f81f7">0 1 1 1</text><text x="240" y="128" fill="#2f81f7">= 7</text>
    <text x="40" y="154" fill="#d29922">5 ^ 3</text><text x="120" y="154" fill="#d29922">0 1 1 0</text><text x="240" y="154" fill="#d29922">= 6</text>
  </g>
  <g font-family="sans-serif" font-size="12" fill="currentColor" fill-opacity=".7">
    <text x="310" y="102">both bits 1</text><text x="310" y="128">at least one bit 1</text><text x="310" y="154">bits differ</text>
  </g>
</svg>
<figcaption>Bitwise operations act column by column.</figcaption>
</div>

### Why `~5 == -6`

Python ints behave as if they had **infinitely many** sign bits in **two's complement**. Flipping every bit of `x` gives `-x - 1`:

```python
print(~5, ~0, ~-1)     # -6 -1 0
print(-20 >> 2)        # -5: right shift floors, like // 4
```

### Bit-manipulation idioms

```python
x = 0b10110
print((x >> 2) & 1)        # read bit 2           → 1
x |= (1 << 0)              # set bit 0
x &= ~(1 << 4)             # clear bit 4
x ^= (1 << 1)              # toggle bit 1
print(bin(x))
n = 40
print(n & (n - 1) == 0)    # is n a power of two? (False for 40)
print(n & -n)              # lowest set bit of n  → 8
print(bin(n).count("1"), n.bit_count())   # popcount → 2 2
```

> [!WARNING]
> Python's precedence for `&`, `|`, `^` differs from C. In Python they bind **tighter** than comparisons, so `5 & 3 == 1` means `(5 & 3) == 1`, which is `True`. In C, `5 & 3 == 1` means `5 & (3 == 1)`, which is `0`. Parenthesise bitwise expressions anyway; nobody remembers these tables reliably.

## 5. Assignment operators

Augmented assignment `x op= y` is shorthand for `x = x op y`, with two differences:

1. The target is evaluated only **once**. This matters for `a[f()] += 1`.
2. For **mutable** objects it may modify **in place** (`list +=` extends the existing list), as you saw in the Variables lesson.

```python
count = 10
count += 1      # 11
count //= 2     # 5
count **= 2     # 25
count %= 7      # 4
```

> [!DANGER]
> Python has **no `++` or `--`**. `x++` is a `SyntaxError`, and `++x` is legal but does nothing: it's unary plus applied twice. Write `x += 1`.

### The walrus operator `:=` (assignment expression)

`:=` assigns **inside an expression** and yields the value. It's useful for avoiding a computation twice:

```python
import sys
data = [3, 8, 1, 9]
if (n := len(data)) > 3:
    print(f"list is long ({n} elements)")

# read lines until an empty one
# while (line := input()) != "":
#     process(line)
```

## 6. Identity and membership

```python
a = [1, 2]
print(a is not None)          # identity: True
print(2 in a, 5 not in a)     # membership: True True
print("ell" in "hello")       # substring: True
print("k" in {"k": 1})        # dict membership checks KEYS: True
```

Membership is **O(n)** for lists and strings (a linear scan), but **O(1) on average** for sets and dicts (hash lookup). This difference decides whether many interview solutions pass.

## 7. The precedence table

From **highest** (binds tightest) to **lowest**:

| Precedence | Operators | Associativity |
|---|---|---|
| 1 | `(...)`, `[...]`, `{...}`, calls `f(x)`, indexing `a[i]`, attribute `a.b` | left |
| 2 | `await` | — |
| 3 | `**` | **right** |
| 4 | unary `+x`, `-x`, `~x` | — |
| 5 | `*`, `/`, `//`, `%`, `@` | left |
| 6 | `+`, `-` | left |
| 7 | `<<`, `>>` | left |
| 8 | `&` | left |
| 9 | `^` | left |
| 10 | `\|` | left |
| 11 | comparisons `in, not in, is, is not, <, <=, >, >=, !=, ==` | **chained** |
| 12 | `not` | — |
| 13 | `and` | left |
| 14 | `or` | left |
| 15 | `if … else` | right |
| 16 | `lambda` | — |
| 17 | `:=` | — |

Memory aid: **P E U M A S B C L**, i.e. Parentheses, Exponent, Unary, Multiplicative, Additive, Shifts, Bitwise (`& ^ |`), Comparisons, Logical (`not and or`).

Worked examples:

```python
print(-3 ** 2)           # -9:  ** before unary minus → -(3**2)
print(2 * 3 % 4)         # 2:   same level, left to right → (2*3) % 4
print(10 - 4 - 3)        # 3:   left-assoc → (10-4)-3
print(2 ** 3 ** 2)       # 512: right-assoc → 2**(3**2)
print(1 + 2 << 1)        # 6:   + before << → (1+2) << 1
print(not 1 == 2)        # True: == before not → not (1 == 2)
print(10 / 2 * 5)        # 25.0: left to right, NOT 10 / (2*5)
```

> [!TIP]
> When in doubt, add parentheses. They cost nothing at run time and make intent explicit. Code reviewers prefer `(a & mask) == 0` over relying on the table.

## 8. Exam-ready answers

> [!EXAM]
> **Chained comparisons.** Python allows comparison operators to be chained: `a < b < c` is evaluated as `(a < b) and (b < c)`, except that `b` is evaluated only once and evaluation stops as soon as one comparison is false. In C the same expression compares the boolean result of `a < b` with `c`, which is usually a logic error.

> [!EXAM]
> **Operator precedence and associativity.** Precedence determines which operator is applied first in an expression without parentheses. Associativity determines the grouping of operators with equal precedence. In Python, exponentiation has the highest precedence among arithmetic operators and is right-associative (`2**3**2 == 512`). Multiplicative operators bind tighter than additive ones, shifts and bitwise operators come next, then comparisons (which chain), then `not`, `and` and `or`. Most binary operators are left-associative.

> [!EXAM]
> **Bitwise operators.** `&` (AND), `|` (OR), `^` (XOR), `~` (NOT), `<<` and `>>` (shifts) operate on the two's-complement binary representation of integers. Left shift by n multiplies by 2ⁿ; right shift by n floor-divides by 2ⁿ. Because Python integers have unbounded precision, `~x` equals `-x-1`.

## 9. Cheat sheet

| Idiom | Meaning |
|---|---|
| `lo <= x < hi` | range check |
| `a == b == c` | all three equal |
| `x & 1` | odd? |
| `x >> k & 1` | bit k |
| `x \| (1 << k)` | set bit k |
| `x & ~(1 << k)` | clear bit k |
| `x ^ (1 << k)` | toggle bit k |
| `x & (x - 1) == 0` (x > 0) | power of two |
| `x & -x` | lowest set bit |
| `a ^ b ^ a == b` | XOR cancels |
| `(n := len(s)) > 10` | assign and test |

> [!INTERVIEW]
> **"Find the number that appears once when every other number appears twice, in O(1) space."** XOR every element together. Pairs cancel (`x ^ x == 0`) and `0 ^ y == y`, so what's left is the single number. This is LeetCode 136, and it's the classic demonstration of why bitwise operators matter.
