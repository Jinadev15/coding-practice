---
id: py-hello-judge
title: Hello, Judge
difficulty: Easy
order: 1
tags: stdout, basics
---
## Statement
Write a program that prints exactly two lines:

```text
Hello, Judge!
Python runs on a virtual machine.
```

There is no input. Spelling, capitalisation and punctuation must match exactly. This problem exists so you see how a judge compares output character by character.

## Starter
```python
# Print the two required lines.
```

## Tests
=== sample

---
Hello, Judge!
Python runs on a virtual machine.

## Solution
Each `print()` call writes its arguments followed by a newline (`end="\n"` by default), so two calls give two lines.

```python
print("Hello, Judge!")
print("Python runs on a virtual machine.")
```

**Common failure:** writing `Hello Judge!` (missing comma) or `hello, judge!`. The judge compares text exactly, apart from trailing whitespace.
