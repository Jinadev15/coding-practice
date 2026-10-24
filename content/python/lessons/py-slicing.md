# Slicing in Depth

Slicing extracts a sub-sequence with `seq[start:stop:step]`. It works on every sequence type: lists, strings, tuples, ranges and bytes. It's the source of some of Python's most elegant one-liners (`s[::-1]`) and of a lot of off-by-one confusion. This lesson gives you a model that makes every slice predictable, including negative steps, which is where most people start guessing.

## 1. The syntax and the half-open rule

> [!SYNTAX]
> `seq[start:stop:step]`. All three parts are optional.
> - `start`: first index **included** (default: the beginning)
> - `stop`: first index **excluded** (default: past the end)
> - `step`: the stride (default `1`; may be negative; must not be `0`)

The key model: **indices point *between* elements**.

<div class="figure">
<svg viewBox="0 0 600 170" width="600" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="15">
  <g fill="none" stroke="currentColor" stroke-opacity=".6">
    <rect x="60" y="55" width="70" height="44"/><rect x="130" y="55" width="70" height="44"/><rect x="200" y="55" width="70" height="44"/>
    <rect x="270" y="55" width="70" height="44"/><rect x="340" y="55" width="70" height="44"/><rect x="410" y="55" width="70" height="44"/>
  </g>
  <g fill="currentColor" font-size="20"><text x="88" y="84">P</text><text x="158" y="84">y</text><text x="230" y="84">t</text><text x="298" y="84">h</text><text x="368" y="84">o</text><text x="438" y="84">n</text></g>
  <g fill="#2f81f7" font-size="13"><text x="56" y="45">0</text><text x="126" y="45">1</text><text x="196" y="45">2</text><text x="266" y="45">3</text><text x="336" y="45">4</text><text x="406" y="45">5</text><text x="476" y="45">6</text></g>
  <g fill="#d29922" font-size="13"><text x="50" y="120">-6</text><text x="120" y="120">-5</text><text x="190" y="120">-4</text><text x="260" y="120">-3</text><text x="330" y="120">-2</text><text x="400" y="120">-1</text></g>
  <path d="M130 140 L130 150 L270 150 L270 140" fill="none" stroke="#3fb950" stroke-width="2"/>
  <text x="155" y="168" fill="#3fb950" font-size="13">s[1:3] = "yt"</text>
</svg>
<figcaption>Think of the positive indices as labels on the gaps between characters. <code>s[1:3]</code> takes everything between gap 1 and gap 3.</figcaption>
</div>

From this model:

- `len(s[a:b]) == b - a` (for `0 ≤ a ≤ b ≤ len(s)`)
- `s[:k] + s[k:] == s` for **any** `k`. Splitting never loses or duplicates an element.
- `s[:k]` is the first `k` elements and `s[-k:]` is the last `k`.

```python
a = list(range(10))     # [0, 1, ..., 9]
print(a[2:7])           # [2, 3, 4, 5, 6]
print(a[:3], a[7:])     # [0, 1, 2] [7, 8, 9]
print(a[-3:])           # [7, 8, 9]   last three
print(a[:-3])           # [0, ..., 6] all but the last three
print(a[1:-1])          # drop the first and last
```

## 2. Slices never raise `IndexError`

Out-of-range bounds are **clipped** to the sequence:

```python
a = [0, 1, 2]
print(a[1:100])     # [1, 2]
print(a[100:])      # []
print(a[-100:2])    # [0, 1]
print("abc"[5:])    # ''
```

Indexing `a[100]` raises `IndexError`; slicing `a[100:]` gives an empty result. That makes slices handy for "take up to the first k items" without checking the length first.

## 3. Step

```python
a = list(range(10))
print(a[::2])       # [0, 2, 4, 6, 8]   every second
print(a[1::2])      # [1, 3, 5, 7, 9]   odd positions
print(a[2:8:3])     # [2, 5]
```

## 4. Negative step: walking backwards

With a negative step, the slice walks **from `start` down toward `stop`**, still excluding `stop`. The defaults flip too: the default `start` becomes the **last** element and the default `stop` becomes "before the first".

```python
a = list(range(10))
print(a[::-1])        # [9, 8, ..., 0]   reversed copy
print(a[7:2:-1])      # [7, 6, 5, 4, 3]  from 7 down to (but excluding) 2
print(a[-1:-4:-1])    # [9, 8, 7]        last three, reversed
print(a[::-2])        # [9, 7, 5, 3, 1]
print(a[2:7:-1])      # []               can't walk DOWN from 2 to 7
```

> [!KEY]
> Rule for any slice: start at `start` and keep adding `step` while you haven't reached or passed `stop`. If the first step already moves away from `stop`, the result is empty. `a[2:7:-1]` is empty because walking down from 2 never reaches 7.

