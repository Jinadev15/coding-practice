# Fixed-Point Arithmetic

Many microcontrollers used in motor controllers, sensors and small drones (Cortex-M0/M0+/M3, older DSPs, FPGAs) have **no floating-point unit**. There, a software `float` multiply costs dozens of cycles. Fixed-point arithmetic represents fractional numbers as scaled integers, so they run at integer speed with deterministic timing and bit-exact reproducibility across platforms. This lesson covers Q formats, conversions, the multiply and divide rules, rounding, saturation, and a fixed-point filter and PID.

## 1. The idea: an implied binary point

A **Qm.n** number stores a real value `x` as the integer `X = round(x · 2ⁿ)`, using m integer bits (plus sign) and n fraction bits.

| Format | Container | Range | Resolution |
|---|---|---|---|
| Q15 (Q0.15) | `int16_t` | [-1, 1 - 2⁻¹⁵] | 3.05e-5 |
| Q31 | `int32_t` | [-1, 1) | 4.66e-10 |
| Q16.16 | `int32_t` | [-32768, 32768) | 1.53e-5 |
| Q8.8 | `int16_t` | [-128, 128) | 0.0039 |

```c
#include <stdint.h>
typedef int32_t q16_t;                 /* Q16.16 */
#define Q16_ONE   (1 << 16)
#define Q16(x)    ((q16_t)((x) * 65536.0 + ((x) >= 0 ? 0.5 : -0.5)))   /* compile-time constants */
static inline double q16_to_double(q16_t a) { return a / 65536.0; }
```

> [!KEY]
> Choose the format from the **physical range and resolution** you need. An IMU angle within ±π that needs 0.001 rad fits Q3.12 in 16 bits. A wheel position in metres up to 1000 m with 0.1 mm resolution needs Q10.14 or more, so use 32 bits.

## 2. Addition and subtraction

Values in the **same** Q format add as plain integers: `(a·2ⁿ) + (b·2ⁿ) = (a+b)·2ⁿ`. Values in different formats must first be shifted to a common format. The danger is overflow, and signed integer overflow in C is undefined behaviour, so production code uses **saturating** arithmetic:

```c
static inline q16_t q16_add_sat(q16_t a, q16_t b) {
    int64_t s = (int64_t)a + b;
    if (s > INT32_MAX) return INT32_MAX;
    if (s < INT32_MIN) return INT32_MIN;
    return (q16_t)s;
}
```

Saturation is what you want in control: a velocity command that clips at the maximum is safe. One that wraps from +32767 to -32768 reverses the motor.

## 3. Multiplication: widen, multiply, shift, round

`(a·2ⁿ)(b·2ⁿ) = ab·2²ⁿ`, so the raw product has **2n** fraction bits and must be shifted right by n. It also needs twice the width:

```c
static inline q16_t q16_mul(q16_t a, q16_t b) {
    int64_t p = (int64_t)a * b;                 /* Q32.32 in 64 bits: cannot overflow */
    p += (int64_t)1 << 15;                      /* round half up (add 0.5 LSB before shifting) */
    p >>= 16;                                   /* arithmetic shift on all mainstream compilers */
    if (p > INT32_MAX) return INT32_MAX;        /* saturate the result */
    if (p < INT32_MIN) return INT32_MIN;
    return (q16_t)p;
}
```

> [!DANGER]
> `a * b >> 16` with 32-bit `a` and `b` overflows for any product above about 1.0 × 32768. Always widen **before** multiplying: `(int64_t)a * b`, not `(int64_t)(a * b)`.

Right-shifting a negative number truncates toward −∞. Adding half an LSB first gives round-half-up, which is unbiased enough for most filters. Before C23, right-shifting a negative signed value is implementation-defined. GCC, Clang and every DSP compiler use an arithmetic shift, and CMSIS-DSP relies on it.

**Q15 × Q15 on a DSP**: `(int32_t)a * b` gives Q30, and `>> 15` gives Q15. The single overflow case is -1 × -1 = +1, which isn't representable in Q15 and must saturate to 0x7FFF. That's why ARM provides the `QDADD`/`SSAT` saturating instructions.

