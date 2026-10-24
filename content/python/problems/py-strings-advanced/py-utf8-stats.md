---
id: py-utf8-stats
title: UTF-8 Byte Counter
difficulty: Medium
order: 3
tags: unicode, encode, bytes
---
## Statement
For each input line (read until the end of input), print three numbers:

1. the number of **characters** (code points)
2. the number of **bytes** in its UTF-8 encoding
3. the number of characters that are **not ASCII** (code point > 127)

Then print a final line `total B` with the total byte count of all the lines (not counting newlines).

## Starter
```python
import sys
for line in sys.stdin.read().splitlines():
    pass
```

## Tests
=== sample
hello
héllo
€5
🙂ok
---
5 5 0
5 6 1
2 4 1
3 6 1
total 21
=== hidden
naïve café
---
10 12 2
total 12
=== hidden

---
0 0 0
total 0

## Hints
- `len(line.encode("utf-8"))` gives the byte count.
- `ord(ch) > 127` identifies non-ASCII characters.
- UTF-8 lengths: up to U+007F → 1 byte, up to U+07FF → 2, up to U+FFFF → 3, beyond that → 4.

## Solution
Encoding gives the byte length directly, and `ord` classifies each character.

```python
import sys
total = 0
for line in sys.stdin.read().splitlines():
    nbytes = len(line.encode("utf-8"))
    non_ascii = sum(1 for ch in line if ord(ch) > 127)
    print(len(line), nbytes, non_ascii)
    total += nbytes
print("total", total)
```

Try computing the byte count **without** `encode`, using the code-point ranges in the hints. That's exactly what a C implementation of UTF-8 does, and it shows why `€` (U+20AC) needs 3 bytes and `🙂` (U+1F642) needs 4.
