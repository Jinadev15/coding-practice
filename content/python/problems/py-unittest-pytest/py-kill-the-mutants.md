---
id: py-kill-the-mutants
title: Write Tests That Kill the Mutants
difficulty: Medium
order: 1
tags: testing, edge cases, assertions, mutation testing
---
## Statement
This time **you write the tests**, and the judge grades their quality by **mutation testing**: your tests run against the correct implementation (they must pass) and against several subtly broken **mutants** (each must be caught by a failing assertion or an unexpected exception).

The function under test parses robot mission durations:

```python
def parse_duration(text: str) -> int:
    """Parse durations like "1h30m", "45s", "2h", "1h0m5s", " 3m " into total seconds.
    Rules: units h, m, s in that order, each at most once, each a non-negative integer;
    surrounding whitespace is ignored; uppercase units are accepted ("1H30M");
    at least one component is required; anything else raises ValueError.
    The total must be <= 86400 (24 h), else ValueError."""
```

Write a function `check(parse_duration)` that **raises `AssertionError`** (use plain `assert`) if the given implementation is wrong, and returns normally if it's correct. You're given the function as a parameter, so it's easy to test many implementations.

Tip: think like an attacker. Test each rule and each boundary: the order of units, repeated units, empty strings, whitespace, case, zero values, the 24-hour limit exactly and just above it, non-digit garbage, and missing numbers (`"h"`).

## Starter
```python
def check(parse_duration):
    assert parse_duration("1h30m") == 5400
```

## Driver
```python
import re
import sys

def correct(text):
    s = text.strip().lower()
    m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", s)
    if not s or not m:
        raise ValueError(text)
    h, mi, se = (int(g) if g else 0 for g in m.groups())
    total = h * 3600 + mi * 60 + se
    if total > 86400:
        raise ValueError(text)
    return total

def m_no_strip(text):
    return correct(text) if text == text.strip() else (_ for _ in ()).throw(ValueError(text))
def m_no_case(text):
    if text != text.lower():
        raise ValueError(text)
    return correct(text)
def m_limit_off_by_one(text):
    s = text.strip().lower()
    m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", s)
    if not s or not m:
        raise ValueError(text)
    h, mi, se = (int(g) if g else 0 for g in m.groups())
    total = h * 3600 + mi * 60 + se
    if total >= 86400:                       # rejects exactly 24 h
        raise ValueError(text)
    return total
def m_no_limit(text):
    try:
        return correct(text)
    except ValueError:
        s = text.strip().lower()
        m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", s)
        if s and m:
            h, mi, se = (int(g) if g else 0 for g in m.groups())
            return h * 3600 + mi * 60 + se
        raise
def m_any_order(text):
    s = text.strip().lower()
    parts = re.findall(r"(\d+)([hms])", s)
    if not s or "".join(a + b for a, b in parts) != s:
        raise ValueError(text)
    mult = {"h": 3600, "m": 60, "s": 1}
    total = sum(int(a) * mult[b] for a, b in parts)
    if total > 86400:
        raise ValueError(text)
    return total
def m_empty_is_zero(text):
    if not text.strip():
        return 0
    return correct(text)
def m_minutes_as_seconds(text):
    s = text.strip().lower()
    m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", s)
    if not s or not m:
        raise ValueError(text)
    h, mi, se = (int(g) if g else 0 for g in m.groups())
    total = h * 3600 + mi + se              # forgot * 60
    if total > 86400:
        raise ValueError(text)
    return total
def m_bare_number(text):
    if text.strip().isdigit():
        return int(text.strip())            # accepts "90" as seconds
    return correct(text)

MUTANTS = [("no_strip", m_no_strip), ("no_case", m_no_case), ("limit_off_by_one", m_limit_off_by_one),
           ("no_limit", m_no_limit), ("any_order", m_any_order), ("empty_is_zero", m_empty_is_zero),
           ("minutes_as_seconds", m_minutes_as_seconds), ("bare_number", m_bare_number)]

def caught(impl):
    try:
        check(impl)
    except AssertionError:
        return True
    except Exception:
        return True                         # an unexpected exception also exposes the mutant
    return False

which = sys.stdin.read().split()
if not which:
    which = [name for name, _ in MUTANTS]
ok_on_correct = not caught(correct)
print("passes on the correct implementation:", ok_on_correct)
for name, impl in MUTANTS:
    if name in which:
        print(f"mutant {name}: {'killed' if caught(impl) else 'SURVIVED'}")
```

## Tests
=== sample
minutes_as_seconds empty_is_zero
---
passes on the correct implementation: True
mutant empty_is_zero: killed
mutant minutes_as_seconds: killed
=== hidden
no_strip no_case limit_off_by_one no_limit any_order empty_is_zero minutes_as_seconds bare_number
---
passes on the correct implementation: True
mutant no_strip: killed
mutant no_case: killed
mutant limit_off_by_one: killed
mutant no_limit: killed
mutant any_order: killed
mutant empty_is_zero: killed
mutant minutes_as_seconds: killed
mutant bare_number: killed

## Hints
- A correct test **must** pass on the correct implementation, so be careful: `pytest.raises` isn't available here, so write a small helper: `def raises(f, x): try: f(x) except ValueError: return True; return False`, then `assert raises(parse_duration, "")`.
- Boundaries: `"24h"` is allowed (86400), but `"24h0m1s"` and `"1440m1s"` aren't.
- Order: `"30m1h"` must be rejected. A correct parser doesn't accept units out of order.
- Don't forget: `" 3m "`, `"1H30M"`, `"90"` (no unit), and `"h"`.

## Solution
```python
def check(parse_duration):
    def raises(x):
        try:
            parse_duration(x)
        except ValueError:
            return True
        return False

    # happy paths and arithmetic of every unit
    assert parse_duration("1h30m") == 5400
    assert parse_duration("45s") == 45
    assert parse_duration("2h") == 7200
    assert parse_duration("1h0m5s") == 3605
    assert parse_duration("3m") == 180
    assert parse_duration("0s") == 0
    # whitespace and case
    assert parse_duration(" 3m ") == 180
    assert parse_duration("1H30M") == 5400
    # the 24 h boundary: exactly allowed, just above rejected
    assert parse_duration("24h") == 86400
    assert parse_duration("1440m") == 86400
    assert raises("24h0m1s")
    assert raises("86401s")
    # malformed inputs
    for bad in ["", "   ", "30m1h", "1h1h", "h", "90", "1.5h", "abc", "1d", "-5s", "1 h"]:
        assert raises(bad), bad
```

Each assertion targets a specific rule, and each mutant violates at least one of them:
- `" 3m "` kills **no_strip**, `"1H30M"` kills **no_case**, and `"24h" == 86400` kills **limit_off_by_one** (a classic off-by-one at a boundary).
- `"86401s"` raising kills **no_limit**, `"30m1h"` raising kills **any_order**, `""` raising kills **empty_is_zero**, `"3m" == 180` kills **minutes_as_seconds**, and `"90"` raising kills **bare_number**.

That's the idea behind **mutation testing** (tools like `mutmut` and `cosmic-ray` automate it): coverage only tells you lines were *executed*, while mutation testing tells you whether your tests would *notice* if those lines were wrong. Boundary values, invalid inputs and each documented rule are where weak tests let mutants survive.
