# String Basics

Text is the most common data you'll process: input lines, file contents, identifiers, JSON, logs. Python's `str` is an **immutable sequence of Unicode characters**. That one sentence explains most of how strings behave. This lesson covers how to write string literals, index into them, combine and compare them, and why you can't change one in place. String *methods* (`split`, `join`, `strip`…) and encodings have their own lesson later.

## 1. Writing string literals

```python
a = 'single quotes'
b = "double quotes"          # identical to single; pick one style and be consistent
c = "it's easy"              # use the other quote type to avoid escaping
d = 'say "hi"'
e = """triple quotes
can span
multiple lines"""
```

Single and double quotes are **completely equivalent** in Python (unlike C, where `'a'` is a `char` and `"a"` is a string). There is **no separate character type**: a "character" is just a string of length 1.

### Escape sequences

A backslash inside a normal string starts an **escape sequence**:

| Escape | Meaning | Escape | Meaning |
|---|---|---|---|
| `\n` | newline | `\\` | a literal backslash |
| `\t` | tab | `\'` `\"` | quote characters |
| `\r` | carriage return | `\u00e9` | Unicode code point (é) |
| `\0` | null character | `\x41` | byte/char by hex (A) |

```python
print("col1\tcol2\nrow2")
print(len("a\nb"))     # 3: \n is ONE character
```

### Raw strings

Prefix `r` turns off escape processing. That's essential for **regular expressions** and **Windows paths**:

```python
print(len(r"a\nb"))         # 4: backslash and n are two separate characters
path = r"C:\new\table"      # without r, \n and \t would become newline and tab
```

> [!WARNING]
> A raw string still cannot end with an odd number of backslashes: `r"C:\"` is a syntax error, because `\"` still prevents the quote from closing the string.

### Adjacent literal concatenation

String literals written next to each other are joined **at compile time**:

```python
msg = ("This is a long message "
       "split across lines.")
```

## 2. Strings are sequences: indexing

Each character has a position. Python supports **zero-based** positive indices and **negative** indices that count from the end.

<div class="figure">
<svg viewBox="0 0 520 150" width="520" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="15">
  <g fill="none" stroke="currentColor" stroke-opacity=".6">
    <rect x="60" y="50" width="60" height="44"/><rect x="120" y="50" width="60" height="44"/><rect x="180" y="50" width="60" height="44"/>
    <rect x="240" y="50" width="60" height="44"/><rect x="300" y="50" width="60" height="44"/><rect x="360" y="50" width="60" height="44"/>
  </g>
  <g fill="currentColor" font-size="20">
    <text x="82" y="79">P</text><text x="142" y="79">y</text><text x="203" y="79">t</text><text x="262" y="79">h</text><text x="322" y="79">o</text><text x="382" y="79">n</text>
  </g>
  <g fill="#2f81f7" font-size="13">
    <text x="85" y="40">0</text><text x="145" y="40">1</text><text x="205" y="40">2</text><text x="265" y="40">3</text><text x="325" y="40">4</text><text x="385" y="40">5</text>
  </g>
  <g fill="#d29922" font-size="13">
    <text x="80" y="115">-6</text><text x="140" y="115">-5</text><text x="200" y="115">-4</text><text x="260" y="115">-3</text><text x="320" y="115">-2</text><text x="380" y="115">-1</text>
  </g>
  <text x="430" y="40" fill="#2f81f7" font-family="sans-serif" font-size="12">positive</text>
  <text x="430" y="115" fill="#d29922" font-family="sans-serif" font-size="12">negative</text>
</svg>
<figcaption><code>s = "Python"</code>. For any valid index, <code>s[-k] == s[len(s) - k]</code>.</figcaption>
</div>

```python
s = "Python"
print(s[0], s[5], s[-1], s[-6])   # P n n P
print(len(s))                     # 6
# s[6]   → IndexError: string index out of range
```

> [!KEY]
> Valid indices are `0 … len(s)-1` and `-len(s) … -1`. The last character is `s[-1]` (or `s[len(s)-1]`). Indexing past the end raises `IndexError`.

### A first look at slicing

`s[start:stop]` gives the characters from `start` up to **but not including** `stop`. Out-of-range slice bounds are clipped, never an error. (The Slicing lesson covers steps and edge cases in depth.)

```python
s = "Python"
print(s[1:4])    # yth    indices 1, 2, 3
print(s[:2])     # Py     from the start
print(s[2:])     # thon   to the end
print(s[::-1])   # nohtyP reversed (step -1)
print(s[2:100])  # thon   no error
```

## 3. Strings are immutable

You cannot change a string in place. Every "modification" builds a **new** string.

```python
s = "hello"
# s[0] = "H"        → TypeError: 'str' object does not support item assignment
s = "H" + s[1:]     # new string "Hello", s rebound to it
upper = s.upper()   # methods also return NEW strings
print(s, upper)     # Hello HELLO
```

