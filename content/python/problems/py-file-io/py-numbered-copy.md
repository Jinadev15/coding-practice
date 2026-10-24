---
id: py-numbered-copy
title: Numbered Copy
difficulty: Easy
order: 1
tags: files, read, write, encoding
---
## Statement
Write `numbered_copy(src, dst)`: read the text file `src` (UTF-8) and write `dst` with every line prefixed by its 1-based line number, a colon and a space. **Blank lines are skipped and don't get a number.** Return the number of lines written.

The driver writes the stdin text to `in.txt`, calls your function, then prints the returned count and the exact contents of `out.txt`.

## Starter
```python
def numbered_copy(src, dst):
    pass
```

## Driver
```python
import sys
with open("in.txt", "w", encoding="utf-8") as f:
    f.write(sys.stdin.read())
n = numbered_copy("in.txt", "out.txt")
print(n)
with open("out.txt", encoding="utf-8") as f:
    print(f.read(), end="")
```

## Tests
=== sample
alpha
beta

gamma
---
3
1: alpha
2: beta
3: gamma
=== hidden
héllo wörld
---
1
1: héllo wörld
=== hidden


---
0

## Hints
- Stream with `for line in fin:` and `line.rstrip("\n")`.
- Open both files in one `with`: `with open(src, encoding="utf-8") as fin, open(dst, "w", encoding="utf-8") as fout:`.

## Solution
```python
def numbered_copy(src, dst):
    count = 0
    with open(src, encoding="utf-8") as fin, open(dst, "w", encoding="utf-8") as fout:
        for line in fin:
            text = line.rstrip("\n")
            if not text.strip():
                continue
            count += 1
            fout.write(f"{count}: {text}\n")
    return count
```

Both files close automatically, in reverse order, when the `with` block ends. That also flushes `out.txt` before the driver reads it. Without `encoding="utf-8"` the accented test could fail on a system with a different default encoding.
