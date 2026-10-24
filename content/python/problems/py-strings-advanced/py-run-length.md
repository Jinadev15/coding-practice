---
id: py-run-length
title: Run-Length Encoding
difficulty: Medium
order: 1
tags: strings, encoding, parsing
---
## Statement
**Run-length encoding** compresses runs of a repeated character: `"aaabccdddd"` → `"a3b1c2d4"`.

Each input line is a command:

- `E text`: print the encoding of `text` (letters only, non-empty)
- `D code`: print the decoding of `code`. Counts may have **several digits**: `"a12b1"` is twelve `a`s and then `b`.

First line `t`, then `t` commands.

## Starter
```python
def encode(s):
    pass

def decode(code):
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    cmd, arg = input().split()
    print(encode(arg) if cmd == "E" else decode(arg))
```

## Tests
=== sample
3
E aaabccdddd
D a3b1c2d4
E z
---
a3b1c2d4
aaabccdddd
z1
=== hidden
3
E aaaaaaaaaaaa
D a12b1
D x10y2
---
a12
aaaaaaaaaaaab
xxxxxxxxxxyy
=== hidden
2
E abab
E AAaa
---
a1b1a1b1
A2a2

## Hints
- Encode: walk the string, extending the current run while the character repeats; when it changes, emit `char + str(count)`.
- Decode: read a letter, then collect **all** the following digits into the count (`ch.isdigit()`).
- Build the output with a list and `"".join(...)`.

## Solution
Encoding scans runs. Decoding alternates between reading one letter and reading a multi-digit number. Collecting digits until a non-digit is how every number tokenizer works.

```python
def encode(s):
    out = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(f"{s[i]}{j - i}")
        i = j
    return "".join(out)

def decode(code):
    out = []
    i = 0
    while i < len(code):
        ch = code[i]
        i += 1
        j = i
        while j < len(code) and code[j].isdigit():
            j += 1
        out.append(ch * int(code[i:j]))
        i = j
    return "".join(out)
```

Both run in O(n) over the input or output length. `itertools.groupby` turns the encoder into a one-liner (`"".join(f"{k}{len(list(g))}" for k, g in groupby(s))`), which you'll meet in the itertools topic. The single-digit-count assumption is the classic bug, and the `a12b1` test catches it.