Why immutable? Strings can be **dictionary keys** (keys must be hashable, so their value can't change), can be safely shared between names, and can be cached and interned.

> [!DANGER]
> Calling a method and ignoring its result does nothing: `s.upper()` on its own line leaves `s` unchanged. Write `s = s.upper()`.

## 4. Operators on strings

| Operation | Example | Result |
|---|---|---|
| Concatenation `+` | `"ab" + "cd"` | `"abcd"` |
| Repetition `*` | `"ab" * 3` | `"ababab"` (`* 0` gives `""`) |
| Membership `in` | `"th" in "Python"` | `True` (substring test) |
| Length | `len("héllo")` | `5` (characters, not bytes) |
| Comparison | `"apple" < "apricot"` | `True` (lexicographic) |

`+` only joins strings with strings: `"Age: " + 21` raises `TypeError`. Convert first with `"Age: " + str(21)`, or better, use an f-string: `f"Age: {21}"`.

### How string comparison works

Strings compare **lexicographically by Unicode code point**, character by character, like a dictionary but with code-point order:

```python
print(ord("A"), ord("Z"), ord("a"))   # 65 90 97
print("Z" < "a")       # True: every uppercase ASCII letter sorts before lowercase
print("abc" < "abcd")  # True: a proper prefix sorts first
print("10" < "9")      # True!  '1' (49) < '9' (57). Strings are not numbers
```

> [!DANGER]
> Sorting numeric strings sorts them as text: `sorted(["10", "9", "100"])` gives `['10', '100', '9']`. Convert to `int` first.

### `ord()` and `chr()`

`ord(ch)` gives a character's code point; `chr(n)` goes back. Together they make character arithmetic possible:

```python
print(ord("a"), chr(98))                      # 97 b
print(chr(ord("a") + 2))                      # c
offset = ord("e") - ord("a")                  # 4: position in the alphabet
```

## 5. Iterating over a string

A `for` loop visits each character:

```python
for ch in "hey":
    print(ch, ord(ch))
```

```output
h 104
e 101
y 121
```

Counting with a loop, for example the vowels:

```python
text = "Programming in Python"
count = 0
for ch in text.lower():
    if ch in "aeiou":
        count += 1
print(count)      # 5
```

## 6. Unicode in one paragraph

A Python 3 `str` holds **Unicode code points**, not bytes. `len("héllo") == 5` and `len("🙂") == 1`. Converting to bytes for files or networks is called **encoding** (usually UTF-8), and the Strings Advanced lesson covers it. In C, a string is an array of bytes ending in `'\0'`, and `strlen("é")` is 2 in UTF-8. Python hides that layer from you.

## 7. `str()` vs `repr()`

- `str(x)` is the human-readable form (what `print` shows).
- `repr(x)` is the unambiguous, developer form. For strings it includes the quotes and escapes.

```python
s = "hi\n"
print(str(s))     # hi (plus a newline)
print(repr(s))    # 'hi\n'
```

The REPL echoes values with `repr`, which is why you see quotes there.

## 8. Exam-ready answers

> [!EXAM]
> **Strings in Python.** A string (`str`) is an immutable, ordered sequence of Unicode characters. Literals may use single, double or triple quotes; triple-quoted strings can span lines, and a raw-string prefix `r` disables escape sequences. Strings support zero-based indexing, negative indexing from the end, slicing `s[start:stop:step]`, concatenation with `+`, repetition with `*`, membership tests with `in`, and lexicographic comparison by Unicode code point. Because strings are immutable, operations such as `upper()` or concatenation return new string objects, and strings are hashable, so they can be used as dictionary keys.

> [!EXAM]
> **Why are strings immutable?** Immutability makes strings hashable, so they can be dictionary keys and set elements, and makes it safe for several references to share one string object. It also enables optimisations such as interning and caching hash values. The cost is that building a string piece by piece with `+=` in a loop can create many temporary objects. `''.join(parts)` is the efficient alternative.

## 9. Cheat sheet

| Task | Code |
|---|---|
| first / last char | `s[0]`, `s[-1]` |
| reverse | `s[::-1]` |
| is palindrome | `s == s[::-1]` |
| substring test | `"sub" in s` |
| repeat | `"-" * 20` |
| char ↔ code | `ord("a")`, `chr(97)` |
| alphabet position | `ord(ch) - ord("a")` |
| number → text | `str(42)` |
| text → number | `int("42")`, `float("2.5")` |
| debug-print with quotes | `repr(s)` or `print(f"{s!r}")` |

> [!INTERVIEW]
> **"Why is `s += ch` in a loop potentially O(n²)?"** Each `+=` must create a new string and copy everything so far. CPython has an optimisation that sometimes resizes in place when no other reference exists, but it isn't guaranteed (other implementations such as PyPy don't do it). The portable linear-time idiom is to collect pieces in a list and `''.join(pieces)` once.