## 4. Division

`(a·2ⁿ)/(b·2ⁿ) = a/b` has **no** fraction bits, so pre-shift the dividend:

```c
static inline q16_t q16_div(q16_t a, q16_t b) {
    if (b == 0) return a >= 0 ? INT32_MAX : INT32_MIN;      /* define the edge case */
    int64_t n = ((int64_t)a << 16);
    n += ((n >= 0) == (b >= 0)) ? b / 2 : -b / 2;            /* round to nearest */
    int64_t q = n / b;
    return q > INT32_MAX ? INT32_MAX : q < INT32_MIN ? INT32_MIN : (q16_t)q;
}
```

Division is slow on small MCUs (Cortex-M0 has no hardware divide), so precompute reciprocals: multiply by `Q16(1.0 / dt)` instead of dividing by `dt` every loop.

## 5. Error budget

Each multiply adds up to ½ LSB of rounding error. Through N chained operations, the error grows to about N/2 LSB, or √N·LSB/√12 when errors are random. Keep intermediate results in **wider** accumulators: an FIR filter accumulates Q30 products in an `int64_t` and rounds once at the end, instead of rounding every tap.

```c
/* Q15 FIR: y[n] = Σ h[k]·x[n-k] */
int16_t fir_q15(const int16_t *h, const int16_t *x_hist, int taps) {
    int64_t acc = 0;                               /* Q30 accumulator with lots of headroom */
    for (int k = 0; k < taps; ++k) acc += (int32_t)h[k] * x_hist[k];
    acc = (acc + (1 << 14)) >> 15;                 /* one rounding step back to Q15 */
    if (acc > 32767) acc = 32767;
    if (acc < -32768) acc = -32768;
    return (int16_t)acc;
}
```

## 6. A fixed-point PID

```c
typedef struct { q16_t kp, ki, kd, integ, prev_err, out_min, out_max; } PidQ16;

q16_t pid_step(PidQ16 *p, q16_t setpoint, q16_t measured) {      /* gains pre-multiplied by dt */
    q16_t err = q16_add_sat(setpoint, -measured);
    q16_t i = q16_add_sat(p->integ, q16_mul(p->ki, err));
    if (i > p->out_max) i = p->out_max;            /* anti-windup: clamp the integrator */
    if (i < p->out_min) i = p->out_min;
    p->integ = i;
    q16_t d = q16_mul(p->kd, q16_add_sat(err, -p->prev_err));
    p->prev_err = err;
    q16_t u = q16_add_sat(q16_add_sat(q16_mul(p->kp, err), i), d);
    return u > p->out_max ? p->out_max : u < p->out_min ? p->out_min : u;
}
```

(`-measured` overflows for INT32_MIN. Production code clamps sensor inputs to a sane range at the boundary, so that value never reaches here.)

## 7. When to use fixed point today

- **Use it** on FPU-less MCUs, in hot DSP loops (CMSIS-DSP `arm_fir_q15`), on FPGAs and in ASIC models, for bit-exact reproducibility (consensus, lockstep simulation, replay), and for quantised neural networks (int8 inference is fixed point).
- **Avoid it** when you have a single-precision FPU (Cortex-M4F/M7/M33) and dynamic range matters. Floats are simpler and just as fast there, though double precision may still be emulated in software.

> [!EXAM]
> **How do you multiply two Q16.16 numbers, and why?**
> The raw product of two values scaled by 2¹⁶ is scaled by 2³², so it must be computed in 64 bits (`(int64_t)a * b`). Then add 2¹⁵ to round to nearest, shift right by 16 to return to Q16.16, and saturate to the int32 range. Widening before multiplying prevents intermediate overflow, rounding removes the negative bias of truncation, and saturation keeps out-of-range results at the limits instead of wrapping.

> [!INTERVIEW]
> - "Represent 0.3 in Q15." round(0.3 × 32768) = 9830 = 0x2666.
> - "What is −1 × −1 in Q15?" It overflows (+1 isn't representable), so the result saturates to 0x7FFF.
