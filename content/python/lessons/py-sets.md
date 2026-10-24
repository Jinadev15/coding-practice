# Sets and Frozensets

A set is an **unordered collection of unique, hashable elements**. Think of it as a dictionary with keys but no values. That gives you two superpowers: **O(1) membership tests** and **mathematical set algebra** (union, intersection, difference). Whenever an algorithm asks "have I seen this before?", "is this allowed?" or "what do these two collections have in common?", the answer is usually a set.

## 1. Creating sets

```python
primes = {2, 3, 5, 7}
empty = set()                  # NOT {} — that's an empty dict
letters = set("hello")         # {'h', 'e', 'l', 'o'}: duplicates removed
nums = set([3, 1, 3, 2])       # {1, 2, 3}
evens = {x for x in range(10) if x % 2 == 0}   # set comprehension
```

> [!DANGER]
> `{}` is an empty **dict**. The only way to write an empty set is `set()`.

Sets are **unordered**: there's no index (`s[0]` is a `TypeError`), and the iteration order is arbitrary. Never rely on it. For a deterministic order, use `sorted(s)`.

## 2. Elements must be hashable

A set is a hash table of its elements (like a dict's keys), so elements must be hashable:

```python
ok = {1, "a", (1, 2), frozenset({3})}
# bad = {[1, 2]}     → TypeError: cannot use 'list' as a set element (unhashable type: 'list')
print({1, 1.0, True})   # {1}: equal values are the same element
```

## 3. Adding and removing

| Method | Does | Missing element |
|---|---|---|
| `s.add(x)` | add one element (no effect if present) | — |
| `s.update(it)` | add every element of an iterable | — |
| `s.remove(x)` | remove `x` | **`KeyError`** |
| `s.discard(x)` | remove `x` if present | silently nothing |
| `s.pop()` | remove and return an **arbitrary** element | `KeyError` if empty |
| `s.clear()` | remove everything | — |

```python
s = {1, 2}
s.add(2)          # still {1, 2}
s.update([3, 4])  # {1, 2, 3, 4}
s.discard(99)     # fine
# s.remove(99)    → KeyError: 99
```

## 4. Set algebra

<div class="figure">
<svg viewBox="0 0 640 170" width="640" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="13">
  <defs>
    <clipPath id="cA1"><circle cx="70" cy="80" r="45"/></clipPath>
    <clipPath id="cA2"><circle cx="230" cy="80" r="45"/></clipPath>
    <clipPath id="cA3"><circle cx="390" cy="80" r="45"/></clipPath>
    <clipPath id="cA4"><circle cx="550" cy="80" r="45"/></clipPath>
  </defs>
  <circle cx="70" cy="80" r="45" fill="#2f81f7" fill-opacity=".45"/><circle cx="110" cy="80" r="45" fill="#2f81f7" fill-opacity=".45"/>
  <circle cx="270" cy="80" r="45" fill="#3fb950" fill-opacity=".45" clip-path="url(#cA2)"/>
  <circle cx="230" cy="80" r="45" fill="none" stroke="currentColor" stroke-opacity=".5"/><circle cx="270" cy="80" r="45" fill="none" stroke="currentColor" stroke-opacity=".5"/>
  <circle cx="390" cy="80" r="45" fill="#d29922" fill-opacity=".5"/><circle cx="430" cy="80" r="45" fill="var(--panel, #161b22)"/>
  <circle cx="390" cy="80" r="45" fill="none" stroke="currentColor" stroke-opacity=".5"/><circle cx="430" cy="80" r="45" fill="none" stroke="currentColor" stroke-opacity=".5"/>
  <circle cx="550" cy="80" r="45" fill="#a371f7" fill-opacity=".5"/><circle cx="590" cy="80" r="45" fill="#a371f7" fill-opacity=".5"/>
  <circle cx="590" cy="80" r="45" fill="var(--panel, #161b22)" clip-path="url(#cA4)"/>
  <circle cx="550" cy="80" r="45" fill="none" stroke="currentColor" stroke-opacity=".5"/><circle cx="590" cy="80" r="45" fill="none" stroke="currentColor" stroke-opacity=".5"/>
  <g fill="currentColor"><text x="55" y="155">a | b</text><text x="215" y="155">a &amp; b</text><text x="375" y="155">a - b</text><text x="535" y="155">a ^ b</text></g>
</svg>
<figcaption>Union, intersection, difference and symmetric difference (left circle a, right circle b).</figcaption>
</div>

| Operation | Operator | Method | `{1,2,3,4}` ⊕ `{3,4,5}` |
|---|---|---|---|
| union (in either) | `a \| b` | `a.union(b)` | `{1, 2, 3, 4, 5}` |
| intersection (in both) | `a & b` | `a.intersection(b)` | `{3, 4}` |
| difference (in a, not b) | `a - b` | `a.difference(b)` | `{1, 2}` |
| symmetric difference (in exactly one) | `a ^ b` | `a.symmetric_difference(b)` | `{1, 2, 5}` |
| subset | `a <= b` | `a.issubset(b)` | `False` |
| proper subset | `a < b` | — | |
| superset | `a >= b` | `a.issuperset(b)` | |
| no common elements | — | `a.isdisjoint(b)` | `False` |

The operators need **both** sides to be sets. The methods accept any iterable: `a.union([7, 8])` works, but `a | [7, 8]` is a `TypeError`.

In-place versions: `a |= b`, `a &= b`, `a -= b`, `a ^= b` (or `update`, `intersection_update`, …).

## 5. Why sets are fast: the membership test

```python
import timeit
L = list(range(10_000))
S = set(L)
print(timeit.timeit(lambda: 9999 in L, number=1000))   # ~0.03 s  (linear scan)
print(timeit.timeit(lambda: 9999 in S, number=1000))   # ~0.00003 s (hash lookup)
```

About **1000× faster** here. The gap grows with size, because the list test is O(n) and the set test is O(1).

> [!KEY]
> If you test membership inside a loop over another collection, convert the searched collection to a set first. That turns an O(n·m) algorithm into O(n + m):
> ```python
> banned = set(banned_words)            # O(m), once
> clean = [w for w in words if w not in banned]   # O(n) total
> ```

## 6. Common set patterns

```python
# deduplicate (order NOT preserved)
unique = set([3, 1, 3, 2])

# deduplicate PRESERVING first-seen order: use dict keys
unique_ordered = list(dict.fromkeys([3, 1, 3, 2, 1]))    # [3, 1, 2]

# does a list contain duplicates?
has_dup = len(set(nums)) != len(nums)

# seen-before check during a scan
seen = set()
for x in stream:
    if x in seen:
        print("repeat:", x)
        break
    seen.add(x)

# common elements of two lists
common = set(a) & set(b)

# letters used in a word vs an alphabet
missing = set("abcdefghijklmnopqrstuvwxyz") - set(sentence.lower())
```

## 7. `frozenset`: the immutable set

`frozenset` is to `set` what `tuple` is to `list`: immutable, so **hashable**. Use it as a dict key or as an element of another set:

```python
fs = frozenset([1, 2])
groups = {fs: "team A"}                       # a set as a dict key
print(frozenset([2, 1]) in groups)            # True: order doesn't matter
family = {frozenset({"ada", "bob"}), frozenset({"cy"})}   # a set of sets
```

## 8. Complexity

| Operation | Average |
|---|---|
| `x in s`, `add`, `remove`, `discard` | O(1) |
| `len(s)` | O(1) |
| `a \| b` | O(len(a) + len(b)) |
| `a & b` | O(min(len(a), len(b))) |
| `a - b` | O(len(a)) |
| building from n items | O(n) |

## 9. Exam-ready answers

> [!EXAM]
> **Sets.** A set is an unordered, mutable collection of distinct hashable objects, implemented as a hash table, so membership testing, insertion and deletion take constant time on average. Sets are created with braces `{1, 2}` or the `set()` constructor (an empty set must be written `set()`, since `{}` is an empty dictionary). They support mathematical operations such as union (`|`), intersection (`&`), difference (`-`), symmetric difference (`^`) and subset tests (`<=`). Sets do not support indexing because they are unordered. A `frozenset` is an immutable, hashable variant that can be used as a dictionary key or set element.

> [!EXAM]
> **`remove` vs `discard`.** Both delete an element from a set. `remove(x)` raises `KeyError` if `x` is absent, while `discard(x)` does nothing in that case.

## 10. Cheat sheet

| Need | Code |
|---|---|
| empty set | `set()` |
| unique values | `set(xs)` |
| unique, order kept | `list(dict.fromkeys(xs))` |
| fast lookup | `allowed = set(xs)`; `x in allowed` |
| in both | `a & b` |
| in a but not b | `a - b` |
| in exactly one | `a ^ b` |
| has duplicates | `len(set(xs)) < len(xs)` |
| set as dict key | `frozenset(...)` |
| deterministic print | `sorted(s)` |

> [!INTERVIEW]
> **"Find the longest consecutive sequence in an unsorted array in O(n)"** (LeetCode 128). Put every number in a set. A number `x` starts a run only if `x - 1` is **not** in the set. From each start, walk `x + 1, x + 2, …` with O(1) set lookups. Each number is visited at most twice, so the whole thing is O(n). Sorting would cost O(n log n).
