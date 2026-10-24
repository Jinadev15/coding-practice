# Numbers: int, float, complex

Numbers look trivial until a program prints `0.30000000000000004`, or a C programmer's `-7 / 2` disagrees with yours. This lesson covers Python's numeric types: what they can represent, exactly how each arithmetic operator behaves (especially with negative numbers), and where floating point bites. These rules come up constantly in interviews and judge problems.

## 1. The numeric tower

| Type | Example literals | Represents | Precision |
|---|---|---|---|
| `int` | `0`, `-42`, `1_000_000`, `0xFF`, `0b1010`, `0o17` | Whole numbers | **Unlimited** (bignum) |
| `float` | `3.14`, `-0.5`, `1e9`, `2.5e-3`, `float('inf')` | Real numbers, approximately | IEEE-754 double: ~15–17 significant digits |
| `complex` | `3+4j`, `2j`, `complex(1, -1)` | a + bi | two floats |
| `bool` | `True`, `False` | a subclass of `int` (1 and 0) | — |

Standard-library extras: `decimal.Decimal` (exact decimal arithmetic for money) and `fractions.Fraction` (exact rationals).

```python
print(type(7), type(7.0), type(7j), type(True))
print(True + True)        # bool is an int: 2
```

```output
<class 'int'> <class 'float'> <class 'complex'> <class 'bool'>
2
```

## 2. `int`: arbitrary precision

A Python `int` never overflows. It grows to use as much memory as it needs.

```python
print(2 ** 100)
print(len(str(3 ** 8000)))      # a 3817-digit number, computed exactly
```

```output
1267650600228229401496703205376
3817
```

> [!WARNING]
> Since Python 3.11, converting an `int` with more than **4300 digits** to or from a decimal string raises `ValueError` (a protection against denial-of-service attacks that use huge numbers). The arithmetic itself is unlimited. If you really need the digits, call `sys.set_int_max_str_digits(0)`.

In C/C++ a 32-bit `int` holds only up to 2,147,483,647, and overflow is a classic bug (and *undefined behaviour* for signed types in C). In Python you simply don't have that problem. The price is speed and memory: a small int is a 28-byte object, not 4 bytes.

### Literals in other bases

```python
print(0b1010, 0o17, 0xFF)          # binary, octal, hex literals → 10 15 255
print(bin(10), oct(8), hex(255))   # int → base string: 0b1010 0o10 0xff
print(int("ff", 16), int("1010", 2), int("  42  "))   # str → int: 255 10 42
print(1_000_000)                   # underscores for readability → 1000000
```

## 3. The arithmetic operators

| Operator | Name | `7 ⊕ 2` | `-7 ⊕ 2` | Result type |
|---|---|---|---|---|
| `+` `-` `*` | add, subtract, multiply | 9, 5, 14 | −5, −9, −14 | int if both int |
| `/` | **true division** | 3.5 | −3.5 | **always float** |
| `//` | **floor division** | 3 | **−4** | int if both int |
| `%` | modulo (remainder) | 1 | **1** | sign follows the **divisor** |
| `**` | power | 49 | 49 | int, or float for negative exponents |

### Floor division and modulo with negatives: the rule that trips everyone

> [!KEY]
> Python's `//` rounds **toward negative infinity** (floor). `%` is defined so that the identity
> **`a == (a // b) * b + (a % b)`** always holds, which makes the result of `%` take the **sign of the divisor `b`**.

```python
print(-7 // 2, -7 % 2)    # -4  1   because -4*2 + 1 = -7
print(7 // -2, 7 % -2)    # -4 -1   because -4*-2 + (-1) = 7
print(divmod(-7, 2))      # (-4, 1): both at once
```

