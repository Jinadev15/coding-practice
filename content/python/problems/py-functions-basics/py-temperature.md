---
id: py-temperature
title: Temperature Conversions
difficulty: Easy
order: 1
tags: functions, return values
---
## Statement
Implement four small functions that **return** values. Don't print inside them.

- `c_to_f(c)`: Celsius → Fahrenheit (`F = C × 9/5 + 32`)
- `f_to_c(f)`: Fahrenheit → Celsius
- `c_to_k(c)`: Celsius → Kelvin (`K = C + 273.15`)
- `convert(value, src, dst)`: converts between any two of the units `"C"`, `"F"`, `"K"`, built **on top of** the three functions above (convert to Celsius first, then to the target)

The driver prints results rounded to 2 decimals.

## Starter
```python
def c_to_f(c):
    pass

def f_to_c(f):
    pass

def c_to_k(c):
    pass

def convert(value, src, dst):
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    v, s, d = input().split()
    print(f"{convert(float(v), s, d):.2f}")
```

## Tests
=== sample
3
100 C F
32 F C
0 C K
---
212.00
0.00
273.15
=== hidden
4
-40 C F
-40 F C
300 K C
212 F K
---
-40.00
-40.00
26.85
373.15
=== hidden
2
25 C C
0 K F
---
25.00
-459.67

## Hints
- In `convert`, write a step that turns any unit into Celsius, and a step that turns Celsius into any unit.
- K → C is `K - 273.15`.

## Solution
Small single-purpose functions, composed through a common pivot unit (Celsius). This avoids writing all six direct conversion formulas.

```python
def c_to_f(c):
    return c * 9 / 5 + 32

def f_to_c(f):
    return (f - 32) * 5 / 9

def c_to_k(c):
    return c + 273.15

def convert(value, src, dst):
    to_c = {"C": lambda v: v, "F": f_to_c, "K": lambda v: v - 273.15}
    from_c = {"C": lambda v: v, "F": c_to_f, "K": c_to_k}
    return from_c[dst](to_c[src](value))
```

The dictionaries of functions are **dispatch tables**: functions as values replace an `if src == ... elif ...` chain. With n units, a pivot needs 2n small conversions instead of n(n−1) direct ones. That's the same idea as an "intermediate representation" in compilers.
