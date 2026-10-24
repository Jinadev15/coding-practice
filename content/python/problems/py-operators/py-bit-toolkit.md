---
id: py-bit-toolkit
title: Bit Toolkit
difficulty: Medium
order: 2
tags: bit manipulation, masks, shifts
---
## Statement
Start with a non-negative integer `x`. Then process `q` commands, each on its own line:

| Command | Action | Output |
|---|---|---|
| `get k` | — | `1` if bit `k` of x is set, else `0` |
| `set k` | turn bit `k` on | — |
| `clear k` | turn bit `k` off | — |
| `toggle k` | flip bit `k` | — |
| `count` | — | the number of set bits in x |
| `lowest` | — | the value of the lowest set bit of x (e.g. 12 → 4), or 0 if x is 0 |
| `pow2` | — | `YES` if x is a power of two, else `NO` |
| `show` | — | x in decimal, then a space, then x in binary (no prefix) |

Bit 0 is the least significant bit. `0 ≤ k ≤ 100`, so x can grow beyond 64 bits. Python handles that natively.

Input: first line `x`, second line `q`, then `q` commands.

## Starter
```python
x = int(input())
q = int(input())
for _ in range(q):
    parts = input().split()
```

## Tests
=== sample
12
6
show
get 2
get 0
count
lowest
pow2
---
12 1100
1
0
2
4
NO
=== sample
0
5
set 3
show
pow2
toggle 3
lowest
---
8 1000
YES
0
=== hidden
255
5
clear 0
clear 7
show
toggle 0
count
---
126 1111110
7
=== hidden
1
4
set 100
count
pow2
get 100
---
2
NO
1
=== hidden
6
6
clear 5
show
toggle 1
show
pow2
lowest
---
6 110
4 100
YES
4
=== hidden
0
2
pow2
count
---
NO
0

## Hints
- `(x >> k) & 1` reads a bit. `1 << k` builds a mask with only bit k set.
- Set `x |= mask`, clear `x &= ~mask`, toggle `x ^= mask`.
- `x & -x` isolates the lowest set bit. `x & (x - 1) == 0` tests powers of two, but remember that 0 is **not** a power of two.

## Solution
Each command is one standard bit idiom from the lesson.

```python
x = int(input())
q = int(input())
for _ in range(q):
    parts = input().split()
    cmd = parts[0]
    if cmd == "get":
        print((x >> int(parts[1])) & 1)
    elif cmd == "set":
        x |= 1 << int(parts[1])
    elif cmd == "clear":
        x &= ~(1 << int(parts[1]))
    elif cmd == "toggle":
        x ^= 1 << int(parts[1])
    elif cmd == "count":
        print(bin(x).count("1"))
    elif cmd == "lowest":
        print(x & -x)
    elif cmd == "pow2":
        print("YES" if x > 0 and x & (x - 1) == 0 else "NO")
    elif cmd == "show":
        print(x, f"{x:b}")
```

`x & (x - 1)` removes the lowest set bit. A power of two has exactly one set bit, so the result is 0. Without the `x > 0` guard, 0 would wrongly pass, and the last hidden test checks that edge case. `int.bit_count()` (Python 3.10+) is a faster popcount than `bin(x).count("1")`.
