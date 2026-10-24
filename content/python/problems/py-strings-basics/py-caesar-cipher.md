---
id: py-caesar-cipher
title: Caesar Cipher
difficulty: Medium
order: 3
tags: ord, chr, modulo
---
## Statement
Encrypt a message with a Caesar cipher: shift every **letter** forward in the alphabet by `k` positions, wrapping around from `z` to `a`. Preserve case. Leave every non-letter (digits, spaces, punctuation) unchanged.

Input: first line `k` (it may be negative or larger than 26, e.g. `-3` or `100`), second line the message.

```text
k = 3:  "Hello, World!"  →  "Khoor, Zruog!"
```

## Starter
```python
k = int(input())
msg = input()
```

## Tests
=== sample
3
Hello, World!
---
Khoor, Zruog!
=== sample
-1
abc XYZ
---
zab WXY
=== hidden
26
Python 3.14
---
Python 3.14
=== hidden
100
xyz
---
tuv
=== hidden
-27
Aa Zz!
---
Zz Yy!
=== hidden
13
Why did the chicken cross the road?
---
Jul qvq gur puvpxra pebff gur ebnq?

## Hints
- Convert a lowercase letter to a position 0–25 with `ord(ch) - ord('a')`.
- Shift and wrap: `(pos + k) % 26`. Python's `%` already returns 0–25 for negative `k`.
- Convert back with `chr(new_pos + ord('a'))`. Do the same with `'A'` for uppercase.

## Solution
Map each letter to 0–25, add `k`, reduce modulo 26 and map back. Python's `%` always gives a result in `[0, 26)` for a positive divisor, so negative shifts work with no special case. In C you'd need `((pos + k) % 26 + 26) % 26`.

```python
k = int(input())
msg = input()
out = []
for ch in msg:
    if "a" <= ch <= "z":
        out.append(chr((ord(ch) - ord("a") + k) % 26 + ord("a")))
    elif "A" <= ch <= "Z":
        out.append(chr((ord(ch) - ord("A") + k) % 26 + ord("A")))
    else:
        out.append(ch)
print("".join(out))
```

We build a list and `join` once instead of `+=` on a string. That's the linear-time idiom from the lesson. The shift-13 test is **ROT13**, which is its own inverse.
