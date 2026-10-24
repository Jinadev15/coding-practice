# Integer and Floating-Point Representation

Every number in a computer is a fixed-size bit pattern. Integers wrap or overflow, and floating-point numbers are **approximations** with limited precision and range. These facts cause real failures:
- Ariane 5 exploded when a 64-bit float was converted to a 16-bit integer.
- The Patriot missile clock drifted because 0.1 isn't exactly representable in binary.
- Accumulated rounding errors make robot odometry drift.

This lesson covers two's complement integers, integer conversions, IEEE-754 floating point, and how to compute and compare safely.

## 1. Unsigned integers

An n-bit unsigned integer represents 0 … 2ⁿ − 1. Arithmetic is **modulo 2ⁿ** (well-defined wrap-around):

```c
uint8_t a = 250;
a += 10;            /* 4: (250 + 10) mod 256 */
unsigned u = 0;
u - 1;              /* UINT_MAX */
```

## 2. Two's complement signed integers

The value of bits b_{n−1} … b₀ is **−b_{n−1}·2^{n−1} + Σ b_i·2^i**. The top bit has negative weight.

| 8-bit pattern | unsigned | two's complement |
|---|---|---|
| `0000 0000` | 0 | 0 |
| `0111 1111` | 127 | 127 |
| `1000 0000` | 128 | −128 |
| `1111 1111` | 255 | −1 |

