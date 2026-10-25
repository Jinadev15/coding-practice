---
id: py-number-formats
title: Number Formats
difficulty: Easy
order: 1
tags: f-strings, format spec
---
## Statement
Read a non-negative integer `n`. Print it in four formats, one per line:

1. with comma thousands separators, e.g. `1,234,567`
2. in binary, without a prefix
3. in **uppercase** hexadecimal, with a lowercase `0x` prefix, e.g. `0xFF`
4. zero-padded to a width of 10 digits (wider numbers are printed in full)

Use format specs, not manual string building.

## Starter
```python
n = int(input())
```

## Tests
=== sample
255
---
255
11111111
0xFF
0000000255
=== sample
1234567
---
1,234,567
100101101011010000111
0x12D687
0001234567
=== hidden
0
---
0
0
0x0
0000000000
=== hidden
98765432109876
---
98,765,432,109,876
10110011101001110011110011111110011101100110100
0x59D39E7F3B34
98765432109876

## Hints
- Format specs go after a colon inside an f-string: `f"{n:,}"` adds thousands separators.
- `b` is binary, `X` is uppercase hexadecimal: `f"{n:b}"`, `f"0x{n:X}"`.
- `f"{n:010d}"` means: pad with zeros to width 10. Numbers wider than 10 digits are printed in full automatically.

## Solution
Each line is one format spec: `,` for grouping, `b` for binary, `X` for uppercase hex (the `0x` is plain text, because `#X` would give `0X`), and `010d` for zero-padding to width 10.

```python
n = int(input())
print(f"{n:,}")
print(f"{n:b}")
print(f"0x{n:X}")
print(f"{n:010d}")
```

Width is a **minimum**, so the 14-digit number in the last test prints unpadded and untruncated.
