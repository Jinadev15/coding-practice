---
id: py-typed-functions
title: Write Typed Signatures
difficulty: Easy
order: 1
tags: type hints, syntax drill
---
## Statement
Implement these functions **with exactly the type hints shown**. The driver checks your annotations as well as the behaviour, so this drills the syntax.

| Function | Signature | Behaviour |
|---|---|---|
| `word_lengths` | `(words: list[str]) -> dict[str, int]` | map each word to its length |
| `safe_div` | `(a: float, b: float) -> float \| None` | `a / b`, or `None` if `b == 0` |
| `apply_twice` | `(f: Callable[[int], int], x: int) -> int` | `f(f(x))` |
| `min_max` | `(xs: Iterable[int]) -> tuple[int, int]` | the smallest and largest |

Import `Callable` and `Iterable` from `collections.abc`.

## Starter
```python
from collections.abc import Callable, Iterable

def word_lengths(words):
    pass

def safe_div(a, b):
    pass

def apply_twice(f, x):
    pass

def min_max(xs):
    pass
```

## Driver
```python
import annotationlib
from collections.abc import Callable, Iterable
expected = {
    "word_lengths": {"words": list[str], "return": dict[str, int]},
    "safe_div": {"a": float, "b": float, "return": float | None},
    "apply_twice": {"f": Callable[[int], int], "x": int, "return": int},
    "min_max": {"xs": Iterable[int], "return": tuple[int, int]},
}
ok = True
for name, ann in expected.items():
    got = annotationlib.get_annotations(globals()[name])
    if got != ann:
        ok = False
        print(f"{name}: annotations {got} != expected")
if ok:
    print("annotations ok")
print(word_lengths(input().split()))
a, b = map(float, input().split())
print(safe_div(a, b))
print(apply_twice(lambda v: v * 3 + 1, int(input())))
print(min_max(int(x) for x in input().split()))
```

## Tests
=== sample
hi there
6 3
1
5 -2 9
---
annotations ok
{'hi': 2, 'there': 5}
2.0
13
(-2, 9)
=== hidden
solo
1 0
0
7
---
annotations ok
{'solo': 4}
None
4
(7, 7)

## Solution
```python
from collections.abc import Callable, Iterable

def word_lengths(words: list[str]) -> dict[str, int]:
    return {w: len(w) for w in words}

def safe_div(a: float, b: float) -> float | None:
    return None if b == 0 else a / b

def apply_twice(f: Callable[[int], int], x: int) -> int:
    return f(f(x))

def min_max(xs: Iterable[int]) -> tuple[int, int]:
    lo = hi = None
    for x in xs:
        if lo is None or x < lo:
            lo = x
        if hi is None or x > hi:
            hi = x
    return lo, hi
```

`min_max` receives a **generator** from the driver. That's why it's typed `Iterable` and loops once, instead of calling `min(xs)` and then `max(xs)`: the second call would find the generator already exhausted. The type hint and the implementation agree.