<div class="figure">
<svg viewBox="0 0 600 120" width="600" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="13">
  <line x1="30" y1="60" x2="570" y2="60" stroke="currentColor" stroke-opacity=".5"/>
  <g fill="currentColor">
    <text x="62" y="85">-5</text><text x="142" y="85">-4</text><text x="222" y="85">-3</text><text x="302" y="85">-2</text>
    <text x="382" y="85">-1</text><text x="465" y="85">0</text>
  </g>
  <g stroke="currentColor" stroke-opacity=".5"><line x1="70" y1="55" x2="70" y2="65"/><line x1="150" y1="55" x2="150" y2="65"/><line x1="230" y1="55" x2="230" y2="65"/><line x1="310" y1="55" x2="310" y2="65"/><line x1="390" y1="55" x2="390" y2="65"/><line x1="470" y1="55" x2="470" y2="65"/></g>
  <circle cx="190" cy="60" r="6" fill="#d29922"/>
  <text x="168" y="40" fill="#d29922">-3.5</text>
  <path d="M184 50 C170 30, 160 30, 152 50" stroke="#3fb950" fill="none" stroke-width="2"/>
  <text x="95" y="30" fill="#3fb950">Python floor → -4</text>
  <path d="M196 50 C210 30, 220 30, 228 50" stroke="#f85149" fill="none" stroke-width="2"/>
  <text x="235" y="30" fill="#f85149">C truncation → -3</text>
</svg>
<figcaption>−7 / 2 = −3.5. Python's <code>//</code> floors to −4; C/C++ <code>/</code> on ints truncates toward zero to −3.</figcaption>
</div>

> [!DANGER]
> Porting code between Python and C/C++? In C, `-7 / 2 == -3` and `-7 % 2 == -1`. In Python `-7 // 2 == -4` and `-7 % 2 == 1`. Python's version is mathematically nicer: `n % k` is always in `[0, k)` for positive `k`, which is exactly what you want for circular indexing (`(i - 1) % n` wraps correctly).

### Power

```python
print(2 ** 10)        # 1024
print(2 ** -1)        # 0.5  (negative exponent → float)
print(2 ** 0.5)       # 1.4142135623730951
print(-2 ** 2)        # -4   ** binds tighter than unary minus: -(2**2)
print((-2) ** 2)      # 4
print(2 ** 3 ** 2)    # 512  ** is RIGHT-associative: 2 ** (3**2)
print(pow(3, 200, 1000))   # 3^200 mod 1000 computed fast: modular exponentiation
```

## 4. `float`: IEEE-754 binary floating point

