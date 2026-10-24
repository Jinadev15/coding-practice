---
id: py-shipping-cost
title: Shipping Cost
difficulty: Medium
order: 2
tags: piecewise logic, boundaries, guard clauses
---
## Statement
A courier computes the cost of a parcel from its weight `w` (kg, integer) and destination zone (`local`, `national` or `international`):

| Weight | Base cost |
|---|---|
| `w ≤ 0` | invalid |
| `1 ≤ w ≤ 2` | 50 |
| `3 ≤ w ≤ 10` | 50 + 20 per kg above 2 |
| `w > 10` | 210 + 15 per kg above 10 |

Zone multiplier: `local` ×1, `national` ×2, `international` ×5. Any other zone is invalid.

**Express** is an extra flag (`yes`/`no`). It adds a flat 100 **after** the multiplier, but it isn't allowed for `international` (invalid).

Each of `t` lines has `w zone express`. Print the integer cost or `invalid`.

## Starter
```python
def shipping_cost(w, zone, express):
    # return an int, or the string "invalid"
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    w, zone, express = input().split()
    print(shipping_cost(int(w), zone, express))
```

## Tests
=== sample
4
1 local no
5 national no
12 local yes
3 international yes
---
50
220
340
invalid
=== hidden
6
0 local no
-4 national no
2 local no
3 local no
10 local no
11 local no
---
invalid
invalid
50
70
210
225
=== hidden
4
2 international no
7 moon no
10 national yes
100 international no
---
250
invalid
520
7800
=== hidden
2
1 local yes
2 national yes
---
150
200

## Hints
- Reject invalid input first with guard clauses: bad weight, unknown zone, express with international.
- A dict maps zone to multiplier and doubles as the validity check: `zone not in MULT`.
- Check the boundaries: 2 → 50, 3 → 70, 10 → 210, 11 → 225.

## Solution
Guard clauses reject every invalid case up front. Then the base cost is a piecewise function, the multiplier comes from a dict, and the express surcharge is added last.

```python
MULT = {"local": 1, "national": 2, "international": 5}

def shipping_cost(w, zone, express):
    if w <= 0 or zone not in MULT:
        return "invalid"
    if express == "yes" and zone == "international":
        return "invalid"
    if w <= 2:
        base = 50
    elif w <= 10:
        base = 50 + 20 * (w - 2)
    else:
        base = 210 + 15 * (w - 10)
    cost = base * MULT[zone]
    if express == "yes":
        cost += 100
    return cost
```

The tiers line up: at `w = 10` the middle formula gives 50 + 160 = 210, which is exactly where the third tier starts, so the function is continuous at the boundary. Checking that kind of consistency catches typos in the rules.
