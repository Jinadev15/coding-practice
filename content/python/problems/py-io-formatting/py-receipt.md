---
id: py-receipt
title: Receipt Printer
difficulty: Medium
order: 3
tags: f-strings, alignment, tables
---
## Statement
Print a shop receipt. The first line has `n`. Each of the next `n` lines has an item: `name quantity unit_price` (the name has no spaces; the price has at most 2 decimals).

Print exactly this layout, 30 characters wide:

- Each item line: the name **left-aligned in 14 columns**, the quantity **right-aligned in 4**, then the line total (`quantity × price`) **right-aligned in 12 with 2 decimals**.
- Then a line of 30 `-` characters.
- Then `TOTAL` left-aligned in 18 columns followed by the grand total right-aligned in 12 with 2 decimals **and comma separators**.

```text
apple            3        1.50
bread            1       40.00
------------------------------
TOTAL                    41.50
```

Names longer than 14 characters are printed in full; widths are minimums.

## Starter
```python
n = int(input())
total = 0.0
for _ in range(n):
    name, qty, price = input().split()
```

## Tests
=== sample
2
apple 3 0.50
bread 1 40
---
apple            3        1.50
bread            1       40.00
------------------------------
TOTAL                    41.50
=== sample
1
laptop 2 54999.99
---
laptop           2   109999.98
------------------------------
TOTAL               109,999.98
=== hidden
3
pen 10 5
notebook 4 45.25
eraser 1 3
---
pen             10       50.00
notebook         4      181.00
eraser           1        3.00
------------------------------
TOTAL                   234.00
=== hidden
1
x 0 99
---
x                0        0.00
------------------------------
TOTAL                     0.00
=== hidden
2
gold 3 1000000
silver 1 0.01
---
gold             3  3000000.00
silver           1        0.01
------------------------------
TOTAL             3,000,000.01

## Hints
- Item line spec: `f"{name:<14}{qty:>4}{line_total:>12.2f}"`.
- The total line: `f"{'TOTAL':<18}{total:>12,.2f}"`. The grouping `,` comes **before** `.2f`.
- For money in real code you'd use integer cents. Here floats with `.2f` rounding are fine because the inputs have only 2 decimals.

## Solution
Each line is built from fixed-width fields. Note the order in `>12,.2f`: align and width, then grouping, then precision and type, exactly as in the mini-language grammar.

```python
n = int(input())
total = 0.0
for _ in range(n):
    name, qty, price = input().split()
    qty = int(qty)
    line_total = qty * float(price)
    total += line_total
    print(f"{name:<14}{qty:>4}{line_total:>12.2f}")
print("-" * 30)
print(f"{'TOTAL':<18}{total:>12,.2f}")
```

Item lines deliberately have **no** grouping separator while the total line has one. Reading the spec carefully is half of every formatting problem.