A `float` is a 64-bit **binary** approximation of a real number: 1 sign bit, 11 exponent bits and 52 fraction bits. Most decimal fractions **cannot be represented exactly in binary**, just as 1/3 cannot be written exactly in decimal.

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
from decimal import Decimal
print(Decimal(0.1))       # the exact value actually stored for 0.1
```

```output
0.30000000000000004
False
0.1000000000000000055511151231257827021181583404541015625
```

> [!KEY]
> Never compare floats with `==`. Compare within a tolerance:
> ```python
> import math
> math.isclose(0.1 + 0.2, 0.3)          # True (default rel_tol=1e-09)
> abs(a - b) < 1e-9                      # manual absolute tolerance
> ```

Important float facts:

| Fact | Value |
|---|---|
| Largest float | `1.7976931348623157e+308` (`sys.float_info.max`) |
| Machine epsilon | `2.220446049250313e-16`, the gap between 1.0 and the next float |
| Exact integers up to | 2⁵³ = 9,007,199,254,740,992. Beyond that, not every integer is representable |
| Overflow | `1e308 * 10` → `inf` (no exception) |
| Special values | `float('inf')`, `float('-inf')`, `float('nan')`; note `nan != nan` |

```python
print(2**53 + 1 == float(2**53 + 1))    # False: the float rounded to 2**53
big = 10**20
print(big == 1e20)                       # True here, but don't rely on it
```

> [!DANGER]
> Never use `float` for money. `0.1 + 0.2` dollars is wrong. Use integer cents (`int`) or `Decimal("0.10")`. Build `Decimal` from **strings**, not floats: `Decimal(0.1)` captures the binary error.

## 5. Converting and rounding

```python
int(3.9)      # 3    truncates toward zero
int(-3.9)     # -3   truncates toward zero (NOT floor)
float(7)      # 7.0
float("2.5")  # 2.5
round(3.14159, 2)  # 3.14
```

`round()` uses **banker's rounding** (round half to even) for exact halves:

```python
print(round(0.5), round(1.5), round(2.5), round(3.5))   # 0 2 2 4
print(round(2.675, 2))                                  # 2.67 (!) because 2.675 is really 2.67499999…
```

| Function | −3.5 | 3.5 | Rule |
|---|---|---|---|
| `int(x)` / `math.trunc(x)` | −3 | 3 | toward zero |
| `math.floor(x)` | −4 | 3 | toward −∞ |
| `math.ceil(x)` | −3 | 4 | toward +∞ |
| `round(x)` | −4 | 4 | nearest, ties to even |

### Integer ceiling division without floats

A classic judge trick: `ceil(a / b)` for positive integers, done exactly with integers:

```python
a, b = 10**18 + 1, 3
print(-(-a // b))        # 333333333333333334: exact ceiling division
print((a + b - 1) // b)  # 333333333333333334: the same, for positive a and b
import math
print(math.ceil(a / b))  # 333333333333333312: WRONG, the float lost digits
```

Using `math.ceil(a / b)` goes through a float and **loses precision** for numbers above 2⁵³.

## 6. Mixed arithmetic: type promotion

When operand types differ, the "narrower" type is converted: `bool → int → float → complex`.

```python
print(1 + 2.0)       # 3.0   (int + float → float)
print(7.0 // 2)      # 3.0   (floor division of floats gives a float)
print(True * 3.5)    # 3.5
print(1 + 2j + 0.5)  # (1.5+2j)
```

## 7. `complex` (briefly)

```python
z = 3 + 4j
print(z.real, z.imag, abs(z), z.conjugate())   # 3.0 4.0 5.0 (3-4j)
import cmath
print(cmath.sqrt(-1))                          # 1j
```

You'll use complex numbers in signal processing (FFT) and control theory (poles and zeros), both common in robotics.

## 8. Exact alternatives: `Decimal` and `Fraction`

```python
from decimal import Decimal, getcontext
print(Decimal("0.1") + Decimal("0.2"))         # 0.3, exactly
getcontext().prec = 50
print(Decimal(1) / Decimal(7))                 # 50 significant digits

from fractions import Fraction
print(Fraction(1, 3) + Fraction(1, 6))         # 1/2
```

## 9. Exam-ready answers

> [!EXAM]
> **Numeric types in Python.** Python provides `int` (integers of arbitrary precision, limited only by memory), `float` (double-precision IEEE-754 binary floating point, about 15–17 significant decimal digits), and `complex` (a pair of floats for the real and imaginary parts). `bool` is a subclass of `int` with values `True` (1) and `False` (0). In mixed arithmetic the operands are promoted to the wider type in the order `int → float → complex`. The `decimal` and `fractions` modules provide exact decimal and rational arithmetic.

> [!EXAM]
> **`/` vs `//` vs `%`.** `/` performs true division and always returns a float. `//` performs floor division, rounding the quotient toward negative infinity. `%` returns the remainder such that `a == (a // b) * b + a % b`, so the result has the same sign as the divisor. For example, `-7 // 2 == -4` and `-7 % 2 == 1`. C truncates toward zero instead, giving −3 and −1.

> [!EXAM]
> **Why is `0.1 + 0.2 != 0.3`?** Floats are stored in binary, and 0.1, 0.2 and 0.3 have no finite binary representation. Each is rounded to the nearest representable double, and the rounding errors make the computed sum `0.30000000000000004`. Floats should be compared with a tolerance (`math.isclose`), and exact decimal quantities such as money should use integers or `Decimal`.

## 10. Cheat sheet

| Want | Write |
|---|---|
| quotient and remainder | `q, r = divmod(a, b)` |
| exact ceiling of `a/b` (ints) | `-(-a // b)` |
| last digit | `n % 10` |
| drop last digit | `n // 10` |
| is `n` even? | `n % 2 == 0` |
| wrap index backwards | `(i - 1) % n` |
| fast `a^b mod m` | `pow(a, b, m)` |
| float equality | `math.isclose(x, y)` |
| infinity sentinel | `float('inf')` |
| number of digits | `len(str(abs(n)))` |

> [!INTERVIEW]
> **"What does `round(2.5)` return, and why?"** `2`. Python 3 uses round-half-to-even (banker's rounding), which avoids the upward bias of always rounding .5 up when summing many rounded values. A follow-up is `round(2.675, 2) == 2.67`, which happens because 2.675 is stored as 2.67499999999999982236431605997495353221893310546875.