- The range is −2^{n−1} … 2^{n−1} − 1, so it's asymmetric: there's one more negative value.
- Negation is "invert and add 1": `-x == ~x + 1`.
- Addition and subtraction use the **same hardware** as unsigned arithmetic. Only overflow detection and comparisons differ.
- `-INT_MIN` overflows (there's no positive counterpart), and so do `abs(INT_MIN)` and `INT_MIN / -1`.
- Sign extension: widening a negative value copies the sign bit (`(int8_t)0xFF → (int32_t)0xFFFFFFFF`).

C23 mandates two's complement. Earlier standards also allowed sign-magnitude and ones' complement, though every mainstream platform used two's complement. **Signed overflow remains undefined behaviour.**

## 3. Integer conversions: where bugs hide

**Integer promotion**: types narrower than `int` (`char`, `short`, `uint8_t`) are promoted to `int` before arithmetic.

**Usual arithmetic conversions**: in a binary operation on mixed types, if one operand is unsigned with rank ≥ the other's, the **signed operand converts to unsigned**:

```c
int i = -1;
unsigned u = 1;
if (i < u) puts("less");      /* NOT printed: -1 converts to UINT_MAX, and UINT_MAX < 1 is false */

size_t n = strlen(s);
for (int k = n - 1; k >= 0; k--) { }       /* OK: the int is compared with int */
for (size_t k = n - 1; k >= 0; k--) { }    /* infinite loop: size_t is never < 0 */

uint8_t a = 200, b = 100;
uint8_t c = a + b;            /* a + b = 300 as int, then truncated to 44 on assignment */
```

| Conversion | Result |
|---|---|
| to unsigned, value out of range | well-defined: reduced modulo 2ⁿ |
| to signed, value out of range | **implementation-defined** (GCC wraps); C23 still says implementation-defined |
| float → integer, out of range | **undefined behaviour** |
| integer → float | may round (`(float)16777217` → 16777216) |

Enable `-Wconversion -Wsign-compare` to catch these.

## 4. IEEE-754 floating point

A binary floating-point number is **(−1)^s × 1.f × 2^(e − bias)**:

| Format | Sign | Exponent | Fraction | Precision | Range (approx.) | Machine epsilon |
|---|---|---|---|---|---|---|
| `float` (binary32) | 1 | 8 (bias 127) | 23 | ~7.2 decimal digits | 1.2e−38 … 3.4e38 | 2⁻²³ ≈ 1.19e−7 |
| `double` (binary64) | 1 | 11 (bias 1023) | 52 | ~15.9 digits | 2.2e−308 … 1.8e308 | 2⁻⁵² ≈ 2.22e−16 |

Special values:
- **±0**: they compare equal, but `1/+0 = +inf` and `1/-0 = -inf`.
- **±infinity**: overflow, or `x / 0.0` for x ≠ 0.
- **NaN**: `0.0/0.0`, `sqrt(-1)`, `inf - inf`. NaN compares **unequal to everything, including itself**: `x != x` is the classic NaN test (better: `isnan(x)`).
- **Subnormals**: tiny values near zero with reduced precision (gradual underflow). They can be very slow on some CPUs, which is why flush-to-zero modes exist.

### What can't be represented

Only fractions with power-of-two denominators are exact. `0.1` in binary is `0.000110011001100…`, repeating forever:

```c
printf("%.20f\n", 0.1);           /* 0.10000000000000000555 */
printf("%d\n", 0.1 + 0.2 == 0.3); /* 0 */
float f = 16777217.0f;            /* 2^24 + 1: becomes 16777216, since float has 24 significant bits */
```

### Rounding, cancellation and accumulation

- Every operation rounds to the nearest representable value (round-half-to-even by default), with a relative error ≤ ε/2 per operation.
- **Catastrophic cancellation**: subtracting nearly equal numbers loses significant digits (`1.0000001f - 1.0f`). Rearrange the formula. For example, use `(-b - copysign(sqrt(disc), b)) / 2a` for the quadratic formula, and `log1p` / `expm1` for small arguments.
- **Accumulation**: summing many small values into a large one loses them. Use **Kahan (compensated) summation** or sum in `double`:

```c
double kahan_sum(const float *x, size_t n) {
    double sum = 0.0, c = 0.0;              /* c holds the lost low-order bits */
    for (size_t i = 0; i < n; i++) {
        double y = x[i] - c;
        double t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }
    return sum;
}
```

- Floating-point addition isn't associative: `(a + b) + c != a + (b + c)` in general. That's why `-ffast-math` (which allows reassociation) changes results.

## 5. Comparing floats correctly

```c
#include <math.h>
#include <stdbool.h>

bool nearly_equal(double a, double b, double rel_tol, double abs_tol) {
    if (a == b) return true;                         /* handles infinities and exact matches */
    double diff = fabs(a - b);
    return diff <= abs_tol || diff <= rel_tol * fmax(fabs(a), fabs(b));
}
/* nearly_equal(0.1 + 0.2, 0.3, 1e-9, 1e-12) → true */
```

- A **relative** tolerance scales with magnitude, and an **absolute** tolerance is needed near zero.
- Never use `==` on computed floats, except for deliberate cases (comparing with exactly representable constants, or checking a value hasn't changed).
- Use **integers** (cents, ticks, fixed point) where exactness matters: money, timestamps, and encoder counts in robotics.

## 6. Robotics consequences

| Pitfall | Fix |
|---|---|
| a timestamp in `float` seconds loses ms resolution after ~2.3 hours (2¹³ s, where spacing ≈ 1 ms) | `int64_t` nanoseconds or `double` |
| an angle accumulating past 2π | wrap regularly: `atan2(sin a, cos a)` or `remainder(a, 2*M_PI)` |
| odometry summing millions of increments | double precision, or periodic re-anchoring |
| converting a sensor double to int16 without a range check | clamp first (the Ariane 5 lesson) |
| comparing poses with `==` | tolerance on position and angle |

## 7. Exam-ready answers

> [!EXAM]
> **Two's complement.** In n-bit two's complement, the most significant bit has weight −2^{n−1} and the remaining bits their usual positive weights, giving a range from −2^{n−1} to 2^{n−1} − 1. A value is negated by inverting all bits and adding one, and addition and subtraction are performed by the same circuitry as for unsigned numbers, with results correct modulo 2ⁿ. In C, unsigned arithmetic wraps modulo 2ⁿ by definition, whereas signed overflow is undefined behaviour, and mixing signed and unsigned operands converts the signed operand to unsigned, which can turn negative values into large positive ones.

> [!EXAM]
> **IEEE-754 floating point.** IEEE-754 binary formats represent a number as a sign, a biased exponent and a fraction with an implicit leading 1, giving about 7 significant decimal digits for single precision and 16 for double. Only numbers with finite binary expansions are exact, so values such as 0.1 are rounded, and each arithmetic operation introduces a relative rounding error bounded by half the machine epsilon. Special values include signed zeros, infinities, NaN (which compares unequal to everything, including itself) and subnormal numbers. Floating-point values should therefore be compared with an appropriate relative or absolute tolerance rather than for exact equality.

## 8. Cheat sheet

| Fact | Value / practice |
|---|---|
| `-x` in two's complement | `~x + 1` |
| int8 range | −128 … 127 |
| float exact integers | up to 2²⁴ = 16 777 216 |
| double exact integers | up to 2⁵³ ≈ 9.007e15 |
| `FLT_EPSILON` / `DBL_EPSILON` | 1.19e−7 / 2.22e−16 |
| NaN test | `isnan(x)` (or `x != x`) |
| float equality | relative + absolute tolerance |
| signed < unsigned compare | cast deliberately, enable `-Wsign-compare` |
| long sums | Kahan summation / accumulate in double |

> [!INTERVIEW]
> **"Why does `0.1 + 0.2 != 0.3`?"** None of the three is exactly representable in binary. 0.1 and 0.2 are each rounded to the nearest double, their sum is rounded again, and the result (0.30000000000000004) is a different double from the one nearest to 0.3. Compare with a tolerance, or use decimal or fixed-point arithmetic for money. Follow-up: "is float addition associative?" No. Rounding happens after each operation, so the grouping changes the result.