| Slice | Meaning |
|---|---|
| `s[::-1]` | reversed copy |
| `s[-1]` | last element (indexing, not a slice) |
| `s[-k:]` | last k elements |
| `s[:-k]` | all but the last k |
| `s[k:]` | all but the first k |
| `s[::k]` | every k-th element |
| `s[i:j][::-1]` | elements i..j−1 reversed (clearer than one combined slice) |

## 5. Slices make copies (shallow)

Slicing a list creates a **new list** containing references to the same elements:

```python
a = [1, 2, 3]
b = a[:]             # a full-slice copy (the same as a.copy() or list(a))
b.append(4)
print(a, b)          # [1, 2, 3] [1, 2, 3, 4]
print(a[:] is a)     # False
```

It's a **shallow** copy: nested lists inside are still shared (next-but-one lesson). For strings and tuples a slice also builds a new object. Since they're immutable, you can't tell, except for the cost: slicing is **O(k)** in the length of the result.

> [!WARNING]
> In a loop, `s[1:]` or `a[i:]` copies every time. `while s: s = s[1:]` is O(n²). Move an index instead.

## 6. Slice assignment (lists only)

Assigning to a slice **replaces** that region, and the replacement can have a different length:

```python
b = [1, 2, 3, 4, 5]
b[1:3] = ["x"]        # replace two elements with one → [1, 'x', 4, 5]
b[1:1] = [9, 9]       # empty slice = insertion       → [1, 9, 9, 'x', 4, 5]
b[:] = []             # clear in place (the same list object)
```

With a step (an *extended* slice), the lengths must match exactly:

```python
c = [1, 2, 3, 4, 5]
c[::2] = [0, 0, 0]    # [0, 2, 0, 4, 0]
# c[::2] = [7]        → ValueError: attempt to assign sequence of size 1 to extended slice of size 3
```

Slice deletion:

```python
c = [1, 2, 3, 4, 5]
del c[::2]            # [2, 4]
del c[:]              # empty it
```

> [!KEY]
> `nums[:] = new_values` **mutates** the existing list (everyone holding a reference sees the change). `nums = new_values` just rebinds the local name. In-place problems sometimes need the former.

## 7. `slice` objects

`a[1:8:3]` is really `a[slice(1, 8, 3)]`. You can name slices for readability, which helps with fixed-width records:

```python
record = "2026-10-24 ERROR disk full"
DATE, LEVEL, MSG = slice(0, 10), slice(11, 16), slice(17, None)
print(record[DATE], record[LEVEL], record[MSG])   # 2026-10-24 ERROR disk full
print(slice(1, 8, 3).indices(10))                 # (1, 8, 3): bounds clipped to a length
```

## 8. Slicing 2D lists

Slicing a list of lists slices the **outer** list (rows). For columns, use a comprehension:

```python
m = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]
print(m[1:])                      # rows 1..: [[4, 5, 6], [7, 8, 9]]
print([row[1:] for row in m])     # drop the first column
print([row[0] for row in m])      # column 0: [1, 4, 7]
```

NumPy arrays support real 2D slicing (`m[:, 1:]`), which you'll meet in the Scientific Stack module.

## 9. Exam-ready answers

> [!EXAM]
> **Slicing.** The expression `s[start:stop:step]` returns a new sequence of the same type containing the elements from index `start` up to but not including `stop`, taking every `step`-th element. Omitted values default to the beginning, the end and a step of 1. Negative indices count from the end, and a negative step traverses the sequence in reverse (in which case the defaults for `start` and `stop` are swapped). Slice bounds outside the sequence are clipped rather than raising `IndexError`. Slicing a list produces a shallow copy, and assigning to a slice of a list replaces that portion, possibly with a different number of elements.

## 10. Cheat sheet

| Goal | Slice |
|---|---|
| copy | `a[:]` |
| reverse | `a[::-1]` |
| first k | `a[:k]` |
| last k | `a[-k:]` |
| drop first / last | `a[1:]`, `a[:-1]` |
| middle without ends | `a[1:-1]` |
| even / odd positions | `a[::2]`, `a[1::2]` |
| insert at i | `a[i:i] = [x, y]` |
| replace in place | `a[:] = new` |
| rotate right by k | `a[-k:] + a[:-k]` (with `k %= n`, `k > 0`) |

> [!INTERVIEW]
> **"Is `a[-0:]` the last zero elements?"** No. `-0 == 0`, so `a[-0:]` is `a[0:]`, the **whole** list. This bites rotation code: `a[-k:] + a[:-k]` with `k = 0` gives `a + []`, which happens to be correct, but `a[-k:]` meant as "last k" returns everything when k is 0. Handle `k == 0` explicitly.
